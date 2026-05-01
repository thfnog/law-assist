'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { Share2, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react';
import axios from 'axios';
import { supabase } from '@/lib/supabase';

export default function IntegrationsPage() {
  const [loading, setLoading] = useState(false);
  const [officeId, setOfficeId] = useState<string | null>(null);

  useEffect(() => {
    const fetchOffice = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        const { data: userData } = await supabase
          .from('user')
          .select('escritorio_id')
          .eq('id', user.id)
          .single();
        if (userData) setOfficeId(userData.escritorio_id);
      }
    };
    fetchOffice();
  }, []);

  const handleConnectGoogle = async () => {
    if (!officeId) return;
    setLoading(true);
    try {
      const response = await axios.get(`/api/auth/google/login?escritorio_id=${officeId}`);
      window.location.href = response.data.url;
    } catch (error) {
      console.error('Error connecting to Google:', error);
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Integrações</h1>
          <p className="text-slate-500 mt-1">Conecte suas ferramentas favoritas para automatizar seu escritório.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Google Integration Card */}
          <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_Logos_by_Google.png" alt="Google" className="w-8 h-8 object-contain" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-800">Google Workspace</h3>
                <p className="text-sm text-slate-500 leading-relaxed mt-2">
                  Gerencie documentos no Drive, gere contratos no Docs e organize dados em Sheets automaticamente.
                </p>
              </div>
            </div>
            
            <div className="mt-8 pt-8 border-t border-slate-50 flex items-center justify-between">
              <button 
                onClick={handleConnectGoogle}
                disabled={loading || !officeId}
                className="px-6 py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-all flex items-center gap-2 disabled:opacity-50"
              >
                {loading ? 'Conectando...' : 'Conectar Google'}
                <ExternalLink size={16} />
              </button>
            </div>
          </div>

          {/* Trello Integration Card */}
          <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center">
                <img src="https://upload.wikimedia.org/wikipedia/commons/7/7a/Trello-logo.png" alt="Trello" className="w-8 h-8 object-contain" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-800">Trello</h3>
                <p className="text-sm text-slate-500 leading-relaxed mt-2">
                  Sincronize a jornada dos seus clientes com quadros e listas no Trello.
                </p>
              </div>
            </div>
            
            <div className="mt-8 pt-8 border-t border-slate-50 flex items-center justify-between">
              <button 
                className="px-6 py-3 bg-white border border-slate-200 text-slate-600 rounded-xl font-bold hover:bg-slate-50 transition-all flex items-center gap-2"
              >
                Configurar Trello
              </button>
              <span className="text-xs text-emerald-600 font-bold flex items-center gap-1">
                <CheckCircle size={12} /> Ativo
              </span>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
