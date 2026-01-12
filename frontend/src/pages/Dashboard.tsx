import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Building2, FileText, AlertTriangle, CheckCircle, Clock, Activity, Shield, Cpu, Zap } from 'lucide-react';
import { Badge } from '@/components/ui';
import { CyberCard } from '@/components/ui/CyberCard';
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
  const navigate = useNavigate();

  const { data: stats, isLoading, isError, error } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/dashboard/stats');
      return response.data;
    },
  });

  const findingsData = [
    { severity: 'Critical', count: stats?.criticalFindings || 0, color: 'bg-red-500', text: 'text-red-500', glow: 'shadow-[0_0_10px_rgba(239,68,68,0.5)]' },
    { severity: 'High', count: stats?.highFindings || 0, color: 'bg-orange-500', text: 'text-orange-500', glow: 'shadow-[0_0_10px_rgba(249,115,22,0.5)]' },
    { severity: 'Medium', count: stats?.mediumFindings || 0, color: 'bg-yellow-500', text: 'text-yellow-500', glow: 'shadow-[0_0_10px_rgba(234,179,8,0.5)]' },
    { severity: 'Low', count: stats?.lowFindings || 0, color: 'bg-green-500', text: 'text-green-500', glow: 'shadow-[0_0_10px_rgba(34,197,94,0.5)]' },
  ];

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'upload':
        navigate('/documents');
        break;
      case 'register':
        navigate('/vendors');
        break;
      case 'query':
        navigate('/query');
        break;
      case 'agents':
        navigate('/agents');
        break;
      default:
        break;
    }
  };

  if (isLoading) {
    return (
      <div className="p-8 space-y-8">
        <div className="h-12 w-1/3 bg-muted/20 animate-pulse rounded-lg" />
        <div className="grid gap-6 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-40 bg-muted/10 animate-pulse rounded-xl" />)}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-8 flex items-center justify-center h-[50vh]">
        <CyberCard variant="danger" className="p-8 text-center max-w-md">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4 animate-bounce" />
          <h3 className="text-xl font-bold text-white mb-2">System Error</h3>
          <p className="text-muted-foreground">{getApiErrorMessage(error)}</p>
        </CyberCard>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-8 animate-in fade-in duration-500">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
        <div>
          <h1 className="text-5xl font-bold tracking-tighter text-white neon-text mb-2">
            COMMAND<span className="text-primary">CENTER</span>
          </h1>
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              SYSTEM ONLINE
            </span>
            <span className="text-white/10">|</span>
            <span className="font-mono text-primary/80">V.2.0.4-ALPHA</span>
          </div>
        </div>

        <div className="flex gap-3">
          <div className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 flex items-center gap-2">
            <Clock className="h-4 w-4 text-primary" />
            <span className="font-mono text-sm text-white">
              {new Date().toLocaleTimeString('en-US', { hour12: false })}
            </span>
          </div>
        </div>
      </div>

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 auto-rows-[minmax(180px,auto)]">

        {/* 1. Main Stats - Critical Findings (Large Square) */}
        <CyberCard variant="danger" className="col-span-1 lg:col-span-2 row-span-2 p-6 flex flex-col justify-between group">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-muted-foreground font-medium flex items-center gap-2">
                <Shield className="h-5 w-5 text-red-500" />
                CRITICAL THREATS
              </h3>
              <p className="text-xs text-red-400/60 mt-1 uppercase tracking-wider font-mono">Immediate Action Required</p>
            </div>
            <Badge variant="outline" className="border-red-500/30 text-red-400 bg-red-500/10 animate-pulse">
              ACTIVE
            </Badge>
          </div>

          <div className="mt-8">
            <div className="text-7xl font-bold text-white font-mono tracking-tighter neon-text group-hover:scale-105 transition-transform duration-300">
              {stats?.criticalFindings || 0}
            </div>
            <div className="h-2 w-full bg-white/5 rounded-full mt-4 overflow-hidden">
              <div className="h-full bg-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)] w-[30%]" />
            </div>
          </div>
        </CyberCard>

        {/* 2. Total Vendors (Wide Rect) */}
        <CyberCard
          className="col-span-1 lg:col-span-2 p-6 flex items-center justify-between cursor-pointer hover:border-primary/50 transition-all"
          onClick={() => navigate('/vendors')}
        >
          <div>
            <p className="text-muted-foreground text-sm uppercase tracking-wider mb-2">Monitored Vendors</p>
            <div className="text-4xl font-bold text-white font-mono flex items-baseline gap-2">
              {stats?.totalVendors || 0}
              <span className="text-sm font-sans text-green-400 font-normal">+12%</span>
            </div>
          </div>
          <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
            <Building2 className="h-8 w-8 text-primary" />
          </div>
        </CyberCard>

        {/* 3. Pending Analysis (Small Square) */}
        <CyberCard
          variant="warning"
          className="p-6 flex flex-col justify-center gap-2 cursor-pointer hover:border-yellow-500/50 transition-all"
          onClick={() => navigate('/documents')}
        >
          <Clock className="h-8 w-8 text-yellow-500 mb-2" />
          <div className="text-3xl font-bold text-white font-mono">{stats?.pendingAnalysis || 0}</div>
          <p className="text-xs text-muted-foreground uppercase tracking-widest">Pending Review</p>
        </CyberCard>

        {/* 4. Completed Docs (Small Square) */}
        <CyberCard
          variant="success"
          className="p-6 flex flex-col justify-center gap-2 cursor-pointer hover:border-green-500/50 transition-all"
          onClick={() => navigate('/analysis')}
        >
          <CheckCircle className="h-8 w-8 text-green-500 mb-2" />
          <div className="text-3xl font-bold text-white font-mono">{stats?.completedAnalysis || 0}</div>
          <p className="text-xs text-muted-foreground uppercase tracking-widest">Analyzed</p>
        </CyberCard>

        {/* 5. Findings Distribution (Tall Rect) */}
        <CyberCard
          className="col-span-1 lg:col-span-1 row-span-2 p-6 cursor-pointer hover:border-primary/50 transition-all"
          onClick={() => navigate('/analysis')}
        >
          <h3 className="text-white font-semibold mb-6 flex items-center gap-2">
            <Activity className="h-4 w-4 text-primary" />
            Risk Distribution
          </h3>
          <div className="space-y-6">
            {findingsData.map((finding) => (
              <div key={finding.severity} className="space-y-1">
                <div className="flex justify-between text-xs uppercase tracking-wider">
                  <span className={finding.text}>{finding.severity}</span>
                  <span className="text-white font-mono">{finding.count}</span>
                </div>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                  <div className={`h-full ${finding.color} ${finding.glow}`} style={{ width: `${Math.min((finding.count / 20) * 100, 100)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </CyberCard>

        {/* 6. AI Agent Status (Wide) */}
        <CyberCard className="col-span-1 lg:col-span-3 p-0 flex flex-col lg:flex-row overflow-hidden">
          <div className="p-6 lg:w-1/3 border-b lg:border-b-0 lg:border-r border-white/10 bg-white/5 flex flex-col justify-center">
            <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <Cpu className="h-6 w-6 text-primary animate-pulse" />
              Neural Net
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Active agent operations and real-time threat scanning.
            </p>
            <button
              onClick={() => handleQuickAction('agents')}
              className="text-xs font-mono text-primary border border-primary/30 rounded px-3 py-1.5 w-fit hover:bg-primary/10 transition-colors uppercase"
            >
              Manage Network
            </button>
          </div>
          <div className="p-6 lg:w-2/3 grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { name: 'Sentinel Prime', status: 'SCANNING', color: 'text-primary' },
              { name: 'Vector Analyst', status: 'PROCESSING', color: 'text-purple-400' },
              { name: 'Watchdog Zero', status: 'IDLE', color: 'text-gray-400' },
              { name: 'Audit Core', status: 'INDEXING', color: 'text-green-400' }
            ].map(agent => (
              <div key={agent.name} className="flex items-center justify-between p-3 rounded bg-black/40 border border-white/5">
                <span className="text-sm font-medium text-white">{agent.name}</span>
                <span className={`text-[10px] font-mono ${agent.color} border border-white/10 px-2 py-0.5 rounded`}>
                  {agent.status}
                </span>
              </div>
            ))}
          </div>
        </CyberCard>
      </div>

      {/* Quick Actions Footer */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Upload New Report', icon: FileText, cmd: 'upload' },
          { label: 'Register Vendor', icon: Building2, cmd: 'register' },
          { label: 'Execute AI Query', icon: Zap, cmd: 'query' }
        ].map((action, i) => (
          <button
            key={i}
            onClick={() => handleQuickAction(action.cmd)}
            className="glass-card group flex items-center justify-between p-5 rounded-xl hover:border-primary/50 transition-all duration-300"
          >
            <span className="text-sm font-semibold text-muted-foreground group-hover:text-white transition-colors">{action.label}</span>
            <div className="h-8 w-8 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
              <action.icon className="h-4 w-4 text-white/50 group-hover:text-primary transition-colors" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
