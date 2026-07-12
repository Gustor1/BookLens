"use client";

import React, { useState, useRef, useEffect } from "react";
import { useI18n } from "@/components/layout/I18nProvider";
import { ChatMessage } from "@/types";
import { api, isDemoMode } from "@/lib/api/client";
import { Button } from "@/components/ui";
import { Send, User, Bot, AlertTriangle, Sparkles, FileText, Globe } from "lucide-react";
import PageTransition from "@/components/ui/PageTransition";

export default function AssistantPage() {
  const { locale, t } = useI18n();
  const [activeMode, setActiveMode] = useState<"discover" | "academic" | "docs">("discover");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [demoActive, setDemoActive] = useState(false);
  
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setDemoActive(isDemoMode());
    // Initial welcome message
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content: "Bonjour ! Je suis l'assistant IA de MediaLens. Posez-moi des questions sur les liaisons culturelles entre livres, films et jeux vidéo, ou explorez des textes critiques et essais académiques.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  }, [locale]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || loading) return;
    
    const userMsg: ChatMessage = {
      id: String(Date.now()),
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInputValue("");
    setLoading(true);

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      
      const res = await api.chatWithAssistant(
        text,
        history,
        locale,
        "nvidia"
      );

      const botMsg: ChatMessage = {
        id: String(Date.now() + 1),
        role: "assistant",
        content: res.response,
        type: res.type as "text" | "image",
        image_bytes_b64: res.image_bytes_b64,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        {
          id: String(Date.now() + 1),
          role: "assistant",
          content: "⚠️ Une erreur est survenue lors de la communication avec l'assistant.",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    t("assistant.suggest_1"),
    t("assistant.suggest_2"),
    t("assistant.suggest_3")
  ];

  return (
    <PageTransition>
      <div className="flex flex-col h-[calc(100vh-140px)] md:h-[calc(100vh-180px)] max-w-4xl mx-auto border border-slate-900 bg-card/20 rounded-2xl overflow-hidden shadow-2xl">
        
        {/* Modes Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between p-4 border-b border-slate-900 bg-slate-950/40 gap-3">
          <div className="flex gap-1 bg-slate-900/60 p-1 rounded-lg border border-slate-800 self-start">
            {[
              { id: "discover", label: t("assistant.mode_discover"), icon: Sparkles },
              { id: "academic", label: t("assistant.mode_academic"), icon: Globe },
              { id: "docs", label: t("assistant.mode_docs"), icon: FileText }
            ].map(mode => {
              const Icon = mode.icon;
              return (
                <button
                  key={mode.id}
                  onClick={() => setActiveMode(mode.id as any)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                    activeMode === mode.id
                      ? "bg-teal-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{mode.label}</span>
                </button>
              );
            })}
          </div>

          {demoActive && (
            <div className="inline-flex items-center gap-1.5 bg-amber-500/10 border border-amber-500/20 text-amber-500 rounded-lg px-2.5 py-1 text-[11px] font-medium font-sans">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              <span>{t("assistant.api_offline")}</span>
            </div>
          )}
        </div>

        {/* Message area */}
        <div className="flex-grow overflow-y-auto p-4 md:p-6 flex flex-col gap-4 no-scrollbar">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-[85%] ${
                msg.role === "user" ? "self-end flex-row-reverse" : "self-start"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border ${
                  msg.role === "user"
                    ? "bg-slate-900 border-slate-800 text-slate-300"
                    : "bg-teal-500/10 border-teal-500/20 text-teal-400"
                }`}
              >
                {msg.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`rounded-2xl p-4 text-sm font-sans leading-relaxed ${
                  msg.role === "user"
                    ? "bg-teal-600 text-white rounded-tr-none"
                    : "bg-slate-900/60 border border-slate-800/80 text-slate-200 rounded-tl-none"
                }`}
              >
                <div className="prose prose-invert max-w-none text-xs md:text-sm whitespace-pre-wrap">
                  {msg.content}
                </div>
                <span className="block text-[9px] opacity-50 mt-2 text-right">
                  {msg.timestamp}
                </span>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 max-w-[85%] self-start">
              <div className="w-8 h-8 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl rounded-tl-none p-4 text-sm text-slate-400 flex items-center gap-2">
                <span className="animate-bounce">●</span>
                <span className="animate-bounce delay-100">●</span>
                <span className="animate-bounce delay-200">●</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Suggestion list */}
        {messages.length <= 1 && !loading && (
          <div className="px-4 pb-3 flex flex-col gap-2">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-1">
              Suggestions de questions
            </span>
            <div className="flex flex-col gap-1.5">
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(s)}
                  className="text-left text-xs bg-slate-900/40 hover:bg-slate-900 border border-slate-800/60 hover:border-slate-700/80 text-slate-300 rounded-xl px-3.5 py-2 transition-all active:scale-98 line-clamp-1 cursor-pointer font-sans"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input box */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage(inputValue);
          }}
          className="p-4 border-t border-slate-900 bg-slate-950/40 flex items-center gap-3"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={loading}
            placeholder={t("assistant.placeholder")}
            className="flex-grow bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500 transition-all font-sans"
          />
          <Button
            type="submit"
            variant="primary"
            className="px-4 py-2.5 h-10 w-10 !p-0 rounded-xl cursor-pointer"
            disabled={!inputValue.trim() || loading}
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>

      </div>
    </PageTransition>
  );
}
