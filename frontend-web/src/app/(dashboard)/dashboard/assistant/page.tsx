"use client";

import { useState, useRef, useEffect } from "react";
import { useAIChat, type ChatResponse } from "@/hooks/use-ai";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Bot, Send, User, Sparkles, Loader2 } from "lucide-react";

const DEMO_COMPANY_ID = "00000000-0000-0000-0000-000000000001";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  source?: string;
  suggestions?: string[];
}

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Bonjour ! Je suis l'assistant MMS Express. Je peux vous aider avec le suivi des commandes, l'optimisation des livraisons, et l'analyse de la performance. Comment puis-je vous aider ?",
      timestamp: new Date(),
      suggestions: [
        "Combien de commandes aujourd'hui ?",
        "Comment optimiser les livraisons ?",
        "Y a-t-il des problèmes en cours ?",
      ],
    },
  ]);
  const [input, setInput] = useState("");
  const chatMutation = useAIChat(DEMO_COMPANY_ID);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;
    const userMsg: Message = { role: "user", content: text.trim(), timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    const history = messages.map((m) => ({ role: m.role, content: m.content }));

    try {
      const resp = await chatMutation.mutateAsync({
        message: text.trim(),
        conversation_history: history,
      });
      const assistantMsg: Message = {
        role: "assistant",
        content: resp.message,
        timestamp: new Date(),
        source: resp.source,
        suggestions: resp.suggestions,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Désolé, une erreur est survenue. Veuillez réessayer.",
          timestamp: new Date(),
        },
      ]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-display font-bold text-2xl text-gray-900 dark:text-white">
              Assistant IA
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Powered by Ollama — aide opérateur en temps réel
            </p>
          </div>
        </div>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex-shrink-0 flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
              )}
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                  msg.role === "user"
                    ? "bg-primary text-white rounded-br-md"
                    : "bg-gray-100 dark:bg-surface-dark-alt text-gray-900 dark:text-gray-100 rounded-bl-md"
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                {msg.source && (
                  <p className="text-[10px] mt-2 opacity-60">
                    via {msg.source}
                  </p>
                )}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {msg.suggestions.map((s, j) => (
                      <button
                        key={j}
                        onClick={() => sendMessage(s)}
                        className="text-xs px-3 py-1.5 rounded-full border border-gray-200 dark:border-gray-600 hover:bg-white dark:hover:bg-surface-dark text-gray-700 dark:text-gray-300 transition-colors"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-lg bg-secondary/20 flex-shrink-0 flex items-center justify-center">
                  <User className="w-4 h-4 text-secondary" />
                </div>
              )}
            </div>
          ))}
          {chatMutation.isPending && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex-shrink-0 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div className="bg-gray-100 dark:bg-surface-dark-alt rounded-2xl rounded-bl-md px-4 py-3">
                <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-gray-100 dark:border-gray-800 p-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Posez votre question..."
              className="flex-1 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-surface-dark px-4 py-3 text-sm text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              disabled={chatMutation.isPending}
            />
            <Button
              type="submit"
              disabled={!input.trim() || chatMutation.isPending}
              className="rounded-xl px-4"
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}
