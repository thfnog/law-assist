'use client';

import DashboardLayout from '@/components/DashboardLayout';
import { 
  Users, 
  Briefcase, 
  Clock, 
  TrendingUp,
  FileText,
  Calendar
} from 'lucide-react';

export default function DashboardPage() {
  const stats = [
    { name: 'Clientes Ativos', value: '124', icon: Users, color: 'text-blue-600', bg: 'bg-blue-50' },
    { name: 'Processos em Curso', value: '42', icon: Briefcase, color: 'text-indigo-600', bg: 'bg-indigo-50' },
    { name: 'Prazos Próximos', value: '8', icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
    { name: 'Taxa de Sucesso', value: '94%', icon: TrendingUp, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Visão Geral</h1>
          <p className="text-slate-500 mt-1">Acompanhe a saúde do seu escritório em tempo real.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => (
            <div key={stat.name} className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm shadow-slate-200/40">
              <div className={`w-12 h-12 ${stat.bg} ${stat.color} rounded-2xl flex items-center justify-center mb-4`}>
                <stat.icon size={24} />
              </div>
              <p className="text-sm font-medium text-slate-400">{stat.name}</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{stat.value}</h3>
            </div>
          ))}
        </div>

        {/* Activity & Calendar */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-white rounded-[2rem] border border-slate-100 p-8 shadow-sm">
            <div className="flex items-center justify-between mb-8">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <FileText size={20} className="text-indigo-600" /> Atividades Recentes
              </h3>
              <button className="text-sm font-semibold text-indigo-600 hover:underline">Ver tudo</button>
            </div>
            <div className="space-y-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-4 p-4 rounded-2xl hover:bg-slate-50 transition-colors cursor-pointer group">
                  <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center text-slate-500 group-hover:bg-white group-hover:shadow-sm transition-all">
                    <FileText size={20} />
                  </div>
                  <div className="flex-grow">
                    <p className="font-bold text-slate-800 text-sm">Contrato gerado - João Silva</p>
                    <p className="text-xs text-slate-400">Há 2 horas • Por Dra. Beatriz</p>
                  </div>
                  <button className="p-2 text-slate-300 hover:text-indigo-600">
                    <Calendar size={18} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-indigo-600 rounded-[2rem] p-8 text-white relative overflow-hidden shadow-xl shadow-indigo-200">
            <div className="relative z-10">
              <h3 className="text-xl font-bold mb-4">Chat Inteligente</h3>
              <p className="text-indigo-100 text-sm mb-8 leading-relaxed">
                Use o poder da IA para analisar processos, gerar contratos e responder clientes instantaneamente.
              </p>
              <a 
                href="/dashboard/chat" 
                className="inline-block px-8 py-3 bg-white text-indigo-600 font-bold rounded-2xl hover:bg-indigo-50 transition-all text-sm"
              >
                Abrir Chat
              </a>
            </div>
            <MessageSquare size={140} className="absolute -bottom-10 -right-10 text-indigo-500/30 rotate-12" />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
