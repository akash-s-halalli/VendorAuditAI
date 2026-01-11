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
    <div className="flex h-full w-64 flex-col bg-card border-r">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 border-b px-6">
        <Shield className="h-8 w-8 text-primary" />
        <span className="text-xl font-bold">VendorAuditAI</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = location.pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="border-t p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
            {user?.fullName?.charAt(0) || user?.email?.charAt(0) || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.fullName || user?.email}</p>
            <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Link
            to="/settings"
            className="flex-1 flex items-center justify-center gap-2 rounded-md border px-3 py-2 text-sm text-muted-foreground hover:bg-accent"
          >
            <Settings className="h-4 w-4" />
            Settings
          </Link>
          <button
            onClick={logout}
            className="flex items-center justify-center rounded-md border px-3 py-2 text-sm text-muted-foreground hover:bg-destructive hover:text-destructive-foreground"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
