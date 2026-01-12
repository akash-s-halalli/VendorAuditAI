import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Cpu, Shield, Zap, Activity, Terminal, Eye, FileText, Play, Loader2, RefreshCw, AlertCircle } from 'lucide-react';
import { Badge, Button, Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui';
import apiClient, { getApiErrorMessage } from '@/lib/api';

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

const agentColors: Record<string, string> = {
  threat_detection: 'text-primary',
  risk_assessment: 'text-yellow-400',
  vulnerability_scanner: 'text-red-400',
  compliance_verification: 'text-purple-400',
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

  // Run task mutation
  const runTaskMutation = useMutation({
    mutationFn: async ({ agentId, taskType }: { agentId: string; taskType: string }) => {
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
    },
  });

  const agents: Agent[] = agentsResponse?.data || [];
  const logs: AgentLog[] = logsResponse?.data || [];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-400 bg-green-500/10 shadow-[0_0_10px_rgba(34,197,94,0.2)]';
      case 'processing':
        return 'text-yellow-400 bg-yellow-500/10';
      case 'idle':
        return 'text-gray-400 bg-gray-500/10';
      case 'error':
        return 'text-red-400 bg-red-500/10';
      case 'disabled':
        return 'text-gray-600 bg-gray-800/50';
      default:
        return 'text-gray-400 bg-gray-500/10';
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
      <div className="space-y-8 pb-8 animate-in fade-in duration-500">
        <div className="flex items-center justify-center h-[60vh]">
          <div className="text-center">
            <Loader2 className="h-12 w-12 text-primary animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Initializing agent network...</p>
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="space-y-8 pb-8 animate-in fade-in duration-500">
        <div className="flex items-center justify-center h-[60vh]">
          <div className="text-center glass-card p-8 rounded-xl">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Network Error</h3>
            <p className="text-muted-foreground mb-4">{getApiErrorMessage(error)}</p>
            <Button onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry Connection
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-white neon-text flex items-center gap-3">
            <Cpu className="h-10 w-10 text-primary animate-pulse" />
            AI Agent Network
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            Autonomous agents managing your third-party risk ecosystem.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-panel border-green-500/20 shadow-[0_0_15px_rgba(34,197,94,0.2)]">
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_green]" />
            <span className="text-xs font-mono text-green-400 tracking-wider">NETWORK STABLE</span>
          </div>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {agents.map((agent) => {
          const Icon = agentIcons[agent.agent_type] || Shield;
          const color = agentColors[agent.agent_type] || 'text-primary';

          return (
            <div
              key={agent.id}
              className="glass-card rounded-xl border-white/5 overflow-hidden flex flex-col group hover:border-primary/30 transition-all duration-300 hover:shadow-2xl hover:shadow-primary/5"
            >
              {/* Header */}
              <div className="p-6 border-b border-white/5 bg-white/5 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-lg bg-black/40 ${color} shadow-lg ring-1 ring-white/5`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-white group-hover:text-primary transition-colors tracking-tight">
                      {agent.name}
                    </h3>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono">
                      {agent.role}
                    </p>
                  </div>
                </div>
                <Badge
                  variant="outline"
                  className={`glass-panel border-0 uppercase font-mono ${getStatusBadge(agent.status)}`}
                >
                  {agent.status}
                </Badge>
              </div>

              {/* Body */}
              <div className="p-6 space-y-6 flex-1 bg-black/20">
                <p className="text-sm text-gray-400 leading-relaxed font-medium">
                  {agent.description}
                </p>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 rounded-lg bg-black/40 border border-white/5 group-hover:border-white/10 transition-colors">
                    <p className="text-xs text-muted-foreground mb-1 uppercase tracking-wider">Uptime</p>
                    <p className="text-sm font-mono text-white font-bold">
                      {agent.uptime_percentage.toFixed(2)}%
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-black/40 border border-white/5 group-hover:border-white/10 transition-colors">
                    <p className="text-xs text-muted-foreground mb-1 uppercase tracking-wider">Last Run</p>
                    <p className="text-sm font-mono text-white font-bold">
                      {agent.last_run_at
                        ? new Date(agent.last_run_at).toLocaleTimeString()
                        : 'Never'}
                    </p>
                  </div>
                </div>

                {/* Error message if any */}
                {agent.error_message && (
                  <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3">
                    <p className="text-xs text-red-400 font-mono">{agent.error_message}</p>
                  </div>
                )}

                {/* Configuration Preview */}
                <div className="rounded-lg bg-black border border-white/10 p-4 font-mono text-xs space-y-2 h-24 overflow-hidden relative shadow-inner">
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/80 pointer-events-none" />
                  <div className="absolute top-0 right-0 p-2 opacity-50">
                    <Terminal className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="text-gray-500">
                    <span className="text-primary">{'>'}</span> scan_frequency:{' '}
                    <span className="text-green-400">{String(agent.configuration.scan_frequency || 'daily')}</span>
                  </div>
                  <div className="text-gray-500">
                    <span className="text-primary">{'>'}</span> notification:{' '}
                    <span className="text-green-400">
                      {agent.configuration.notification_enabled ? 'enabled' : 'disabled'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-primary/50">
                    <span className="animate-bounce">_</span>
                  </div>
                </div>
              </div>

              {/* Footer Actions */}
              <div className="px-6 py-4 border-t border-white/5 bg-white/5 flex items-center justify-between group-hover:bg-white/10 transition-colors">
                <button
                  className="text-xs uppercase tracking-wider font-bold text-muted-foreground hover:text-white transition-colors"
                  onClick={() => handleViewLogs(agent)}
                >
                  View Logs
                </button>
                <button
                  className="text-xs uppercase tracking-wider font-bold text-primary hover:text-white transition-colors flex items-center gap-2 disabled:opacity-50"
                  onClick={() => handleRunTask(agent)}
                  disabled={runTaskMutation.isPending || agent.status === 'disabled'}
                >
                  {runTaskMutation.isPending && runTaskMutation.variables?.agentId === agent.id ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Play className="h-3 w-3" />
                  )}
                  Run Task
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Logs Modal */}
      <Dialog open={showLogsModal} onOpenChange={setShowLogsModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Terminal className="h-5 w-5 text-primary" />
              {selectedAgent?.name} - Logs
            </DialogTitle>
            <DialogDescription>Recent activity logs for this agent</DialogDescription>
          </DialogHeader>
          <div className="flex-1 overflow-y-auto bg-black/50 rounded-lg p-4 font-mono text-xs space-y-2 min-h-[300px]">
            {logsLoading ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="h-6 w-6 text-primary animate-spin" />
              </div>
            ) : logs.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                No logs available yet. Run a task to generate logs.
              </div>
            ) : (
              logs.map((log) => (
                <div key={log.id} className="flex items-start gap-3 py-1 border-b border-white/5">
                  <span className="text-gray-600 whitespace-nowrap">
                    {new Date(log.created_at).toLocaleTimeString()}
                  </span>
                  <span className={`uppercase w-16 ${getLogLevelColor(log.level)}`}>[{log.level}]</span>
                  <span className="text-gray-300 flex-1">{log.message}</span>
                </div>
              ))
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Task Result Modal */}
      <Dialog open={showTaskResultModal} onOpenChange={setShowTaskResultModal}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-primary" />
              Task Completed
            </DialogTitle>
            <DialogDescription>Task execution results</DialogDescription>
          </DialogHeader>
          {lastTaskResult && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-black/40 border border-white/10">
                  <p className="text-xs text-muted-foreground mb-1">Status</p>
                  <p className="text-sm font-mono text-green-400 uppercase">{lastTaskResult.status}</p>
                </div>
                <div className="p-3 rounded-lg bg-black/40 border border-white/10">
                  <p className="text-xs text-muted-foreground mb-1">Task Type</p>
                  <p className="text-sm font-mono text-white uppercase">{lastTaskResult.task_type}</p>
                </div>
                <div className="p-3 rounded-lg bg-black/40 border border-white/10">
                  <p className="text-xs text-muted-foreground mb-1">Items Processed</p>
                  <p className="text-sm font-mono text-white">{lastTaskResult.items_processed || 0}</p>
                </div>
                <div className="p-3 rounded-lg bg-black/40 border border-white/10">
                  <p className="text-xs text-muted-foreground mb-1">Findings</p>
                  <p className="text-sm font-mono text-white">{lastTaskResult.findings_count || 0}</p>
                </div>
              </div>
              {lastTaskResult.output_data && (
                <div className="rounded-lg bg-black/50 p-4 font-mono text-xs overflow-auto max-h-60">
                  <pre className="text-gray-300">
                    {JSON.stringify(lastTaskResult.output_data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
