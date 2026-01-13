import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Cpu, Shield, Zap, Activity, Terminal, Eye, FileText, Play, Loader2, RefreshCw, AlertCircle, Sparkles, Radio } from 'lucide-react';
import { motion } from 'framer-motion';
import { Badge, Button, Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui';
import apiClient, { getApiErrorMessage } from '@/lib/api';

// Animation variants
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const item = {
  hidden: { y: 20, opacity: 0 },
  show: { y: 0, opacity: 1 }
};

interface Agent {
  id: string;
  name: string;
  agent_type: string;
  role: string;
  description: string;
  status: string;
  uptime_percentage: number;
  last_run_at: string | null;
  error_message: string | null;
  configuration: Record<string, unknown>;
  created_at: string;
}

interface AgentLog {
  id: string;
  agent_id: string;
  task_id: string | null;
  level: string;
  message: string;
  details: Record<string, unknown> | null;
  created_at: string;
}

interface AgentTask {
  id: string;
  agent_id: string;
  task_type: string;
  status: string;
  input_data: Record<string, unknown>;
  output_data: Record<string, unknown> | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  items_processed: number | null;
  findings_count: number | null;
  created_at: string;
}

const agentIcons: Record<string, typeof Shield> = {
  threat_detection: Shield,
  risk_assessment: Activity,
  vulnerability_scanner: Eye,
  compliance_verification: FileText,
};

const agentColors: Record<string, { text: string; glow: string; bg: string }> = {
  threat_detection: { text: 'text-obsidian-teal', glow: 'glow-teal', bg: 'bg-obsidian-teal' },
  risk_assessment: { text: 'text-obsidian-gold', glow: 'glow-gold', bg: 'bg-obsidian-gold' },
  vulnerability_scanner: { text: 'text-obsidian-crimson', glow: 'glow-crimson', bg: 'bg-obsidian-crimson' },
  compliance_verification: { text: 'text-obsidian-blue', glow: 'glow-blue', bg: 'bg-obsidian-blue' },
};

export function Agents() {
  const queryClient = useQueryClient();
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [showLogsModal, setShowLogsModal] = useState(false);
  const [showTaskResultModal, setShowTaskResultModal] = useState(false);
  const [lastTaskResult, setLastTaskResult] = useState<AgentTask | null>(null);

  // Fetch agents from API
  const { data: agentsResponse, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await apiClient.get('/agents');
      return response.data;
    },
  });

  // Fetch logs for selected agent
  const { data: logsResponse, isLoading: logsLoading } = useQuery({
    queryKey: ['agent-logs', selectedAgent?.id],
    queryFn: async () => {
      if (!selectedAgent) return null;
      const response = await apiClient.get(`/agents/${selectedAgent.id}/logs?limit=50`);
      return response.data;
    },
    enabled: !!selectedAgent && showLogsModal,
  });

  // Run task mutation - error state for UI feedback
  const [runningAgentId, setRunningAgentId] = useState<string | null>(null);
  const [_runTaskError, setRunTaskError] = useState<string | null>(null);
  void _runTaskError; // Used for error display
  const runTaskMutation = useMutation({
    mutationFn: async ({ agentId, taskType }: { agentId: string; taskType: string }) => {
      setRunningAgentId(agentId);
      const response = await apiClient.post(`/agents/${agentId}/tasks`, {
        task_type: taskType,
        input_data: {},
      });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      setLastTaskResult(data);
      setShowTaskResultModal(true);
      setRunningAgentId(null);
      setRunTaskError(null);
    },
    onError: (error) => {
      setRunTaskError(getApiErrorMessage(error));
      setRunningAgentId(null);
    },
  });

  const agents: Agent[] = agentsResponse?.data || [];
  const logs: AgentLog[] = logsResponse?.data || [];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return { class: 'text-obsidian-emerald bg-obsidian-emerald/10 glow-emerald', pulse: true };
      case 'processing':
        return { class: 'text-obsidian-gold bg-obsidian-gold/10 glow-gold', pulse: true };
      case 'idle':
        return { class: 'text-slate-400 bg-slate-500/10', pulse: false };
      case 'error':
        return { class: 'text-obsidian-crimson bg-obsidian-crimson/10 glow-crimson', pulse: true };
      case 'disabled':
        return { class: 'text-slate-600 bg-slate-800/50', pulse: false };
      default:
        return { class: 'text-slate-400 bg-slate-500/10', pulse: false };
    }
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-red-400';
      case 'warning':
        return 'text-yellow-400';
      case 'info':
        return 'text-blue-400';
      case 'debug':
        return 'text-gray-500';
      default:
        return 'text-gray-400';
    }
  };

  const handleViewLogs = (agent: Agent) => {
    setSelectedAgent(agent);
    setShowLogsModal(true);
  };

  const handleRunTask = (agent: Agent) => {
    // Determine task type based on agent type
    const taskTypeMap: Record<string, string> = {
      threat_detection: 'scan',
      risk_assessment: 'analyze',
      vulnerability_scanner: 'scan',
      compliance_verification: 'audit',
    };
    const taskType = taskTypeMap[agent.agent_type] || 'scan';
    runTaskMutation.mutate({ agentId: agent.id, taskType });
  };

  if (isLoading) {
    return (
      <div className="space-y-8 pb-8">
        <div className="flex items-center justify-center h-[60vh]">
          <motion.div
            className="text-center glass-panel-liquid p-12 rounded-3xl"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            >
              <Cpu className="h-16 w-16 text-obsidian-teal mx-auto mb-6 drop-shadow-[0_0_20px_rgba(0,212,170,0.5)]" />
            </motion.div>
            <p className="text-muted-foreground font-mono tracking-wider">INITIALIZING NEURAL NETWORK...</p>
            <div className="mt-4 flex justify-center gap-1">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-2 h-2 rounded-full bg-obsidian-teal"
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, delay: i * 0.2, repeat: Infinity }}
                />
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="space-y-8 pb-8">
        <div className="flex items-center justify-center h-[60vh]">
          <motion.div
            className="text-center glass-card-crimson p-12 rounded-3xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <AlertCircle className="h-16 w-16 text-obsidian-crimson mx-auto mb-6 drop-shadow-[0_0_20px_rgba(230,57,70,0.5)]" />
            <h3 className="text-2xl font-bold text-white mb-2 font-heading">Network Error</h3>
            <p className="text-muted-foreground mb-6">{getApiErrorMessage(error)}</p>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button onClick={() => refetch()} className="glow-teal">
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry Connection
              </Button>
            </motion.div>
          </motion.div>
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
      {/* Header */}
      <motion.div variants={item} className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-5xl font-bold tracking-tight text-white font-heading flex items-center gap-4">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <Cpu className="h-12 w-12 text-obsidian-teal drop-shadow-[0_0_15px_rgba(0,212,170,0.5)]" />
            </motion.div>
            <span>Neural <span className="text-obsidian-teal">Network</span></span>
          </h1>
          <p className="text-muted-foreground mt-3 text-lg flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-obsidian-teal" />
            Autonomous agents managing your third-party risk ecosystem.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button variant="outline" size="sm" onClick={() => refetch()} className="glass-panel-liquid border-white/10">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </motion.div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-panel-liquid border-obsidian-emerald/20 glow-emerald">
            <motion.div
              className="h-2 w-2 rounded-full bg-obsidian-emerald"
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
            <span className="text-xs font-mono text-obsidian-emerald tracking-wider">NETWORK STABLE</span>
          </div>
        </div>
      </motion.div>

      {/* Network Stats Bar */}
      <motion.div variants={item} className="grid grid-cols-4 gap-4">
        {[
          { label: 'Active Agents', value: agents.filter(a => a.status === 'active').length, total: agents.length, color: 'obsidian-emerald' },
          { label: 'Processing', value: agents.filter(a => a.status === 'processing').length, color: 'obsidian-gold' },
          { label: 'Avg Uptime', value: `${(agents.reduce((acc, a) => acc + a.uptime_percentage, 0) / agents.length || 0).toFixed(1)}%`, color: 'obsidian-teal' },
          { label: 'Error Rate', value: `${(agents.filter(a => a.status === 'error').length / agents.length * 100 || 0).toFixed(1)}%`, color: 'obsidian-crimson' }
        ].map((stat, idx) => (
          <motion.div
            key={stat.label}
            className="glass-panel-liquid rounded-2xl p-4 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + idx * 0.1 }}
          >
            <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">{stat.label}</p>
            <p className={`text-2xl font-bold font-mono text-${stat.color}`}>
              {typeof stat.value === 'number' ? stat.value : stat.value}
              {stat.total !== undefined && <span className="text-sm text-muted-foreground">/{stat.total}</span>}
            </p>
          </motion.div>
        ))}
      </motion.div>

      {/* Agents Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {agents.map((agent, idx) => {
          const Icon = agentIcons[agent.agent_type] || Shield;
          const colorConfig = agentColors[agent.agent_type] || { text: 'text-obsidian-teal', glow: 'glow-teal', bg: 'bg-obsidian-teal' };
          const statusConfig = getStatusBadge(agent.status);

          return (
            <motion.div
              key={agent.id}
              variants={item}
              whileHover={{ y: -4 }}
              className={`glass-panel-liquid rounded-3xl border-white/5 overflow-hidden flex flex-col group hover:border-obsidian-teal/30 transition-all duration-500 hover:${colorConfig.glow}`}
            >
              {/* Header */}
              <div className="p-6 border-b border-white/5 bg-white/[0.03] flex items-center justify-between relative overflow-hidden">
                {/* Background glow */}
                <div className={`absolute -left-10 -top-10 w-32 h-32 ${colorConfig.bg}/10 rounded-full blur-2xl group-hover:${colorConfig.bg}/20 transition-all duration-500`} />

                <div className="flex items-center gap-4 relative z-10">
                  <motion.div
                    className={`p-3 rounded-xl bg-black/40 ${colorConfig.text} shadow-lg ring-1 ring-white/10 ${colorConfig.glow}`}
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 400 }}
                  >
                    <Icon className="h-6 w-6" />
                  </motion.div>
                  <div>
                    <h3 className={`font-bold text-lg text-white group-hover:${colorConfig.text} transition-colors tracking-tight font-heading`}>
                      {agent.name}
                    </h3>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono">
                      {agent.role}
                    </p>
                  </div>
                </div>
                <Badge
                  variant="outline"
                  className={`glass-panel-liquid border-0 uppercase font-mono ${statusConfig.class} flex items-center gap-2`}
                >
                  {statusConfig.pulse && (
                    <motion.span
                      className="w-1.5 h-1.5 rounded-full bg-current"
                      animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    />
                  )}
                  {agent.status}
                </Badge>
              </div>

              {/* Body */}
              <div className="p-6 space-y-6 flex-1 bg-black/20">
                <p className="text-sm text-slate-400 leading-relaxed">
                  {agent.description}
                </p>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-black/40 border border-white/5 group-hover:border-white/10 transition-colors">
                    <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wider flex items-center gap-2">
                      <Radio className="h-3 w-3" />
                      Uptime
                    </p>
                    <p className={`text-xl font-mono ${colorConfig.text} font-bold`}>
                      {agent.uptime_percentage.toFixed(1)}%
                    </p>
                  </div>
                  <div className="p-4 rounded-xl bg-black/40 border border-white/5 group-hover:border-white/10 transition-colors">
                    <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wider flex items-center gap-2">
                      <Activity className="h-3 w-3" />
                      Last Run
                    </p>
                    <p className="text-sm font-mono text-white font-bold">
                      {agent.last_run_at
                        ? new Date(agent.last_run_at).toLocaleTimeString()
                        : 'Never'}
                    </p>
                  </div>
                </div>

                {/* Error message if any */}
                {agent.error_message && (
                  <motion.div
                    className="rounded-xl bg-obsidian-crimson/10 border border-obsidian-crimson/20 p-4"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                  >
                    <p className="text-xs text-obsidian-crimson font-mono flex items-center gap-2">
                      <AlertCircle className="h-4 w-4" />
                      {agent.error_message}
                    </p>
                  </motion.div>
                )}

                {/* Configuration Preview */}
                <div className="rounded-xl bg-black/60 border border-white/10 p-4 font-mono text-xs space-y-2 h-28 overflow-hidden relative">
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/90 pointer-events-none" />
                  <div className="absolute top-0 right-0 p-3 opacity-50">
                    <Terminal className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <motion.div
                    className="text-slate-500"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + idx * 0.1 }}
                  >
                    <span className={colorConfig.text}>{'>'}</span> scan_frequency:{' '}
                    <span className="text-obsidian-emerald">{String(agent.configuration.scan_frequency || 'daily')}</span>
                  </motion.div>
                  <motion.div
                    className="text-slate-500"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + idx * 0.1 }}
                  >
                    <span className={colorConfig.text}>{'>'}</span> notification:{' '}
                    <span className="text-obsidian-emerald">
                      {agent.configuration.notification_enabled ? 'enabled' : 'disabled'}
                    </span>
                  </motion.div>
                  <div className="flex items-center gap-1 text-obsidian-teal/50 mt-2">
                    <motion.span
                      animate={{ opacity: [1, 0, 1] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    >
                      _
                    </motion.span>
                  </div>
                </div>
              </div>

              {/* Footer Actions */}
              <div className="px-6 py-4 border-t border-white/5 bg-white/[0.02] flex items-center justify-between group-hover:bg-white/[0.05] transition-colors">
                <motion.button
                  className="text-xs uppercase tracking-wider font-bold text-muted-foreground hover:text-white transition-colors flex items-center gap-2"
                  onClick={() => handleViewLogs(agent)}
                  whileHover={{ x: 2 }}
                >
                  <Terminal className="h-3 w-3" />
                  View Logs
                </motion.button>
                <motion.button
                  className={`text-xs uppercase tracking-wider font-bold ${colorConfig.text} hover:text-white transition-colors flex items-center gap-2 disabled:opacity-50 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10`}
                  onClick={() => handleRunTask(agent)}
                  disabled={runTaskMutation.isPending || agent.status === 'disabled'}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {runTaskMutation.isPending && runningAgentId === agent.id ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Play className="h-3 w-3" />
                  )}
                  Run Task
                </motion.button>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Logs Modal */}
      <Dialog open={showLogsModal} onOpenChange={setShowLogsModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col glass-panel-liquid border-white/10">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-white font-heading">
              <Terminal className="h-5 w-5 text-obsidian-teal" />
              {selectedAgent?.name} - Activity Logs
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Real-time activity monitoring for this agent
            </DialogDescription>
          </DialogHeader>
          <div className="flex-1 overflow-y-auto bg-black/60 rounded-xl p-4 font-mono text-xs space-y-2 min-h-[300px] border border-white/5 custom-scrollbar">
            {logsLoading ? (
              <div className="flex items-center justify-center h-full">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <Loader2 className="h-8 w-8 text-obsidian-teal" />
                </motion.div>
              </div>
            ) : logs.length === 0 ? (
              <div className="text-center text-muted-foreground py-12">
                <Terminal className="h-12 w-12 mx-auto mb-4 opacity-30" />
                <p>No logs available yet.</p>
                <p className="text-xs mt-2">Run a task to generate activity logs.</p>
              </div>
            ) : (
              logs.map((log, i) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.02 }}
                  className="flex items-start gap-3 py-2 border-b border-white/5 hover:bg-white/5 transition-colors rounded px-2"
                >
                  <span className="text-slate-600 whitespace-nowrap">
                    {new Date(log.created_at).toLocaleTimeString()}
                  </span>
                  <span className={`uppercase w-16 font-bold ${getLogLevelColor(log.level)}`}>[{log.level}]</span>
                  <span className="text-slate-300 flex-1">{log.message}</span>
                </motion.div>
              ))
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Task Result Modal */}
      <Dialog open={showTaskResultModal} onOpenChange={setShowTaskResultModal}>
        <DialogContent className="max-w-xl glass-panel-liquid border-white/10">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-white font-heading">
              <Zap className="h-5 w-5 text-obsidian-gold drop-shadow-[0_0_10px_rgba(255,184,0,0.5)]" />
              Task Completed
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Execution results and findings summary
            </DialogDescription>
          </DialogHeader>
          {lastTaskResult && (
            <motion.div
              className="space-y-4"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-black/40 border border-white/10">
                  <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wider">Status</p>
                  <p className="text-lg font-mono text-obsidian-emerald uppercase font-bold glow-emerald">{lastTaskResult.status}</p>
                </div>
                <div className="p-4 rounded-xl bg-black/40 border border-white/10">
                  <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wider">Task Type</p>
                  <p className="text-lg font-mono text-white uppercase font-bold">{lastTaskResult.task_type}</p>
                </div>
                <div className="p-4 rounded-xl bg-black/40 border border-white/10">
                  <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wider">Items Processed</p>
                  <p className="text-2xl font-mono text-obsidian-teal font-bold">{lastTaskResult.items_processed || 0}</p>
                </div>
                <div className="p-4 rounded-xl bg-black/40 border border-white/10">
                  <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wider">Findings</p>
                  <p className="text-2xl font-mono text-obsidian-gold font-bold">{lastTaskResult.findings_count || 0}</p>
                </div>
              </div>
              {lastTaskResult.output_data && (
                <div className="rounded-xl bg-black/60 p-4 font-mono text-xs overflow-auto max-h-60 border border-white/10 custom-scrollbar">
                  <pre className="text-slate-300">
                    {JSON.stringify(lastTaskResult.output_data, null, 2)}
                  </pre>
                </div>
              )}
            </motion.div>
          )}
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
