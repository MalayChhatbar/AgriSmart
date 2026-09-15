import React, { useState, useRef, useEffect } from 'react';
import {
  X,
  Send,
  Sparkles,
  Bot,
  User,
  HelpCircle,
  Volume2,
  Globe,
  RefreshCw,
} from 'lucide-react';
import { ChatMessage } from '../types';
import { askKisanAI } from '../services/api';

interface KisanChatDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  currentCrop?: string;
  detectedDisease?: string;
  language: 'en' | 'hi' | 'gu' | 'mr' | 'pa';
  backendUrl: string;
  initialPrompt?: string;
}

export const KisanChatDrawer: React.FC<KisanChatDrawerProps> = ({
  isOpen,
  onClose,
  currentCrop = 'Tomato',
  detectedDisease = 'Early Blight',
  language,
  backendUrl,
  initialPrompt,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'assistant',
      text: `Namaste! I am your AgriSmart AI Farm Assistant. Ask me any questions regarding treatment for ${currentCrop}, pesticide dosage, or weather adjustments.`,
      textHi: `नमस्ते! मैं आपका एग्रीस्मार्ट AI किसान सलाहकार हूँ। ${currentCrop} के उपचार, जैविक खाद या मौसम संबंधी कोई भी सवाल पूछें।`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickPrompts = [
    `How to prepare organic neem spray for ${currentCrop}?`,
    `Will rainfall wash away my chemical fungicide spray?`,
    `What fertilizer should I reduce during ${detectedDisease}?`,
    `Can this disease spread to neighboring crops?`,
  ];

  useEffect(() => {
    if (initialPrompt && isOpen) {
      handleSend(initialPrompt);
    }
  }, [initialPrompt, isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  if (!isOpen) return null;

  const handleSend = async (textToSend?: string) => {
    const queryText = (textToSend || input).trim();
    if (!queryText || isTyping) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const reply = await askKisanAI(queryText, currentCrop, detectedDisease, language, backendUrl);
      setMessages((prev) => [...prev, reply]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'assistant',
          text: 'Unable to reach advisory engine. Please check your network connection.',
          textHi: 'सर्वर से संपर्क नहीं हो पा रहा है। कृपया इंटरनेट जांचें।',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex flex-col justify-end bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-card w-full max-w-md mx-auto rounded-t-3xl border-t border-x border-border shadow-2xl flex flex-col h-[85vh] overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-border flex items-center justify-between bg-card">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-primary/20 flex items-center justify-center text-primary">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h3 className="font-bold text-sm text-foreground">Kisan AI Agricultural Chat</h3>
                <span className="text-[10px] bg-primary/20 text-primary font-extrabold px-1.5 py-0.2 rounded-full">
                  Bilingual
                </span>
              </div>
              <p className="text-xs text-muted-foreground">
                Grounded context: {currentCrop} • {detectedDisease}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Chat Message List */}
        <div className="flex-1 p-4 overflow-y-auto space-y-3">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-2.5 ${
                msg.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.sender === 'assistant' && (
                <div className="w-7 h-7 rounded-lg bg-primary/15 text-primary flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-[82%] rounded-2xl p-3 text-xs leading-relaxed shadow-xs ${
                  msg.sender === 'user'
                    ? 'bg-primary text-primary-foreground font-medium rounded-tr-none'
                    : 'bg-secondary text-foreground rounded-tl-none border border-border'
                }`}
              >
                <p>{language === 'hi' && msg.textHi ? msg.textHi : msg.text}</p>
                <span
                  className={`block text-[10px] mt-1 text-right ${
                    msg.sender === 'user' ? 'text-primary-foreground/75' : 'text-muted-foreground'
                  }`}
                >
                  {msg.timestamp}
                </span>
              </div>

              {msg.sender === 'user' && (
                <div className="w-7 h-7 rounded-lg bg-secondary text-foreground flex items-center justify-center shrink-0 mt-0.5 border border-border">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {isTyping && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <div className="w-7 h-7 rounded-lg bg-primary/15 text-primary flex items-center justify-center">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              </div>
              <span className="italic">Kisan AI is analyzing crop agronomy...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggested Questions */}
        <div className="px-4 py-2 border-t border-border/60 bg-secondary/30">
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
            {quickPrompts.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q)}
                className="whitespace-nowrap px-2.5 py-1 rounded-full bg-card border border-border hover:border-primary/50 text-[11px] font-medium text-foreground transition-all cursor-pointer shadow-2xs"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <div className="p-3 pb-6 border-t border-border bg-card flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={
              language === 'hi'
                ? 'रोग, उपचार या खाद के बारे में पूछें...'
                : 'Ask doubts about disease, neem dosage, weather...'
            }
            className="flex-1 bg-input/70 border border-border text-foreground text-xs rounded-xl px-3.5 py-2.5 focus:ring-1 focus:ring-primary focus:outline-none"
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isTyping}
            className="p-2.5 rounded-xl bg-primary text-primary-foreground hover:brightness-105 active:scale-95 disabled:opacity-50 transition-all cursor-pointer shadow-xs"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
