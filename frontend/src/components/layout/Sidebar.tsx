import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Building2,
  FileText,
  Search,
  Shield,
  MessageSquare,
  Settings,
  LogOut,
  ClipboardList,
  Bell,
  Cpu,
  TrendingUp,
  BarChart3,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/stores/authStore';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
}

const navigation: NavItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Agents', href: '/agents', icon: Cpu },
  { name: 'Risk', href: '/risk', icon: TrendingUp },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Vendors', href: '/vendors', icon: Building2 },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Analysis', href: '/analysis', icon: Shield },
  { name: 'Remediation', href: '/remediation', icon: ClipboardList },
  { name: 'Monitoring', href: '/monitoring', icon: Bell },
  { name: 'Query', href: '/query', icon: MessageSquare },
  { name: 'Search', href: '/search', icon: Search },
];

export function Sidebar() {
  const location = useLocation();
  const { user, logout } = useAuthStore();

  return (
    <div className="flex h-full w-72 flex-col glass-panel border-r border-white/10 relative overflow-hidden transition-all duration-300">
      {/* Glow Effect Background */}
      <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-primary/5 via-transparent to-transparent pointer-events-none" />

      {/* Logo */}
      <div className="flex h-20 items-center gap-3 px-6 border-b border-white/10 backdrop-blur-sm z-10 select-none">
        <div className="relative flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 shadow-[0_0_15px_rgba(0,242,255,0.3)] group-hover:shadow-[0_0_25px_rgba(0,242,255,0.5)] transition-all">
          <Shield className="h-6 w-6 text-primary animate-pulse" />
          <div className="absolute -inset-1 blur-md bg-primary/20 rounded-lg -z-10" />
        </div>
        <div className="flex flex-col">
          <span className="text-xl font-bold tracking-wider text-white neon-text">
            VENDOR<span className="text-primary">AUDIT</span>
          </span>
          <span className="text-[0.65rem] uppercase tracking-[0.2em] text-muted-foreground animate-pulse">
            AI GRC Protocol
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 px-4 py-6 z-10 overflow-y-auto custom-scrollbar">
        {navigation.map((item) => {
          const isActive = location.pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'group flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-all duration-200 relative overflow-hidden',
                isActive
                  ? 'text-primary bg-primary/10 border border-primary/20 shadow-[0_0_10px_rgba(0,242,255,0.15)]'
                  : 'text-muted-foreground hover:text-white hover:bg-white/5 hover:border-white/10 border border-transparent'
              )}
            >
              <item.icon className={cn(
                "h-5 w-5 transition-transform duration-300 group-hover:scale-110",
                isActive ? "text-primary drop-shadow-[0_0_5px_rgba(0,242,255,0.5)]" : "text-muted-foreground group-hover:text-primary"
              )} />
              <span className="relative z-10 tracking-wide">{item.name}</span>
              {isActive && (
                <div className="absolute right-2 w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_5px_#00f2ff] animate-pulse" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="border-t border-white/10 p-4 bg-black/40 backdrop-blur-md z-10">
        <div className="flex items-center gap-3 mb-4 p-2 rounded-lg bg-white/5 border border-white/5 hover:border-primary/20 transition-colors">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-tr from-primary/80 to-secondary/80 text-white text-sm font-bold shadow-lg ring-1 ring-white/10">
            {(user as any)?.user_metadata?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
            <div className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full bg-accent border-2 border-black shadow-[0_0_5px_#00ff9d]" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-white truncate">{(user as any)?.user_metadata?.full_name || user?.email}</p>
            <p className="text-xs text-primary/80 capitalize flex items-center gap-1">
              <span className="w-1 h-1 rounded-full bg-primary inline-block animate-pulse" />
              {(user as any)?.app_metadata?.roles?.[0] || 'Security Officer'}
            </p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <Link
            to="/settings"
            className="flex items-center justify-center gap-2 rounded-md border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-muted-foreground hover:text-white hover:bg-white/10 hover:border-primary/30 transition-all hover:shadow-[0_0_10px_rgba(0,242,255,0.1)]"
          >
            <Settings className="h-3.5 w-3.5" />
            Config
          </Link>
          <button
            onClick={logout}
            className="flex items-center justify-center gap-2 rounded-md border border-destructive/20 bg-destructive/10 px-3 py-2 text-xs font-medium text-destructive hover:bg-destructive/20 hover:text-destructive-foreground hover:border-destructive/40 transition-all hover:shadow-[0_0_10px_rgba(255,0,51,0.2)]"
          >
            <LogOut className="h-3.5 w-3.5" />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
