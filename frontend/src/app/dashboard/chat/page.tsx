'use client';

import { useState, useRef, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { Send, Bot, User, Paperclip, Sparkles, Command } from 'lucide-react';
import axios from 'axios';

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: 'bot', content: 'Olá! Sou seu assistente jurídico inteligente. Como posso ajudar no workspace do seu escritório hoje?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      // In production, this URL will be relative or from env
      const response = await axios.post('/api/chat', { message: userMsg });
      setMessages(prev => [...prev, { role: 'bot', content: response.data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', content: 'Desculpe, tive um problema para processar sua solicitação. Verifique se o servidor backend está ativo.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="h-[calc(100vh-12rem)] flex flex-col bg-white rounded-[2rem] border border-slate-100 shadow-sm overflow-hidden">
        {/* Chat Header */}
        <div className="px-8 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white">
              <Sparkles size={20} />
            </div>
            <div>
              <h3 className="font-bold text-slate-800 text-sm">Assistente LawAssist</h3>
              <p className="text-[10px] text-emerald-600 font-bold uppercase tracking-wider flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" /> IA Online
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 flex items-center gap-1 bg-white px-3 py-1.5 rounded-full border border-slate-100">
              <Command size={12} /> + K para atalhos
            </span>
          </div>
        </div>

        {/* Messages Area */}
        <div ref={scrollRef} className="flex-grow overflow-y-auto p-8 space-y-8 scroll-smooth">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
              <div className={`flex gap-4 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-10 h-10 shrink-0 rounded-2xl flex items-center justify-center ${
                  msg.role === 'bot' ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-900 text-white'
                }`}>
                  {msg.role === 'bot' ? <Bot size={20} /> : <User size={20} />}
                </div>
                <div className={`p-5 rounded-[2rem] text-sm leading-relaxed ${
                  msg.role === 'bot' 
                  ? 'bg-slate-50 text-slate-700 rounded-tl-none border border-slate-100 shadow-sm' 
                  : 'bg-indigo-600 text-white rounded-tr-none shadow-md shadow-indigo-100'
                }`}>
                  {msg.content}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start animate-pulse">
              <div className="flex gap-4">
                <div className="w-10 h-10 bg-indigo-100 rounded-2xl flex items-center justify-center text-indigo-600">
                  <Bot size={20} />
                </div>
                <div className="bg-slate-50 p-5 rounded-[2rem] rounded-tl-none border border-slate-100 flex gap-1">
                  <span className="w-1.5 h-1.5 bg-slate-300 rounded-full" />
                  <span className="w-1.5 h-1.5 bg-slate-300 rounded-full" />
                  <span className="w-1.5 h-1.5 bg-slate-300 rounded-full" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-6 bg-slate-50/50 border-t border-slate-100">
          <div className="max-w-4xl mx-auto relative group">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Pergunte sobre um processo, crie um contrato ou registre um lead..."
              className="w-full pl-6 pr-32 py-5 bg-white border border-slate-200 rounded-[2.5rem] focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 transition-all outline-none shadow-sm text-slate-700"
            />
            <div className="absolute right-3 top-2.5 flex gap-2">
              <button className="p-3 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-all">
                <Paperclip size={20} />
              </button>
              <button 
                onClick={handleSend}
                disabled={loading}
                className="p-3 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 disabled:opacity-50"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
          <p className="text-[10px] text-center text-slate-400 mt-4 uppercase tracking-widest font-bold">
            LawAssist Intelligence — Consultoria Jurídica de Precisão
          </p>
        </div>
      </div>
    </DashboardLayout>
  );
}
