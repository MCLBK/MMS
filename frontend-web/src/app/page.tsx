import Link from "next/link";
import {
  ArrowRight,
  MapPin,
  Truck,
  BarChart3,
  Shield,
  Zap,
  Clock,
  Globe,
  CheckCircle2,
  Star,
  Package,
  Users,
  MessageSquare,
  Brain,
} from "lucide-react";

const FEATURES = [
  {
    icon: Brain,
    title: "Attribution IA",
    desc: "Affectation intelligente des livreurs basee sur la proximite, la charge et les performances. Le scoring multicritere optimise chaque attribution.",
    color: "text-purple-500 bg-purple-500/10",
  },
  {
    icon: MapPin,
    title: "Suivi GPS temps reel",
    desc: "Position des livreurs en direct sur carte interactive. Historique complet et estimation d'arrivee automatique.",
    color: "text-success bg-success/10",
  },
  {
    icon: BarChart3,
    title: "Analytics avances",
    desc: "Tableaux de bord detailles, KPI, performances et tendances. Predictions IA pour anticiper les pics d'activite.",
    color: "text-accent bg-accent/10",
  },
  {
    icon: Shield,
    title: "Multi-tenant securise",
    desc: "Chaque entreprise accede exclusivement a ses donnees. Isolation totale, RBAC granulaire et audit complet.",
    color: "text-primary bg-primary/10",
  },
  {
    icon: MessageSquare,
    title: "Assistant IA",
    desc: "Posez vos questions en langage naturel. L'assistant analyse vos donnees et vous guide dans vos decisions.",
    color: "text-teal-500 bg-teal-500/10",
  },
  {
    icon: Zap,
    title: "Notifications push",
    desc: "Alertes en temps reel pour chaque etape de la livraison. Web et mobile, jamais une mise a jour manquee.",
    color: "text-yellow-500 bg-yellow-500/10",
  },
];

const STATS = [
  { value: "99.9%", label: "Disponibilite" },
  { value: "<2s", label: "Mise a jour GPS" },
  { value: "21", label: "Statuts de suivi" },
  { value: "100%", label: "Gratuit" },
];

const STEPS = [
  {
    step: "01",
    title: "Creez votre entreprise",
    desc: "Inscrivez-vous et configurez votre espace en quelques minutes. Import de donnees existantes possible.",
  },
  {
    step: "02",
    title: "Ajoutez vos livreurs",
    desc: "Enregistrez votre flotte, vehicules et zones de couverture. L'app mobile se connecte instantanement.",
  },
  {
    step: "03",
    title: "Creez vos commandes",
    desc: "Saisissez les commandes ou importez-les. L'IA analyse et attribue automatiquement le meilleur livreur.",
  },
  {
    step: "04",
    title: "Suivez en temps reel",
    desc: "Carte GPS en direct, notifications a chaque etape, preuves de livraison et confirmation client.",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white dark:bg-bg-dark">
      {/* Nav */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-bg-dark/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Truck className="w-4 h-4 text-white" />
            </div>
            <span className="font-display font-bold text-lg text-primary dark:text-white">
              MMS<span className="text-accent">Express</span>
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary dark:hover:text-white transition-colors">
              Fonctionnalites
            </a>
            <a href="#how-it-works" className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary dark:hover:text-white transition-colors">
              Comment ca marche
            </a>
            <a href="#stats" className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-primary dark:hover:text-white transition-colors">
              Chiffres
            </a>
          </nav>
          <div className="flex items-center gap-3">
            <Link href="/login" className="btn-outline text-sm">
              Connexion
            </Link>
            <Link href="/register" className="btn-primary text-sm">
              Commencer
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative pt-32 pb-24 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5 dark:from-primary/10 dark:to-accent/10" />
        <div className="absolute top-20 right-0 w-[500px] h-[500px] rounded-full bg-accent/5 blur-3xl dark:bg-accent/10" />
        <div className="max-w-7xl mx-auto relative">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 bg-accent/10 text-accent px-4 py-1.5 rounded-full text-sm font-display font-semibold mb-6">
              <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
              Plateforme intelligente de livraison
            </div>
            <h1 className="font-display font-extrabold text-4xl sm:text-5xl lg:text-6xl text-primary dark:text-white leading-[1.1] tracking-tight mb-6">
              Gerez vos livraisons avec{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-secondary">
                intelligence
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-300 max-w-2xl mb-8 leading-relaxed">
              Attribution optimisee par IA, suivi GPS temps reel, analytics avances.
              MMS Express centralise vos operations de livraison dans une
              plateforme unique, intuitive et puissante.
            </p>
            <div className="flex flex-wrap gap-4 mb-12">
              <Link href="/register" className="btn-primary text-base px-8 py-3">
                Demarrer gratuitement
                <ArrowRight className="w-4 h-4" />
              </Link>
              <a href="#how-it-works" className="btn-outline text-base px-8 py-3">
                Comment ca marche
              </a>
            </div>

            <div className="flex flex-wrap items-center gap-6 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-success" />
                100% gratuit
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-success" />
                Open source
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-success" />
                Aucune carte requise
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats band */}
      <section id="stats" className="bg-primary dark:bg-surface-dark border-y border-primary-light/20 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {STATS.map((s) => (
              <div key={s.label} className="text-center">
                <p className="font-display font-extrabold text-3xl sm:text-4xl text-white mb-1">
                  {s.value}
                </p>
                <p className="text-sm text-gray-300 dark:text-gray-400 font-medium">
                  {s.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-sm font-display font-semibold text-accent uppercase tracking-wider mb-3">
              Fonctionnalites
            </p>
            <h2 className="font-display font-bold text-3xl sm:text-4xl text-primary dark:text-white mb-4">
              Tout ce dont vous avez besoin
            </h2>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto text-lg">
              Une plateforme complete pour gerer, attribuer et suivre vos
              livraisons de bout en bout.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f) => (
              <div
                key={f.title}
                className="card p-6 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 group"
              >
                <div className={`w-12 h-12 rounded-xl ${f.color} flex items-center justify-center mb-4`}>
                  <f.icon className="w-6 h-6" />
                </div>
                <h3 className="font-display font-bold text-lg mb-2 text-gray-900 dark:text-white group-hover:text-primary dark:group-hover:text-accent transition-colors">
                  {f.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-surface-dark/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-sm font-display font-semibold text-accent uppercase tracking-wider mb-3">
              Comment ca marche
            </p>
            <h2 className="font-display font-bold text-3xl sm:text-4xl text-primary dark:text-white mb-4">
              Operationnel en 4 etapes
            </h2>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto text-lg">
              De la creation de votre espace au suivi en temps reel,
              tout est pense pour aller vite.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {STEPS.map((s) => (
              <div key={s.step} className="relative">
                <div className="text-5xl font-display font-black text-accent/10 dark:text-accent/20 mb-3">
                  {s.step}
                </div>
                <h3 className="font-display font-bold text-lg text-gray-900 dark:text-white mb-2">
                  {s.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-br from-primary to-primary-light dark:from-primary dark:to-primary-light rounded-2xl p-12 sm:p-16 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 rounded-full bg-accent/20 blur-3xl" />
            <div className="relative">
              <h2 className="font-display font-bold text-3xl sm:text-4xl text-white mb-4">
                Pret a transformer vos livraisons ?
              </h2>
              <p className="text-gray-300 text-lg max-w-xl mx-auto mb-8">
                Rejoignez MMS Express et decouvrez une nouvelle facon de gerer vos
                operations de livraison. Gratuit, sans engagement.
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <Link
                  href="/register"
                  className="inline-flex items-center gap-2 bg-accent hover:bg-accent/90 text-white font-display font-semibold px-8 py-3 rounded-xl transition-colors"
                >
                  Creer mon compte
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  href="/login"
                  className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white font-display font-semibold px-8 py-3 rounded-xl transition-colors border border-white/20"
                >
                  Se connecter
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-primary dark:bg-surface-dark border-t border-primary-light/20 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Truck className="w-5 h-5 text-accent" />
                <span className="font-display font-bold text-white">
                  MMS<span className="text-accent">Express</span>
                </span>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed">
                Plateforme intelligente de gestion de livraisons.
                Open source, gratuite, sans compromis.
              </p>
            </div>
            <div>
              <h4 className="font-display font-semibold text-white mb-4">Produit</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#features" className="hover:text-accent transition-colors">Fonctionnalites</a></li>
                <li><a href="#how-it-works" className="hover:text-accent transition-colors">Comment ca marche</a></li>
                <li><a href="#stats" className="hover:text-accent transition-colors">Chiffres</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-display font-semibold text-white mb-4">Plateforme</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><span>Application web</span></li>
                <li><span>Application mobile</span></li>
                <li><span>API REST</span></li>
              </ul>
            </div>
            <div>
              <h4 className="font-display font-semibold text-white mb-4">Technologies</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><span>Next.js + React</span></li>
                <li><span>FastAPI + PostgreSQL</span></li>
                <li><span>React Native CLI</span></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-700 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-500">
              &copy; {new Date().getFullYear()} MMS Express. Tous droits reserves.
            </p>
            <div className="flex items-center gap-1">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-4 h-4 text-accent fill-accent" />
              ))}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
