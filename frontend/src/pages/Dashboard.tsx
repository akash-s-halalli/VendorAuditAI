import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Building2, FileText, AlertTriangle, CheckCircle, Clock, Activity, Shield, Cpu, Search } from 'lucide-react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui';
import { MagneticButton } from '@/components/ui/MagneticButton';
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

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
};

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
    { severity: 'Critical', count: stats?.criticalFindings || 0, color: 'bg-obsidian-crimson', text: 'text-obsidian-crimson', glow: 'shadow-[0_0_15px_rgba(230,57,70,0.4)]' },
    { severity: 'High', count: stats?.highFindings || 0, color: 'bg-orange-500', text: 'text-orange-500', glow: 'shadow-[0_0_15px_rgba(249,115,22,0.4)]' },
    { severity: 'Medium', count: stats?.mediumFindings || 0, color: 'bg-obsidian-gold', text: 'text-obsidian-gold', glow: 'shadow-[0_0_15px_rgba(255,184,0,0.4)]' },
    { severity: 'Low', count: stats?.lowFindings || 0, color: 'bg-obsidian-emerald', text: 'text-obsidian-emerald', glow: 'shadow-[0_0_15px_rgba(0,200,83,0.4)]' },
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
        <div className="h-12 w-1/3 bg-white/5 animate-pulse rounded-xl" />
        <div className="grid gap-6 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-40 bg-white/5 animate-pulse rounded-2xl" />)}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-8 flex items-center justify-center h-[50vh]">
        <div className="glass-panel-liquid p-8 text-center max-w-md rounded-2xl border-obsidian-crimson/20">
          <AlertTriangle className="h-12 w-12 text-obsidian-crimson mx-auto mb-4 animate-pulse" />
          <h3 className="text-xl font-bold text-white mb-2">System Error</h3>
          <p className="text-muted-foreground">{getApiErrorMessage(error)}</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-8 pb-8"
    >
      {/* Header Section */}
      <motion.div variants={item} className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-6xl font-bold tracking-tight text-white font-heading mb-2">
            Command<span className="text-obsidian-teal">Center</span>
          </h1>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/5">
              <span className="w-1.5 h-1.5 rounded-full bg-obsidian-emerald animate-pulse"></span>
              System Optimal
            </span>
            <span className="text-white/10">|</span>
            <span className="font-mono text-obsidian-teal/80">v3.0.0-OBSIDIAN</span>
          </div>
        </div>

        <div className="flex gap-3">
          <div className="px-5 py-2.5 rounded-xl glass-panel-liquid flex items-center gap-3">
            <Clock className="h-4 w-4 text-obsidian-teal animate-pulse" />
            <span className="font-mono text-sm text-white">
              {new Date().toLocaleTimeString('en-US', { hour12: false })}
            </span>
          </div>
        </div>
      </motion.div>

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 auto-rows-[minmax(200px,auto)]">

        {/* 1. Main Stats - Critical Findings (Large Square) */}
        <motion.div variants={item} className="col-span-1 lg:col-span-2 row-span-2 h-full">
          <div className="h-full glass-panel-liquid rounded-3xl p-8 flex flex-col justify-between group relative overflow-hidden transition-all duration-500 hover:shadow-[0_0_40px_rgba(230,57,70,0.1)]">
            {/* Ambient Background Glow */}
            <div className="absolute -right-20 -top-20 w-64 h-64 bg-obsidian-crimson/10 rounded-full blur-3xl group-hover:bg-obsidian-crimson/20 transition-all duration-700" />

            <div className="flex justify-between items-start z-10">
              <div>
                <h3 className="text-slate-400 font-medium flex items-center gap-2 mb-1">
                  <Shield className="h-5 w-5 text-obsidian-crimson" />
                  CRITICAL EXPOSURE
                </h3>
                <p className="text-xs text-obsidian-crimson/80 uppercase tracking-widest font-mono">Action Required</p>
              </div>
              <Badge variant="outline" className="border-obsidian-crimson/30 text-obsidian-crimson bg-obsidian-crimson/10 animate-pulse">
                LIVE
              </Badge>
            </div>

            <div className="mt-8 z-10">
              <div className="flex items-baseline gap-4">
                <div className="text-9xl font-bold text-white font-mono tracking-tighter group-hover:scale-105 transition-transform duration-500" style={{ textShadow: '0 0 30px rgba(230,57,70,0.3)' }}>
                  {stats?.criticalFindings || 0}
                </div>
                <div className="text-xl text-slate-400 font-light mb-4">Threats</div>
              </div>

              <div className="h-2 w-full bg-white/5 rounded-full mt-6 overflow-hidden relative">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: '30%' }}
                  transition={{ duration: 1.5, ease: "circOut" }}
                  className="h-full bg-obsidian-crimson shadow-[0_0_20px_rgba(230,57,70,0.6)]"
                />
              </div>
            </div>
          </div>
        </motion.div>

        {/* 2. Total Vendors (Wide Rect) */}
        <motion.div variants={item} className="col-span-1 lg:col-span-2 h-full">
          <div
            className="h-full glass-panel-liquid rounded-3xl p-8 flex items-center justify-between cursor-pointer group relative overflow-hidden"
            onClick={() => navigate('/vendors')}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-obsidian-teal/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            <div className="relative z-10">
              <p className="text-slate-400 text-sm uppercase tracking-widest mb-3">Active Vendors</p>
              <div className="text-5xl font-bold text-white font-mono flex items-baseline gap-3">
                {stats?.totalVendors || 0}
                <span className="text-lg font-sans text-obsidian-emerald font-medium py-1 px-3 rounded-full bg-obsidian-emerald/10 border border-obsidian-emerald/20">+12%</span>
              </div>
            </div>
            <div className="h-20 w-20 rounded-2xl bg-obsidian-teal/10 flex items-center justify-center border border-obsidian-teal/20 group-hover:scale-110 transition-transform duration-500 shadow-[0_0_20px_rgba(0,212,170,0.2)]">
              <Building2 className="h-10 w-10 text-obsidian-teal" />
            </div>
          </div>
        </motion.div>

        {/* 3. Pending Analysis (Small Square) */}
        <motion.div variants={item}>
          <div
            className="h-full glass-panel-liquid rounded-3xl p-6 flex flex-col justify-between cursor-pointer group relative overflow-hidden"
            onClick={() => navigate('/documents')}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-obsidian-gold/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

            <div className="flex justify-between items-start">
              <Clock className="h-8 w-8 text-obsidian-gold mb-2" />
              <div className="h-2 w-2 rounded-full bg-obsidian-gold animate-pulse" />
            </div>

            <div>
              <div className="text-4xl font-bold text-white font-mono mb-1">{stats?.pendingAnalysis || 0}</div>
              <p className="text-xs text-slate-400 uppercase tracking-widest">Pending Review</p>
            </div>
          </div>
        </motion.div>

        {/* 4. Completed Docs (Small Square) */}
        <motion.div variants={item}>
          <div
            className="h-full glass-panel-liquid rounded-3xl p-6 flex flex-col justify-between cursor-pointer group relative overflow-hidden"
            onClick={() => navigate('/analysis')}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-obsidian-emerald/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

            <div className="flex justify-between items-start">
              <CheckCircle className="h-8 w-8 text-obsidian-emerald mb-2" />
              <div className="h-2 w-2 rounded-full bg-obsidian-emerald animate-pulse" />
            </div>

            <div>
              <div className="text-4xl font-bold text-white font-mono mb-1">{stats?.completedAnalysis || 0}</div>
              <p className="text-xs text-slate-400 uppercase tracking-widest">Analyzed</p>
            </div>
          </div>
        </motion.div>

        {/* 5. Findings Distribution (Tall Rect) */}
        <motion.div variants={item} className="col-span-1 lg:col-span-1 row-span-2 h-full">
          <div
            className="h-full glass-panel-liquid rounded-3xl p-6 cursor-pointer group hover:border-white/10 transition-all"
            onClick={() => navigate('/analysis')}
          >
            <h3 className="text-white font-semibold mb-8 flex items-center gap-2 font-heading">
              <Activity className="h-5 w-5 text-obsidian-teal" />
              Risk Distribution
            </h3>
            <div className="space-y-8">
              {findingsData.map((finding) => (
                <div key={finding.severity} className="space-y-2 group/item">
                  <div className="flex justify-between text-xs uppercase tracking-wider">
                    <span className={`${finding.text} font-bold`}>{finding.severity}</span>
                    <span className="text-white font-mono opacity-60 group-hover/item:opacity-100 transition-opacity">{finding.count}</span>
                  </div>
                  <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min((finding.count / 20) * 100, 100)}%` }}
                      transition={{ duration: 1, delay: 0.5 }}
                      className={`h-full ${finding.color} ${finding.glow}`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* 6. AI Agent Status (Wide) */}
        <motion.div variants={item} className="col-span-1 lg:col-span-3 h-full">
          <div className="h-full glass-panel-liquid rounded-3xl p-0 flex flex-col lg:flex-row overflow-hidden border border-white/5">
            <div className="p-8 lg:w-1/3 border-b lg:border-b-0 lg:border-r border-white/5 bg-white/[0.02] flex flex-col justify-center relative">
              <div className="absolute inset-0 bg-obsidian-teal/5 animate-pulse pointer-events-none" />
              <h3 className="text-2xl font-bold text-white mb-2 flex items-center gap-3 z-10 font-heading">
                <Cpu className="h-6 w-6 text-obsidian-teal" />
                Neural Net
              </h3>
              <p className="text-sm text-slate-400 mb-6 z-10 leading-relaxed">
                Autonomous agents monitoring vector threats in real-time.
              </p>
              <button
                onClick={() => handleQuickAction('agents')}
                className="z-10 text-xs font-mono text-obsidian-teal border border-obsidian-teal/30 rounded-lg px-4 py-2 w-fit hover:bg-obsidian-teal/10 transition-colors uppercase tracking-wider font-bold"
              >
                Manage Network
              </button>
            </div>
            <div className="p-8 lg:w-2/3 grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { name: 'Sentinel Prime', status: 'SCANNING', color: 'text-obsidian-teal' },
                { name: 'Vector Analyst', status: 'PROCESSING', color: 'text-obsidian-blue' },
                { name: 'Watchdog Zero', status: 'IDLE', color: 'text-slate-500' },
                { name: 'Audit Core', status: 'INDEXING', color: 'text-obsidian-emerald' }
              ].map((agent, idx) => (
                <motion.div
                  key={agent.name}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1 + (idx * 0.1) }}
                  className="flex items-center justify-between p-4 rounded-xl bg-black/20 border border-white/5 hover:border-white/10 transition-colors group"
                >
                  <span className="text-sm font-medium text-white group-hover:text-white transition-colors">{agent.name}</span>
                  <span className={`text-[10px] font-mono ${agent.color} border border-white/5 px-2 py-1 rounded bg-white/5 flex items-center gap-2`}>
                    {agent.status === 'SCANNING' && <span className="w-1.5 h-1.5 rounded-full bg-obsidian-teal animate-pulse" />}
                    {agent.status}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Quick Actions Footer */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Upload New Report', icon: FileText, cmd: 'upload' },
          { label: 'Register Vendor', icon: Building2, cmd: 'register' },
          { label: 'Execute AI Query', icon: Search, cmd: 'query' }
        ].map((action, i) => (
          <MagneticButton
            key={i}
            onClick={() => handleQuickAction(action.cmd)}
            className="glass-panel-liquid group flex items-center justify-between p-6 rounded-2xl hover:border-obsidian-teal/30 transition-all duration-300 w-full"
          >
            <span className="text-sm font-medium text-slate-400 group-hover:text-white transition-colors">{action.label}</span>
            <div className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center group-hover:bg-obsidian-teal/20 transition-colors group-hover:scale-110 duration-300">
              <action.icon className="h-5 w-5 text-slate-500 group-hover:text-obsidian-teal transition-colors" />
            </div>
          </MagneticButton>
        ))}
      </div>
    </motion.div>
  );
}
