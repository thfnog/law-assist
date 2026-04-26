'use client';

import { useState } from 'react';
import { supabase } from '@/lib/supabase';
import { useRouter } from 'next/navigation';
import { Building2, User, Mail, Lock, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function RegisterOfficePage() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    officeName: '',
    officeSlug: '',
    fullName: '',
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // 1. Create Auth User
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email: formData.email,
        password: formData.password,
        options: {
          data: {
            full_name: formData.fullName,
            role: 'dono',
            office_name: formData.officeName,
            office_slug: formData.officeSlug,
          }
        }
      });

      if (authError) throw authError;

      setStep(3); // Success step
    } catch (error) {
      console.error('Registration error:', error);
      alert('Erro ao registrar escritório. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 font-sans">
      <div className="max-w-2xl w-full bg-white rounded-[2rem] shadow-2xl shadow-slate-200/50 p-8 md:p-12 border border-slate-100 overflow-hidden relative">
        
        {/* Progress Bar */}
        {step < 3 && (
          <div className="flex gap-2 mb-10">
            <div className={`h-1.5 flex-1 rounded-full ${step >= 1 ? 'bg-indigo-600' : 'bg-slate-100'}`} />
            <div className={`h-1.5 flex-1 rounded-full ${step >= 2 ? 'bg-indigo-600' : 'bg-slate-100'}`} />
          </div>
        )}

        {step === 1 && (
          <div className="animate-in fade-in slide-in-from-right-4 duration-500">
            <h2 className="text-3xl font-bold text-slate-900 mb-2">Primeiro, sobre o escritório</h2>
            <p className="text-slate-500 mb-8">Vamos criar o seu workspace jurídico.</p>
            
            <div className="space-y-6">
              <div>
                <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                  <Building2 size={16} /> Nome do Escritório
                </label>
                <input
                  type="text"
                  value={formData.officeName}
                  onChange={(e) => setFormData({...formData, officeName: e.target.value, officeSlug: e.target.value.toLowerCase().replace(/\s+/g, '-')})}
                  className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                  placeholder="Ex: Nogueira & Associados"
                />
              </div>
              <div>
                <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                  Identificador (Slug)
                </label>
                <div className="flex items-center">
                  <span className="bg-slate-100 px-4 py-4 rounded-l-2xl border border-r-0 border-slate-200 text-slate-400 text-sm">law-assist.app/</span>
                  <input
                    type="text"
                    value={formData.officeSlug}
                    onChange={(e) => setFormData({...formData, officeSlug: e.target.value})}
                    className="flex-1 px-5 py-4 bg-slate-50 border border-slate-200 rounded-r-2xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                    placeholder="nogueira-associados"
                  />
                </div>
              </div>
              <button
                onClick={() => setStep(2)}
                disabled={!formData.officeName || !formData.officeSlug}
                className="w-full py-4 bg-indigo-600 text-white font-bold rounded-2xl hover:bg-indigo-700 transition-all shadow-lg flex items-center justify-center gap-2 disabled:opacity-50"
              >
                Próximo Passo <ArrowRight size={20} />
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="animate-in fade-in slide-in-from-right-4 duration-500">
            <h2 className="text-3xl font-bold text-slate-900 mb-2">Agora, seus dados de Admin</h2>
            <p className="text-slate-500 mb-8">Você será o administrador (Dono) deste workspace.</p>
            
            <form onSubmit={handleRegister} className="space-y-6">
              <div>
                <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                  <User size={16} /> Nome Completo
                </label>
                <input
                  type="text"
                  value={formData.fullName}
                  onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                  className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                  placeholder="Seu nome"
                  required
                />
              </div>
              <div>
                <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                  <Mail size={16} /> E-mail Profissional
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                  placeholder="email@escritorio.com"
                  required
                />
              </div>
              <div>
                <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                  <Lock size={16} /> Senha de Acesso
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full px-5 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                  placeholder="Mínimo 8 caracteres"
                  required
                />
              </div>
              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 py-4 bg-slate-100 text-slate-600 font-bold rounded-2xl hover:bg-slate-200 transition-all"
                >
                  Voltar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-[2] py-4 bg-indigo-600 text-white font-bold rounded-2xl hover:bg-indigo-700 transition-all shadow-lg flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? 'Criando...' : 'Finalizar Cadastro'}
                </button>
              </div>
            </form>
          </div>
        )}

        {step === 3 && (
          <div className="text-center py-10 animate-in zoom-in-95 duration-500">
            <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 size={40} />
            </div>
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Bem-vindo ao LawAssist!</h2>
            <p className="text-slate-500 mb-10 max-w-sm mx-auto">
              O escritório <strong>{formData.officeName}</strong> foi criado. Verifique seu e-mail para confirmar a conta e comece a usar.
            </p>
            <button
              onClick={() => router.push('/login')}
              className="px-10 py-4 bg-indigo-600 text-white font-bold rounded-2xl hover:bg-indigo-700 transition-all shadow-lg"
            >
              Ir para Login
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
