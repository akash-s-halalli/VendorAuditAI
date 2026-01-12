import { useQuery } from '@tanstack/react-query';
import { Building2, FileText, AlertTriangle, CheckCircle, Clock, Activity, Shield, Cpu, Zap } from 'lucide-react';
import { Badge } from '@/components/ui';
import apiClient, { getApiErrorMessage } from '@/lib/api';

interface DashboardStats {
  totalVendors: number;
  totalDocuments: number;
  pendingAnalysis: number;
  completedAnalysis: number;
  criticalFindings: number;
  highFindings: number;
  mediumFindings: number;
  lowFindings: number;
}

export function Dashboard() {
  const { data: stats, isLoading, isError, error } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/dashboard/stats');
      return response.data;
    },
  });

  const statCards = [
    {
      title: 'Total Vendors',
      value: stats?.totalVendors || 0,
      icon: Building2,
      description: 'Active vendors monitored',
      color: 'text-blue-400',
      glow: 'shadow-[0_0_20px_rgba(96,165,250,0.3)]',
    },
    {
      title: 'Documents',
      value: stats?.totalDocuments || 0,
      icon: FileText,
      description: 'Security reports',
      color: 'text-purple-400',
      glow: 'shadow-[0_0_20px_rgba(192,132,252,0.3)]',
    },
    {
      title: 'Pending Analysis',
      value: stats?.pendingAnalysis || 0,
      icon: Clock,
      description: 'Awaiting AI review',
      color: 'text-amber-400',
      glow: 'shadow-[0_0_20px_rgba(251,191,36,0.3)]',
    },
    {
      title: 'Completed',
      value: stats?.completedAnalysis || 0,
      icon: CheckCircle,
      description: 'Analyses finalized',
      color: 'text-primary',
      glow: 'shadow-[0_0_20px_rgba(0,242,255,0.3)]',
    },
  ];

  const findingsData = [
    { severity: 'Critical', count: stats?.criticalFindings || 0, color: 'bg-red-500', glow: 'shadow-[0_0_10px_rgba(239,68,68,0.5)]' },
    { severity: 'High', count: stats?.highFindings || 0, color: 'bg-orange-500', glow: 'shadow-[0_0_10px_rgba(249,115,22,0.5)]' },
    { severity: 'Medium', count: stats?.mediumFindings || 0, color: 'bg-yellow-500', glow: 'shadow-[0_0_10px_rgba(234,179,8,0.5)]' },
    { severity: 'Low', count: stats?.lowFindings || 0, color: 'bg-green-500', glow: 'shadow-[0_0_10px_rgba(34,197,94,0.5)]' },
  ];

  if (isLoading) {
    return (
      <div className="p-8 space-y-8">
        <div className="h-12 w-1/3 bg-muted/20 animate-pulse rounded-lg" />
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-32 bg-muted/10 animate-pulse rounded-xl" />)}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-8 flex items-center justify-center h-[50vh]">
        <div className="glass-panel p-8 rounded-xl border-red-500/30 text-center max-w-md">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4 animate-bounce" />
          <h3 className="text-xl font-bold text-white mb-2">System Error</h3>
          <p className="text-muted-foreground">{getApiErrorMessage(error)}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 animate-in fade-in slide-in-from-top-5 duration-500">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-white neon-text">
            Command Center
          </h1>
          <p className="text-muted-foreground mt-2 flex items-center gap-2">
            <Activity className="h-4 w-4 text-primary animate-pulse" />
            System Status: <span className="text-primary font-mono">ONLINE</span>
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-panel border-primary/20">
          <Zap className="h-4 w-4 text-yellow-400" />
          <span className="text-xs font-mono text-muted-foreground">AI CORES ACTIVE</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, i) => (
          <div
            key={stat.title}
            className={`glass-card rounded-xl p-6 relative overflow-hidden group hover:border-primary/50 transition-all duration-300 animate-in fade-in slide-in-from-bottom-5 delay-[${i * 100}ms]`}
          >
            <div className={`absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity ${stat.color}`}>
              <stat.icon className="h-24 w-24 transform rotate-12" />
            </div>
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
              <div className={`text-3xl font-bold text-white mb-1 ${stat.color} drop-shadow-md`}>{stat.value}</div>
              <p className="text-xs text-muted-foreground/80">{stat.description}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        {/* Main Chart / Findings Area */}
        <div className="glass-card rounded-xl p-6 lg:col-span-4 border-primary/10">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              Security Findings Distribution
            </h3>
          </div>
          <div className="space-y-6">
            {findingsData.map((finding) => (
              <div key={finding.severity} className="space-y-2 group">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground font-medium">{finding.severity}</span>
                  <span className="text-white font-mono">{finding.count}</span>
                </div>
                <div className="h-2 w-full bg-black/40 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${finding.color} ${finding.glow} transition-all duration-1000 ease-out group-hover:brightness-110`}
                    style={{ width: `${Math.min((finding.count / 20) * 100, 100)}%` }} // Scaled for demo
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Agents Status (Visual Only for now) */}
        <div className="glass-card rounded-xl p-0 lg:col-span-3 border-secondary/20 overflow-hidden flex flex-col">
          <div className="p-6 border-b border-white/5 bg-secondary/5">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Cpu className="h-5 w-5 text-secondary" />
              Active Cyber Agents
            </h3>
          </div>
          <div className="p-6 space-y-4 flex-1">
            {[
              { name: 'Sentinel Prime', role: 'Threat Detection', status: 'Scanning', color: 'text-primary' },
              { name: 'Audit Core', role: 'Compliance Check', status: 'Idle', color: 'text-muted-foreground' },
              { name: 'Vector Analyst', role: 'Risk Assessment', status: 'Processing', color: 'text-secondary' },
            ].map((agent, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-black/20 border border-white/5 hover:border-white/10 transition-colors">
                <div className="flex items-center gap-3">
                  <div className={`h-2 w-2 rounded-full ${agent.status !== 'Idle' ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
                  <div>
                    <p className="text-sm font-medium text-white">{agent.name}</p>
                    <p className="text-xs text-muted-foreground">{agent.role}</p>
                  </div>
                </div>
                <Badge variant="outline" className={`glass-panel border-0 ${agent.color}`}>
                  {agent.status}
                </Badge>
              </div>
            ))}
          </div>
          <div className="p-4 bg-black/40 text-center">
            <button className="text-xs text-primary hover:text-white transition-colors uppercase tracking-widest font-bold">
              View Agent Network
            </button>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        {[
          { title: 'Upload Document', desc: 'Ingest new security report', icon: FileText, href: '/documents?action=upload', color: 'text-blue-400' },
          { title: 'Add Vendor', desc: 'Register new entity', icon: Building2, href: '/vendors?action=create', color: 'text-purple-400' },
          { title: 'Query Database', desc: 'Ask AI Assistant', icon: Zap, href: '/query', color: 'text-yellow-400' },
        ].map((action) => (
          <a
            key={action.title}
            href={action.href}
            className="glass-card p-6 rounded-xl border-white/5 hover:border-primary/30 hover:bg-white/5 transition-all duration-300 group flex items-start gap-4"
          >
            <div className={`p-3 rounded-lg bg-black/40 group-hover:scale-110 transition-transform ${action.color}`}>
              <action.icon className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-bold text-white group-hover:text-primary transition-colors">{action.title}</h3>
              <p className="text-sm text-muted-foreground">{action.desc}</p>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
