'use client';

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { useRouter, usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  MessageSquare, 
  Users, 
  Briefcase, 
  Wallet, 
  Share2,
  Settings, 
  LogOut, 
  Menu,
  X,
  ChevronRight,
  Bell
} from 'lucide-react';
import Link from 'next/link';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [user, setUser] = useState<any>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const checkUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push('/login');
      } else {
        setUser(user);
      }
    };
    checkUser();
  }, [router]);

  const menuItems = [
    { name: 'Geral', icon: LayoutDashboard, path: '/dashboard', roles: ['dono', 'advogado', 'financeiro', 'atendente'] },
    { name: 'Chat IA', icon: MessageSquare, path: '/dashboard/chat', roles: ['dono', 'advogado', 'atendente'] },
    { name: 'Clientes', icon: Users, path: '/dashboard/clients', roles: ['dono', 'advogado', 'atendente'] },
    { name: 'Processos', icon: Briefcase, path: '/dashboard/cases', roles: ['dono', 'advogado'] },
    { name: 'Financeiro', icon: Wallet, path: '/dashboard/finance', roles: ['dono', 'financeiro'] },
    { name: 'Integrações', icon: Share2, path: '/dashboard/integrations', roles: ['dono'] },
    { name: 'Configurações', icon: Settings, path: '/dashboard/settings', roles: ['dono'] },
  ];

  const filteredMenu = menuItems.filter(item => 
    !user || item.roles.includes(user.user_metadata?.role || 'advogado')
  );

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push('/login');
  };

  if (!user) return <div className="h-screen flex items-center justify-center bg-slate-50">Carregando workspace...</div>;

  return (
    <div className="flex h-screen bg-slate-50 font-sans">
      {/* Sidebar */}
      <aside 
        className={`${sidebarOpen ? 'w-72' : 'w-20'} bg-white border-r border-slate-200 transition-all duration-300 flex flex-col z-20`}
      >
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-xl shrink-0">L</div>
          {sidebarOpen && <h1 className="font-bold text-slate-800 text-lg">LawAssist</h1>}
        </div>

        <nav className="flex-grow px-4 space-y-2 mt-4">
          {filteredMenu.map((item) => (
            <Link 
              key={item.path} 
              href={item.path}
              className={`flex items-center gap-3 px-4 py-3.5 rounded-2xl transition-all group ${
                pathname === item.path 
                ? 'bg-indigo-50 text-indigo-600' 
                : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <item.icon size={22} className={pathname === item.path ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600'} />
              {sidebarOpen && <span className="font-medium">{item.name}</span>}
              {sidebarOpen && pathname === item.path && <ChevronRight size={16} className="ml-auto" />}
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-100">
          <button 
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-3.5 w-full text-slate-500 hover:bg-red-50 hover:text-red-600 rounded-2xl transition-all group"
          >
            <LogOut size={22} />
            {sidebarOpen && <span className="font-medium">Sair</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-grow flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-8 shrink-0">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-slate-50 rounded-xl text-slate-500 transition-colors"
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <div className="h-6 w-px bg-slate-200" />
            <h2 className="font-semibold text-slate-800">
              {filteredMenu.find(m => m.path === pathname)?.name || 'Bem-vindo'}
            </h2>
          </div>

          <div className="flex items-center gap-6">
            <button className="relative p-2 text-slate-400 hover:text-slate-600 transition-colors">
              <Bell size={24} />
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-red-500 border-2 border-white rounded-full" />
            </button>
            <div className="flex items-center gap-3 pl-6 border-l border-slate-100">
              <div className="text-right hidden md:block">
                <p className="text-sm font-bold text-slate-900">{user.user_metadata?.full_name}</p>
                <p className="text-xs font-medium text-slate-400 capitalize">{user.user_metadata?.role}</p>
              </div>
              <div className="w-10 h-10 bg-slate-200 rounded-full flex items-center justify-center text-slate-500 font-bold border-2 border-white shadow-sm">
                {user.user_metadata?.full_name?.charAt(0) || 'U'}
              </div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-grow overflow-y-auto p-8">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
