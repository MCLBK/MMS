"""Assistant IA conversationnel pour aide aux opérateurs.

Utilise Ollama (gratuit, local) comme backend LLM.
Fallback : réponses basées sur des templates si Ollama n'est pas disponible.
"""

import uuid
from dataclasses import dataclass

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.delivery.models import DeliveryOrder

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"

SYSTEM_PROMPT = """Tu es MMS Assistant, l'assistant IA de la plateforme MMS Express.
Tu aides les opérateurs de livraison avec :
- L'état des commandes et statistiques
- Des conseils d'optimisation des tournées
- L'analyse de la performance des livreurs
- La résolution de problèmes opérationnels

Réponds de manière concise et professionnelle en français.
Utilise les données fournies dans le contexte pour répondre précisément.
Si tu ne connais pas la réponse, dis-le honnêtement.
"""


@dataclass
class AssistantMessage:
    role: str
    content: str
    timestamp: str
    context_used: dict | None = None


@dataclass
class AssistantResponse:
    message: str
    context: dict
    source: str
    suggestions: list[str]


class AIAssistant:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def chat(
        self,
        company_id: uuid.UUID,
        user_message: str,
        conversation_history: list[dict] | None = None,
    ) -> AssistantResponse:
        context = await self._gather_context(company_id, user_message)

        ollama_available = await self._check_ollama()
        if ollama_available:
            response = await self._query_ollama(user_message, context, conversation_history or [])
            source = f"ollama/{OLLAMA_MODEL}"
        else:
            response = self._template_response(user_message, context)
            source = "template-engine"

        suggestions = self._generate_suggestions(user_message, context)

        return AssistantResponse(
            message=response,
            context=context,
            source=source,
            suggestions=suggestions,
        )

    async def _gather_context(self, company_id: uuid.UUID, question: str) -> dict:
        context: dict = {}

        status_counts = await self._get_status_summary(company_id)
        context["order_summary"] = status_counts

        keywords = question.lower()
        if any(w in keywords for w in ["commande", "livraison", "colis", "statut"]):
            context["focus"] = "orders"
        elif any(w in keywords for w in ["livreur", "coursier", "courier", "performance"]):
            context["focus"] = "couriers"
        elif any(w in keywords for w in ["zone", "quartier", "secteur", "carte"]):
            context["focus"] = "zones"
        elif any(w in keywords for w in ["stat", "chiffre", "kpi", "performance", "objectif"]):
            context["focus"] = "analytics"
        else:
            context["focus"] = "general"

        return context

    async def _get_status_summary(self, company_id: uuid.UUID) -> dict:
        stmt = (
            select(
                DeliveryOrder.status,
                func.count().label("cnt"),
            )
            .where(DeliveryOrder.company_id == company_id)
            .group_by(DeliveryOrder.status)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return {
            str(r.status.value) if hasattr(r.status, "value") else str(r.status): r.cnt
            for r in rows
        }

    async def _check_ollama(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{OLLAMA_URL}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def _query_ollama(
        self,
        user_message: str,
        context: dict,
        history: list[dict],
    ) -> str:
        context_str = self._format_context(context)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context_str:
            messages.append(
                {
                    "role": "system",
                    "content": f"Contexte actuel de l'entreprise :\n{context_str}",
                }
            )

        for msg in history[-10:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        messages.append({"role": "user", "content": user_message})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{OLLAMA_URL}/api/chat",
                    json={
                        "model": OLLAMA_MODEL,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": 0.7, "num_predict": 500},
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    fallback = "Désolé, je n'ai pas pu générer une réponse."
                    return data.get("message", {}).get("content", fallback)
        except Exception:
            pass

        return self._template_response(user_message, context)

    def _template_response(self, question: str, context: dict) -> str:
        q = question.lower()
        summary = context.get("order_summary", {})
        total = sum(summary.values())

        if any(w in q for w in ["combien", "nombre", "total", "stat"]):
            if total == 0:
                return "Aucune commande enregistrée pour le moment."
            lines = [f"Voici le résumé des {total} commandes :"]
            status_labels = {
                "pending": "En attente",
                "assigned": "Assignées",
                "in_transit": "En transit",
                "delivered": "Livrées",
                "completed": "Terminées",
                "cancelled": "Annulées",
                "delivery_failed": "Échouées",
            }
            for status, count in sorted(summary.items(), key=lambda x: x[1], reverse=True):
                label = status_labels.get(status, status.replace("_", " ").title())
                lines.append(f"  • {label} : {count}")
            return "\n".join(lines)

        if any(w in q for w in ["problème", "erreur", "échec", "failed", "bloqué"]):
            failed = summary.get("delivery_failed", 0)
            if failed > 0:
                return (
                    f"Il y a actuellement {failed} livraison(s) en échec. "
                    "Je recommande de vérifier les adresses de livraison "
                    "et de contacter les clients concernés. "
                    "Vous pouvez aussi réassigner ces commandes."
                )
            return "Aucun problème détecté. Toutes les livraisons se déroulent normalement."

        if any(w in q for w in ["optimiser", "améliorer", "conseil", "astuce"]):
            tips = [
                "Voici quelques conseils d'optimisation :",
                "1. Regroupez les livraisons par zone géographique",
                "2. Assignez les commandes urgentes aux livreurs les plus proches",
                "3. Utilisez le scoring IA pour les attributions automatiques",
                "4. Surveillez le taux de ponctualité de vos livreurs",
                "5. Planifiez les livraisons en dehors des heures de pointe (7h-9h, 17h-19h)",
            ]
            return "\n".join(tips)

        if any(w in q for w in ["bonjour", "salut", "hello", "hey"]):
            return (
                f"Bonjour ! Je suis l'assistant MMS Express. "
                f"Vous avez actuellement {total} commande(s) en cours. "
                "Comment puis-je vous aider ?"
            )

        return (
            "Je peux vous aider avec :\n"
            "• Le suivi et les statistiques de vos commandes\n"
            "• L'optimisation de vos tournées de livraison\n"
            "• L'analyse de la performance de vos livreurs\n"
            "• La résolution de problèmes opérationnels\n\n"
            "Posez-moi une question spécifique pour que je puisse vous assister."
        )

    def _format_context(self, context: dict) -> str:
        parts = []
        summary = context.get("order_summary", {})
        if summary:
            total = sum(summary.values())
            parts.append(f"Total commandes: {total}")
            for status, count in summary.items():
                parts.append(f"  - {status}: {count}")
        return "\n".join(parts)

    def _generate_suggestions(self, question: str, context: dict) -> list[str]:
        summary = context.get("order_summary", {})
        suggestions = []

        if summary.get("delivery_failed", 0) > 0:
            suggestions.append("Voir les livraisons échouées")
        if summary.get("pending", 0) > 3:
            suggestions.append("Lancer l'attribution automatique")
        if sum(summary.values()) > 0:
            suggestions.append("Afficher les statistiques du jour")

        if not suggestions:
            suggestions = [
                "Combien de commandes aujourd'hui ?",
                "Comment optimiser les livraisons ?",
                "Y a-t-il des problèmes en cours ?",
            ]

        return suggestions[:3]
