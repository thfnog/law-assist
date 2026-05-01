'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { Layout, MoveRight, ExternalLink, RefreshCw } from 'lucide-react';
import axios from 'axios';

export default function KanbanPage() {
  const [cards, setCards] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchCards = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/trello/kanban');
      setCards(response.data.cards);
    } catch (error) {
      console.error('Error fetching cards:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCards();
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Jornada do Cliente</h1>
            <p className="text-slate-500 mt-1">Gerencie seus processos via Trello integrado.</p>
          </div>
          <button 
            onClick={fetchCards}
            className="p-3 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 text-slate-600 transition-all flex items-center gap-2"
          >
            <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
            Sincronizar Trello
          </button>
        </div>

        {/* Kanban Board Layout */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {/* Column Example: Triagem */}
          <div className="bg-slate-100/50 rounded-[2rem] p-4 flex flex-col min-h-[600px] border border-slate-200/60">
            <div className="flex items-center justify-between mb-6 px-4">
              <h3 className="font-bold text-slate-700 flex items-center gap-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full" /> Triagem
              </h3>
              <span className="bg-white px-2 py-0.5 rounded-full text-xs font-bold text-slate-400 border border-slate-200">
                {cards.length}
              </span>
            </div>

            <div className="space-y-4">
              {cards.map((card) => (
                <div 
                  key={card.id} 
                  className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all group cursor-pointer"
                >
                  <div className="flex justify-between items-start mb-3">
                    <h4 className="font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">
                      {card.name}
                    </h4>
                    <a href={card.shortUrl} target="_blank" className="text-slate-300 hover:text-slate-500">
                      <ExternalLink size={14} />
                    </a>
                  </div>
                  <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                    {card.desc || 'Sem descrição definida no Trello.'}
                  </p>
                  
                  <div className="mt-4 pt-4 border-t border-slate-50 flex justify-between items-center">
                    <div className="flex -space-x-2">
                      <div className="w-6 h-6 bg-slate-200 rounded-full border-2 border-white" />
                    </div>
                    <button className="text-[10px] font-bold text-indigo-600 uppercase tracking-wider flex items-center gap-1 hover:gap-2 transition-all">
                      Mover <MoveRight size={12} />
                    </button>
                  </div>
                </div>
              ))}

              {cards.length === 0 && !loading && (
                <div className="py-20 text-center">
                  <Layout size={40} className="mx-auto text-slate-200 mb-4" />
                  <p className="text-sm text-slate-400">Nenhum card nesta lista.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
