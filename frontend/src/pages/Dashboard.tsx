import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Building2, FileText, AlertTriangle, CheckCircle, Clock, Activity, Shield, Cpu, Search, Sparkles, TrendingUp, RefreshCw, Loader2 } from 'lucide-react';
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { Badge, Button } from '@/components/ui';
import { MagneticButton } from '@/components/ui/MagneticButton';
import apiClient, { getApiErrorMessage } from '@/lib/api';
import { useEffect, useState } from 'react';

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

// Animated Counter Component
function AnimatedCounter({ value, duration = 2 }: { value: number; duration?: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const controls = animate(count, value, { duration });
    const unsubscribe = rounded.on("change", (v) => setDisplayValue(v));
    return () => {
      controls.stop();
      unsubscribe();
    };
  }, [value, duration, count, rounded]);

  return <span>{displayValue}</span>;
}

// Floating Particles Component
function FloatingParticles() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-obsidian-teal/30"
          initial={{
            x: Math.random() * 100 + '%',
            y: Math.random() * 100 + '%',
            opacity: 0.3
          }}
          animate={{
            y: [null, '-20%', null],
            opacity: [0.3, 0.8, 0.3]
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: i * 0.5
          }}
        />
      ))}
    </div>
  );
}

// Pulse Ring Animation
function PulseRing({ color = 'obsidian-teal' }: { color?: string }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
      <motion.div
        className={`w-full h-full rounded-full border border-${color}/20`}
        animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
    </div>
  );
}

export function Dashboard() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [seedMessage, setSeedMessage] = useState<string | null>(null);

  const { data: stats, isLoading, isError, error } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/dashboard/stats');
      return response.data;
    },
  });

  // Debug seed mutation to test each step
  const [debugResult, setDebugResult] = useState<string | null>(null);
  const debugSeedMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.get('/admin/debug-seed');
      return response.data;
    },
    onSuccess: (data) => {
      console.log('[DebugSeed] Result:', data);
      setDebugResult(JSON.stringify(data.steps, null, 2));
      setTimeout(() => setDebugResult(null), 30000);
    },
    onError: (error: unknown) => {
      console.error('[DebugSeed] Error:', error);
      setDebugResult(`Error: ${getApiErrorMessage(error)}`);
      setTimeout(() => setDebugResult(null), 10000);
    },
  });

  // Reseed demo data mutation - increased timeout since this operation takes a while
  const reseedMutation = useMutation({
    mutationFn: async () => {
      const token = localStorage.getItem('access_token');
      console.log('[Reseed] Token present:', !!token, 'Token preview:', token?.substring(0, 20));
      console.log('[Reseed] Making request to /admin/seed-demo-data');
      try {
        const response = await apiClient.post('/admin/seed-demo-data', {}, {
          timeout: 120000, // 2 minute timeout for seed operation
        });
        console.log('[Reseed] Success:', response.data);
        return response.data;
      } catch (err) {
        console.error('[Reseed] Error:', err);
        throw err;
      }
    },
    onSuccess: (data) => {
      setSeedMessage(`Seeded: ${data.vendors_created} vendors, ${data.playbooks_created} playbooks, ${data.findings_created} findings`);
      // Invalidate all queries to refresh data
      queryClient.invalidateQueries();
      setTimeout(() => setSeedMessage(null), 5000);
    },
    onError: (error: unknown) => {
      // More detailed error message for debugging
      let errorMsg = getApiErrorMessage(error);
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { status?: number; data?: { detail?: string } }; code?: string };
        if (axiosError.response?.status) {
          errorMsg = `HTTP ${axiosError.response.status}: ${axiosError.response.data?.detail || errorMsg}`;
        } else if (axiosError.code === 'ECONNABORTED') {
          errorMsg = 'Request timed out - server may be processing. Try refreshing in 30s.';
        }
      }
      setSeedMessage(`Error: ${errorMsg}`);
      setTimeout(() => setSeedMessage(null), 10000);
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
            <Button
              variant="outline"
              size="sm"
              onClick={() => reseedMutation.mutate()}
              disabled={reseedMutation.isPending}
              className="ml-4"
            >
              {reseedMutation.isPending ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Reseed Demo Data
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => debugSeedMutation.mutate()}
              disabled={debugSeedMutation.isPending}
              className="ml-2 border-yellow-500/50 text-yellow-500"
            >
              {debugSeedMutation.isPending ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <AlertTriangle className="h-4 w-4 mr-2" />
              )}
              Debug
            </Button>
            {seedMessage && (
              <span className="ml-2 text-xs text-obsidian-teal">{seedMessage}</span>
            )}
            {debugResult && (
              <pre className="ml-2 text-xs text-yellow-400 bg-black/50 p-2 rounded max-w-md overflow-auto">{debugResult}</pre>
            )}
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
          <div className="h-full glass-card-crimson rounded-3xl p-8 flex flex-col justify-between group relative overflow-hidden transition-all duration-500 hover:shadow-[0_0_60px_rgba(230,57,70,0.15)] card-hover-lift">
            {/* Floating Particles */}
            <FloatingParticles />

            {/* Ambient Background Glow */}
            <div className="absolute -right-20 -top-20 w-64 h-64 bg-obsidian-crimson/10 rounded-full blur-3xl group-hover:bg-obsidian-crimson/25 transition-all duration-700" />
            <div className="absolute -left-10 -bottom-10 w-48 h-48 bg-obsidian-crimson/5 rounded-full blur-2xl group-hover:bg-obsidian-crimson/15 transition-all duration-700" />

            <div className="flex justify-between items-start z-10">
              <div>
                <h3 className="text-slate-400 font-medium flex items-center gap-2 mb-1">
                  <Shield className="h-5 w-5 text-obsidian-crimson drop-shadow-[0_0_8px_rgba(230,57,70,0.5)]" />
                  CRITICAL EXPOSURE
                </h3>
                <p className="text-xs text-obsidian-crimson/80 uppercase tracking-widest font-mono">Action Required</p>
              </div>
              <Badge variant="outline" className="border-obsidian-crimson/30 text-obsidian-crimson bg-obsidian-crimson/10 animate-pulse glow-crimson">
                LIVE
              </Badge>
            </div>

            <div className="mt-8 z-10">
              <div className="flex items-baseline gap-4">
                <div className="text-9xl font-bold text-white font-mono tracking-tighter group-hover:scale-105 transition-transform duration-500 text-glow-crimson">
                  <AnimatedCounter value={stats?.criticalFindings || 0} duration={2.5} />
                </div>
                <div className="text-xl text-slate-400 font-light mb-4">
                  <motion.span
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.5 }}
                  >
                    Threats
                  </motion.span>
                </div>
              </div>

              <div className="h-2 w-full bg-white/5 rounded-full mt-6 overflow-hidden relative">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: '30%' }}
                  transition={{ duration: 1.5, ease: "circOut" }}
                  className="h-full bg-gradient-to-r from-obsidian-crimson to-orange-500 shadow-[0_0_20px_rgba(230,57,70,0.6)]"
                />
                {/* Shimmer effect */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                  animate={{ x: ['-100%', '100%'] }}
                  transition={{ duration: 2, repeat: Infinity, repeatDelay: 1 }}
                />
              </div>
            </div>
          </div>
        </motion.div>

        {/* 2. Total Vendors (Wide Rect) */}
        <motion.div variants={item} className="col-span-1 lg:col-span-2 h-full">
          <div
            className="h-full glass-card-teal rounded-3xl p-8 flex items-center justify-between cursor-pointer group relative overflow-hidden card-hover-lift"
            onClick={() => navigate('/vendors')}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-obsidian-teal/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="absolute -right-10 -top-10 w-40 h-40 bg-obsidian-teal/5 rounded-full blur-2xl group-hover:bg-obsidian-teal/15 transition-all duration-500" />

            <div className="relative z-10">
              <p className="text-slate-400 text-sm uppercase tracking-widest mb-3 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-obsidian-teal" />
                Active Vendors
              </p>
              <div className="text-5xl font-bold text-white font-mono flex items-baseline gap-3">
                <span className="text-glow-teal"><AnimatedCounter value={stats?.totalVendors || 0} duration={2} /></span>
                <motion.span
                  className="text-lg font-sans text-obsidian-emerald font-medium py-1 px-3 rounded-full bg-obsidian-emerald/10 border border-obsidian-emerald/20 flex items-center gap-1"
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 1.5, type: "spring" }}
                >
                  <TrendingUp className="h-3 w-3" />
                  +12%
                </motion.span>
              </div>
            </div>
            <div className="h-20 w-20 rounded-2xl bg-obsidian-teal/10 flex items-center justify-center border border-obsidian-teal/20 group-hover:scale-110 transition-transform duration-500 glow-teal relative">
              <Building2 className="h-10 w-10 text-obsidian-teal drop-shadow-[0_0_8px_rgba(0,212,170,0.5)]" />
              <PulseRing color="obsidian-teal" />
            </div>
          </div>
        </motion.div>

        {/* 3. Pending Analysis (Small Square) */}
        <motion.div variants={item}>
          <div
            className="h-full glass-panel-liquid rounded-3xl p-6 flex flex-col justify-between cursor-pointer group relative overflow-hidden card-hover-lift border-pulse"
            onClick={() => navigate('/documents')}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-obsidian-gold/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="absolute -right-8 -bottom-8 w-24 h-24 bg-obsidian-gold/10 rounded-full blur-xl group-hover:bg-obsidian-gold/20 transition-all duration-500" />

            <div className="flex justify-between items-start relative z-10">
              <motion.div
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
              >
                <Clock className="h-8 w-8 text-obsidian-gold drop-shadow-[0_0_8px_rgba(255,184,0,0.5)]" />
              </motion.div>
              <div className="h-2 w-2 rounded-full bg-obsidian-gold animate-pulse glow-gold" />
            </div>

            <div className="relative z-10">
              <div className="text-4xl font-bold text-white font-mono mb-1">
                <AnimatedCounter value={stats?.pendingAnalysis || 0} duration={1.5} />
              </div>
              <p className="text-xs text-slate-400 uppercase tracking-widest">Pending Review</p>
            </div>
          </div>
        </motion.div>

        {/* 4. Completed Docs (Small Square) */}
        <motion.div variants={item}>
          <div
            className="h-full glass-panel-liquid rounded-3xl p-6 flex flex-col justify-between cursor-pointer group relative overflow-hidden card-hover-lift"
            onClick={() => navigate('/analysis')}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-obsidian-emerald/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="absolute -right-8 -bottom-8 w-24 h-24 bg-obsidian-emerald/10 rounded-full blur-xl group-hover:bg-obsidian-emerald/20 transition-all duration-500" />

            <div className="flex justify-between items-start relative z-10">
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: [0.8, 1.1, 1] }}
                transition={{ duration: 0.5, delay: 1 }}
              >
                <CheckCircle className="h-8 w-8 text-obsidian-emerald drop-shadow-[0_0_8px_rgba(0,200,83,0.5)]" />
              </motion.div>
              <div className="h-2 w-2 rounded-full bg-obsidian-emerald animate-pulse glow-emerald" />
            </div>

            <div className="relative z-10">
              <div className="text-4xl font-bold text-white font-mono mb-1">
                <AnimatedCounter value={stats?.completedAnalysis || 0} duration={1.5} />
              </div>
              <p className="text-xs text-slate-400 uppercase tracking-widest">Analyzed</p>
            </div>
          </div>
        </motion.div>

        {/* 5. Findings Distribution (Tall Rect) */}
        <motion.div variants={item} className="col-span-1 lg:col-span-1 row-span-2 h-full">
          <div
            className="h-full glass-panel-liquid rounded-3xl p-6 cursor-pointer group hover:border-white/10 transition-all relative overflow-hidden"
            onClick={() => navigate('/analysis')}
          >
            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-b from-obsidian-teal/5 via-transparent to-obsidian-crimson/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            <h3 className="text-white font-semibold mb-8 flex items-center gap-2 font-heading relative z-10">
              <Activity className="h-5 w-5 text-obsidian-teal animate-pulse" />
              Risk Distribution
            </h3>
            <div className="space-y-8 relative z-10">
              {findingsData.map((finding, idx) => (
                <motion.div
                  key={finding.severity}
                  className="space-y-2 group/item"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.8 + idx * 0.15 }}
                >
                  <div className="flex justify-between text-xs uppercase tracking-wider">
                    <span className={`${finding.text} font-bold`}>{finding.severity}</span>
                    <span className="text-white font-mono opacity-60 group-hover/item:opacity-100 transition-opacity">
                      <AnimatedCounter value={finding.count} duration={1.5} />
                    </span>
                  </div>
                  <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden relative">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min((finding.count / 20) * 100, 100)}%` }}
                      transition={{ duration: 1, delay: 0.5 + idx * 0.1 }}
                      className={`h-full ${finding.color} ${finding.glow} relative`}
                    />
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Total count badge */}
            <motion.div
              className="absolute bottom-6 right-6 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 2, type: "spring" }}
            >
              <span className="text-xs font-mono text-muted-foreground">Total: </span>
              <span className="text-sm font-bold text-white">
                {(stats?.criticalFindings || 0) + (stats?.highFindings || 0) + (stats?.mediumFindings || 0) + (stats?.lowFindings || 0)}
              </span>
            </motion.div>
          </div>
        </motion.div>

        {/* 6. AI Agent Status (Wide) */}
        <motion.div variants={item} className="col-span-1 lg:col-span-3 h-full">
          <div className="h-full gradient-border rounded-3xl p-0 flex flex-col lg:flex-row overflow-hidden">
            <div className="p-8 lg:w-1/3 border-b lg:border-b-0 lg:border-r border-white/5 bg-white/[0.02] flex flex-col justify-center relative overflow-hidden">
              {/* Animated background pulse */}
              <motion.div
                className="absolute inset-0 bg-obsidian-teal/5 pointer-events-none"
                animate={{ opacity: [0.3, 0.6, 0.3] }}
                transition={{ duration: 3, repeat: Infinity }}
              />
              {/* Neural network lines decoration */}
              <div className="absolute inset-0 opacity-10 pointer-events-none">
                <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                  <motion.path
                    d="M0,50 Q25,30 50,50 T100,50"
                    stroke="currentColor"
                    strokeWidth="0.5"
                    fill="none"
                    className="text-obsidian-teal"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </svg>
              </div>

              <h3 className="text-2xl font-bold text-white mb-2 flex items-center gap-3 z-10 font-heading">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                >
                  <Cpu className="h-6 w-6 text-obsidian-teal drop-shadow-[0_0_10px_rgba(0,212,170,0.5)]" />
                </motion.div>
                Neural Net
              </h3>
              <p className="text-sm text-slate-400 mb-6 z-10 leading-relaxed">
                Autonomous agents monitoring vector threats in real-time.
              </p>
              <motion.button
                onClick={() => handleQuickAction('agents')}
                className="z-10 text-xs font-mono text-obsidian-teal border border-obsidian-teal/30 rounded-lg px-4 py-2 w-fit hover:bg-obsidian-teal/10 transition-colors uppercase tracking-wider font-bold glow-teal"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Manage Network
              </motion.button>
            </div>
            <div className="p-8 lg:w-2/3 grid grid-cols-1 md:grid-cols-2 gap-4 bg-black/20">
              {[
                { name: 'Sentinel Prime', status: 'SCANNING', color: 'text-obsidian-teal', glow: 'glow-teal', dot: 'bg-obsidian-teal' },
                { name: 'Vector Analyst', status: 'PROCESSING', color: 'text-obsidian-blue', glow: 'glow-blue', dot: 'bg-obsidian-blue' },
                { name: 'Watchdog Zero', status: 'IDLE', color: 'text-slate-500', glow: '', dot: 'bg-slate-500' },
                { name: 'Audit Core', status: 'INDEXING', color: 'text-obsidian-emerald', glow: 'glow-emerald', dot: 'bg-obsidian-emerald' }
              ].map((agent, idx) => (
                <motion.div
                  key={agent.name}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1 + (idx * 0.1) }}
                  whileHover={{ scale: 1.02, y: -2 }}
                  className={`flex items-center justify-between p-4 rounded-xl bg-black/40 border border-white/5 hover:border-white/10 transition-all group cursor-pointer ${agent.status !== 'IDLE' ? 'hover:' + agent.glow : ''}`}
                >
                  <span className="text-sm font-medium text-white group-hover:text-white transition-colors flex items-center gap-2">
                    <motion.span
                      className={`w-2 h-2 rounded-full ${agent.dot}`}
                      animate={agent.status !== 'IDLE' ? { scale: [1, 1.2, 1], opacity: [1, 0.7, 1] } : {}}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                    {agent.name}
                  </span>
                  <span className={`text-[10px] font-mono ${agent.color} border border-white/5 px-2 py-1 rounded bg-white/5 flex items-center gap-2`}>
                    {agent.status === 'SCANNING' && (
                      <motion.span
                        className="w-1.5 h-1.5 rounded-full bg-obsidian-teal"
                        animate={{ scale: [1, 1.5, 1] }}
                        transition={{ duration: 0.8, repeat: Infinity }}
                      />
                    )}
                    {agent.status}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Quick Actions Footer */}
      <motion.div
        variants={item}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {[
          { label: 'Upload New Report', icon: FileText, cmd: 'upload', color: 'obsidian-teal' },
          { label: 'Register Vendor', icon: Building2, cmd: 'register', color: 'obsidian-blue' },
          { label: 'Execute AI Query', icon: Search, cmd: 'query', color: 'obsidian-gold' }
        ].map((action, i) => (
          <MagneticButton
            key={i}
            onClick={() => handleQuickAction(action.cmd)}
            className="glass-panel-liquid group flex items-center justify-between p-6 rounded-2xl hover:border-obsidian-teal/30 transition-all duration-300 w-full relative overflow-hidden"
          >
            {/* Hover gradient */}
            <div className={`absolute inset-0 bg-gradient-to-r from-${action.color}/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

            <span className="text-sm font-medium text-slate-400 group-hover:text-white transition-colors relative z-10">{action.label}</span>
            <motion.div
              className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center group-hover:bg-obsidian-teal/20 transition-colors relative z-10"
              whileHover={{ scale: 1.15, rotate: 5 }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              <action.icon className="h-5 w-5 text-slate-500 group-hover:text-obsidian-teal transition-colors" />
            </motion.div>
          </MagneticButton>
        ))}
      </motion.div>

      {/* Version watermark */}
      <motion.div
        className="text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2.5 }}
      >
        <span className="text-[10px] font-mono text-white/10 tracking-widest uppercase">
          VendorAuditAI Enterprise Risk Platform
        </span>
      </motion.div>
    </motion.div>
  );
}
