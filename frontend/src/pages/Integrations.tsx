import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Link2,
  Settings,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Plus,
  Trash2,
  Copy,
  ExternalLink,
  Clock,
  Activity,
  Mail,
  MessageSquare,
  Webhook,
  Bug,
  Loader2,
  X,
  Eye,
  EyeOff,
  Play,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  Button,
  Input,
  Label,
  Badge,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui';
import { CardSkeleton } from '@/components/ui/TypingIndicator';
import { AnimatedCounter } from '@/components/ui/AnimatedCounter';
import apiClient, { getApiErrorMessage } from '@/lib/api';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { type: 'spring' as const, stiffness: 100, damping: 15 },
  },
};

const tabVariants = {
  inactive: { opacity: 0.6 },
  active: { opacity: 1, scale: 1.02 },
};

// Types
type IntegrationType = 'jira' | 'servicenow' | 'slack' | 'teams' | 'email' | 'webhook';
type IntegrationStatus = 'active' | 'inactive' | 'error';

interface Integration {
  id: string;
  name: string;
  type: IntegrationType;
  status: IntegrationStatus;
  config: Record<string, string>;
  last_sync_at?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

interface SyncLog {
  id: string;
  integration_id: string;
  status: 'success' | 'error' | 'partial';
  records_synced: number;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

interface WebhookEndpoint {
  id: string;
  name: string;
  url: string;
  secret: string;
  is_active: boolean;
  trigger_count: number;
  last_triggered_at?: string;
  created_at: string;
}

interface IntegrationStats {
  total_integrations: number;
  active_integrations: number;
  integrations_with_errors: number;
  syncs_last_24h: number;
}

// Configuration forms for each integration type
interface IntegrationConfigField {
  key: string;
  label: string;
  type: 'text' | 'password' | 'url' | 'email';
  placeholder: string;
  required: boolean;
}

const integrationConfigs: Record<IntegrationType, IntegrationConfigField[]> = {
  jira: [
    { key: 'url', label: 'Jira URL', type: 'url', placeholder: 'https://your-domain.atlassian.net', required: true },
    { key: 'email', label: 'Email', type: 'email', placeholder: 'your-email@example.com', required: true },
    { key: 'api_token', label: 'API Token', type: 'password', placeholder: 'Your Jira API token', required: true },
    { key: 'project_key', label: 'Project Key', type: 'text', placeholder: 'e.g., VENDOR', required: true },
  ],
  servicenow: [
    { key: 'instance_url', label: 'Instance URL', type: 'url', placeholder: 'https://your-instance.service-now.com', required: true },
    { key: 'username', label: 'Username', type: 'text', placeholder: 'ServiceNow username', required: true },
    { key: 'password', label: 'Password', type: 'password', placeholder: 'ServiceNow password', required: true },
  ],
  slack: [
    { key: 'webhook_url', label: 'Webhook URL', type: 'url', placeholder: 'https://hooks.slack.com/services/...', required: true },
    { key: 'channel', label: 'Channel', type: 'text', placeholder: '#vendor-alerts', required: false },
  ],
  teams: [
    { key: 'webhook_url', label: 'Webhook URL', type: 'url', placeholder: 'https://outlook.office.com/webhook/...', required: true },
  ],
  email: [
    { key: 'smtp_host', label: 'SMTP Host', type: 'text', placeholder: 'smtp.example.com', required: true },
    { key: 'smtp_port', label: 'SMTP Port', type: 'text', placeholder: '587', required: true },
    { key: 'smtp_username', label: 'Username', type: 'text', placeholder: 'your-email@example.com', required: true },
    { key: 'smtp_password', label: 'Password', type: 'password', placeholder: 'SMTP password', required: true },
    { key: 'from_email', label: 'From Email', type: 'email', placeholder: 'noreply@example.com', required: true },
  ],
  webhook: [],
};

const integrationIcons: Record<IntegrationType, React.ElementType> = {
  jira: Bug,
  servicenow: Settings,
  slack: MessageSquare,
  teams: MessageSquare,
  email: Mail,
  webhook: Webhook,
};

const integrationColors: Record<IntegrationType, { bg: string; text: string; border: string }> = {
  jira: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/30' },
  servicenow: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/30' },
  slack: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/30' },
  teams: { bg: 'bg-blue-600/20', text: 'text-blue-300', border: 'border-blue-600/30' },
  email: { bg: 'bg-gray-500/20', text: 'text-gray-400', border: 'border-gray-500/30' },
  webhook: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/30' },
};

const integrationLabels: Record<IntegrationType, string> = {
  jira: 'Jira',
  servicenow: 'ServiceNow',
  slack: 'Slack',
  teams: 'Microsoft Teams',
  email: 'Email (SMTP)',
  webhook: 'Webhook',
};

const statusColors: Record<IntegrationStatus, string> = {
  active: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  inactive: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  error: 'bg-red-500/20 text-red-400 border-red-500/30',
};

export function Integrations() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'integrations' | 'webhooks'>('integrations');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showWebhookModal, setShowWebhookModal] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState<Integration | null>(null);
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({});

  // Form state for new integration
  const [newIntegration, setNewIntegration] = useState({
    name: '',
    type: 'jira' as IntegrationType,
    config: {} as Record<string, string>,
  });
  const [formError, setFormError] = useState<string | null>(null);

  // Form state for new webhook
  const [newWebhook, setNewWebhook] = useState({
    name: '',
  });

  // Fetch integration stats
  const { data: stats, isLoading: statsLoading } = useQuery<IntegrationStats>({
    queryKey: ['integration-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/integrations/stats');
      return response.data;
    },
  });

  // Fetch integrations
  const { data: integrationsResponse, isLoading: integrationsLoading } = useQuery<{ data: Integration[] }>({
    queryKey: ['integrations'],
    queryFn: async () => {
      const response = await apiClient.get('/integrations/');
      return response.data;
    },
  });

  // Fetch webhooks
  const { data: webhooksResponse, isLoading: webhooksLoading } = useQuery<{ data: WebhookEndpoint[] }>({
    queryKey: ['webhooks'],
    queryFn: async () => {
      const response = await apiClient.get('/integrations/webhooks');
      return response.data;
    },
    enabled: activeTab === 'webhooks',
  });

  // Fetch sync logs for selected integration
  const { data: logsResponse, isLoading: logsLoading } = useQuery<{ data: SyncLog[] }>({
    queryKey: ['integration-logs', selectedIntegration?.id],
    queryFn: async () => {
      const response = await apiClient.get(`/integrations/${selectedIntegration!.id}/logs`);
      return response.data;
    },
    enabled: !!selectedIntegration && showDetailModal,
  });

  // Create integration mutation
  const createIntegrationMutation = useMutation({
    mutationFn: async (data: typeof newIntegration) => {
      const response = await apiClient.post('/integrations/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      queryClient.invalidateQueries({ queryKey: ['integration-stats'] });
      setShowAddModal(false);
      setNewIntegration({ name: '', type: 'jira', config: {} });
      setFormError(null);
    },
    onError: (error) => {
      setFormError(getApiErrorMessage(error));
    },
  });

  // Test integration mutation
  const testIntegrationMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post(`/integrations/${id}/test`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
    },
  });

  // Sync integration mutation
  const syncIntegrationMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post(`/integrations/${id}/sync`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      queryClient.invalidateQueries({ queryKey: ['integration-stats'] });
      queryClient.invalidateQueries({ queryKey: ['integration-logs', selectedIntegration?.id] });
    },
  });

  // Delete integration mutation
  const deleteIntegrationMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/integrations/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      queryClient.invalidateQueries({ queryKey: ['integration-stats'] });
      setShowDetailModal(false);
      setSelectedIntegration(null);
    },
  });

  // Create webhook mutation
  const createWebhookMutation = useMutation({
    mutationFn: async (data: typeof newWebhook) => {
      const response = await apiClient.post('/integrations/webhooks', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
      setShowWebhookModal(false);
      setNewWebhook({ name: '' });
    },
  });

  const handleCreateIntegration = () => {
    if (!newIntegration.name.trim()) {
      setFormError('Integration name is required');
      return;
    }

    // Validate required fields
    const requiredFields = integrationConfigs[newIntegration.type].filter((f) => f.required);
    for (const field of requiredFields) {
      if (!newIntegration.config[field.key]?.trim()) {
        setFormError(`${field.label} is required`);
        return;
      }
    }

    setFormError(null);
    createIntegrationMutation.mutate(newIntegration);
  };

  const handleOpenDetail = (integration: Integration) => {
    setSelectedIntegration(integration);
    setShowDetailModal(true);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const integrations = integrationsResponse?.data || [];
  const webhooks = webhooksResponse?.data || [];
  const logs = logsResponse?.data || [];
  const isLoading = statsLoading || integrationsLoading;

  const dashboardStats = stats || {
    total_integrations: 0,
    active_integrations: 0,
    integrations_with_errors: 0,
    syncs_last_24h: 0,
  };

  return (
    <motion.div
      className="space-y-6"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold neon-text">
            INTEGRATION<span className="text-primary">HUB</span>
          </h1>
          <div className="realtime-pulse flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-500/30">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            <span className="text-xs text-blue-400 font-medium">
              <AnimatedCounter value={dashboardStats.active_integrations} duration={1} /> ACTIVE
            </span>
          </div>
        </div>
        <p className="text-muted-foreground mt-1">
          Connect and manage external system integrations
        </p>
      </motion.div>

      {/* Add Integration Modal */}
      <Dialog open={showAddModal} onOpenChange={setShowAddModal}>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add Integration</DialogTitle>
            <DialogDescription>
              Connect a new external system to VendorAuditAI
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="integration-name">Integration Name *</Label>
              <Input
                id="integration-name"
                placeholder="e.g., Production Jira"
                value={newIntegration.name}
                onChange={(e) => setNewIntegration({ ...newIntegration, name: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="integration-type">Integration Type</Label>
              <select
                id="integration-type"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={newIntegration.type}
                onChange={(e) => setNewIntegration({
                  ...newIntegration,
                  type: e.target.value as IntegrationType,
                  config: {},
                })}
              >
                {Object.entries(integrationLabels).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </select>
            </div>

            {/* Integration Type Preview */}
            <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 border">
              {(() => {
                const Icon = integrationIcons[newIntegration.type];
                const colors = integrationColors[newIntegration.type];
                return (
                  <>
                    <div className={cn('p-2 rounded-lg', colors.bg, colors.border, 'border')}>
                      <Icon className={cn('h-5 w-5', colors.text)} />
                    </div>
                    <div>
                      <p className="font-medium">{integrationLabels[newIntegration.type]}</p>
                      <p className="text-xs text-muted-foreground">
                        {newIntegration.type === 'webhook'
                          ? 'Generate webhook endpoint for external systems'
                          : `Configure ${integrationLabels[newIntegration.type]} connection`
                        }
                      </p>
                    </div>
                  </>
                );
              })()}
            </div>

            {/* Dynamic Configuration Fields */}
            {newIntegration.type !== 'webhook' && integrationConfigs[newIntegration.type].map((field) => (
              <div key={field.key} className="grid gap-2">
                <Label htmlFor={field.key}>
                  {field.label} {field.required && '*'}
                </Label>
                <div className="relative">
                  <Input
                    id={field.key}
                    type={field.type === 'password' && !showPasswords[field.key] ? 'password' : 'text'}
                    placeholder={field.placeholder}
                    value={newIntegration.config[field.key] || ''}
                    onChange={(e) => setNewIntegration({
                      ...newIntegration,
                      config: { ...newIntegration.config, [field.key]: e.target.value },
                    })}
                  />
                  {field.type === 'password' && (
                    <button
                      type="button"
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      onClick={() => setShowPasswords({ ...showPasswords, [field.key]: !showPasswords[field.key] })}
                    >
                      {showPasswords[field.key] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  )}
                </div>
              </div>
            ))}

            {newIntegration.type === 'webhook' && (
              <div className="p-4 rounded-lg bg-muted/50 border">
                <p className="text-sm text-muted-foreground">
                  A unique webhook endpoint URL will be generated after creation. You can configure which events trigger this webhook.
                </p>
              </div>
            )}

            {formError && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {formError}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddModal(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleCreateIntegration}
              disabled={createIntegrationMutation.isPending}
            >
              {createIntegrationMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              <Plus className="mr-2 h-4 w-4" />
              Add Integration
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Integration Detail Modal */}
      <Dialog open={showDetailModal} onOpenChange={setShowDetailModal}>
        <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-center gap-3">
              {selectedIntegration && (() => {
                const Icon = integrationIcons[selectedIntegration.type];
                const colors = integrationColors[selectedIntegration.type];
                return (
                  <div className={cn('p-2 rounded-lg', colors.bg, colors.border, 'border')}>
                    <Icon className={cn('h-5 w-5', colors.text)} />
                  </div>
                );
              })()}
              <div>
                <DialogTitle>{selectedIntegration?.name}</DialogTitle>
                <DialogDescription>
                  {selectedIntegration && integrationLabels[selectedIntegration.type]} Integration
                </DialogDescription>
              </div>
            </div>
          </DialogHeader>

          {selectedIntegration && (
            <div className="space-y-6 py-4">
              {/* Status and Actions */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className={statusColors[selectedIntegration.status]}>
                    {selectedIntegration.status.toUpperCase()}
                  </Badge>
                  {selectedIntegration.last_sync_at && (
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      Last sync: {new Date(selectedIntegration.last_sync_at).toLocaleString()}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => testIntegrationMutation.mutate(selectedIntegration.id)}
                    disabled={testIntegrationMutation.isPending}
                  >
                    {testIntegrationMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-1" />
                        Test
                      </>
                    )}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => syncIntegrationMutation.mutate(selectedIntegration.id)}
                    disabled={syncIntegrationMutation.isPending}
                  >
                    {syncIntegrationMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <RefreshCw className="h-4 w-4 mr-1" />
                        Sync
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {/* Error Message */}
              {selectedIntegration.error_message && (
                <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
                  <span>{selectedIntegration.error_message}</span>
                </div>
              )}

              {/* Configuration Summary */}
              <div>
                <h4 className="text-sm font-medium mb-3">Configuration</h4>
                <div className="rounded-lg border bg-muted/50 p-4 space-y-2">
                  {Object.entries(selectedIntegration.config).map(([key, value]) => {
                    const isSecret = key.toLowerCase().includes('password') ||
                                     key.toLowerCase().includes('token') ||
                                     key.toLowerCase().includes('secret');
                    return (
                      <div key={key} className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground capitalize">
                          {key.replace(/_/g, ' ')}
                        </span>
                        <span className="font-mono text-xs">
                          {isSecret ? '********' : value}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Sync Logs */}
              <div>
                <h4 className="text-sm font-medium mb-3">Sync Logs</h4>
                {logsLoading ? (
                  <CardSkeleton />
                ) : logs.length === 0 ? (
                  <div className="rounded-lg border bg-card p-6 text-center">
                    <Activity className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">No sync logs yet</p>
                  </div>
                ) : (
                  <div className="rounded-lg border bg-card overflow-hidden">
                    <table className="w-full text-sm">
                      <thead className="bg-muted/50">
                        <tr>
                          <th className="px-4 py-2 text-left font-medium">Status</th>
                          <th className="px-4 py-2 text-left font-medium">Records</th>
                          <th className="px-4 py-2 text-left font-medium">Started</th>
                          <th className="px-4 py-2 text-left font-medium">Duration</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {logs.slice(0, 10).map((log) => (
                          <tr key={log.id} className="hover:bg-muted/30">
                            <td className="px-4 py-2">
                              <Badge
                                variant="outline"
                                className={cn(
                                  log.status === 'success' && 'bg-emerald-500/20 text-emerald-400',
                                  log.status === 'error' && 'bg-red-500/20 text-red-400',
                                  log.status === 'partial' && 'bg-yellow-500/20 text-yellow-400'
                                )}
                              >
                                {log.status}
                              </Badge>
                            </td>
                            <td className="px-4 py-2">{log.records_synced}</td>
                            <td className="px-4 py-2 text-muted-foreground">
                              {new Date(log.started_at).toLocaleString()}
                            </td>
                            <td className="px-4 py-2 text-muted-foreground">
                              {log.completed_at
                                ? `${Math.round((new Date(log.completed_at).getTime() - new Date(log.started_at).getTime()) / 1000)}s`
                                : 'Running...'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="destructive"
              onClick={() => selectedIntegration && deleteIntegrationMutation.mutate(selectedIntegration.id)}
              disabled={deleteIntegrationMutation.isPending}
            >
              {deleteIntegrationMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </>
              )}
            </Button>
            <Button variant="outline" onClick={() => setShowDetailModal(false)}>
              <X className="h-4 w-4 mr-2" />
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Webhook Modal */}
      <Dialog open={showWebhookModal} onOpenChange={setShowWebhookModal}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create Webhook Endpoint</DialogTitle>
            <DialogDescription>
              Generate a new webhook endpoint for external systems
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="webhook-name">Webhook Name *</Label>
              <Input
                id="webhook-name"
                placeholder="e.g., CI/CD Pipeline"
                value={newWebhook.name}
                onChange={(e) => setNewWebhook({ ...newWebhook, name: e.target.value })}
              />
            </div>
            <div className="p-4 rounded-lg bg-muted/50 border">
              <p className="text-sm text-muted-foreground">
                A unique URL and secret will be generated. Use this endpoint to receive events from external systems.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowWebhookModal(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => createWebhookMutation.mutate(newWebhook)}
              disabled={createWebhookMutation.isPending || !newWebhook.name.trim()}
            >
              {createWebhookMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              <Plus className="mr-2 h-4 w-4" />
              Create Webhook
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Stats Cards */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total Integrations"
          value={dashboardStats.total_integrations}
          icon={Link2}
          className="border-l-4 border-l-blue-500"
          isLoading={isLoading}
        />
        <StatCard
          title="Active"
          value={dashboardStats.active_integrations}
          icon={CheckCircle}
          className="border-l-4 border-l-emerald-500"
          isLoading={isLoading}
        />
        <StatCard
          title="With Errors"
          value={dashboardStats.integrations_with_errors}
          icon={AlertTriangle}
          className="border-l-4 border-l-red-500"
          isLoading={isLoading}
        />
        <StatCard
          title="Last 24h Syncs"
          value={dashboardStats.syncs_last_24h}
          icon={RefreshCw}
          className="border-l-4 border-l-purple-500"
          isLoading={isLoading}
        />
      </motion.div>

      {/* Tabs */}
      <motion.div variants={itemVariants} className="border-b">
        <nav className="-mb-px flex gap-4">
          {(['integrations', 'webhooks'] as const).map((tab) => (
            <motion.button
              key={tab}
              onClick={() => setActiveTab(tab)}
              variants={tabVariants}
              animate={activeTab === tab ? 'active' : 'inactive'}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                'relative border-b-2 px-4 py-2 text-sm font-medium transition-colors',
                activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              {activeTab === tab && (
                <motion.div
                  layoutId="integration-tab-indicator"
                  className="absolute inset-0 bg-primary/10 rounded-t-lg"
                  initial={false}
                  transition={{ type: 'spring' as const, stiffness: 300, damping: 30 }}
                />
              )}
              <span className="relative z-10 capitalize">{tab}</span>
            </motion.button>
          ))}
        </nav>
      </motion.div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'integrations' && (
          <motion.div
            key="integrations"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <IntegrationsTab
              integrations={integrations}
              isLoading={integrationsLoading}
              onAddIntegration={() => setShowAddModal(true)}
              onOpenDetail={handleOpenDetail}
              onTest={(id) => testIntegrationMutation.mutate(id)}
              onSync={(id) => syncIntegrationMutation.mutate(id)}
              testingId={testIntegrationMutation.isPending ? testIntegrationMutation.variables : undefined}
              syncingId={syncIntegrationMutation.isPending ? syncIntegrationMutation.variables : undefined}
            />
          </motion.div>
        )}
        {activeTab === 'webhooks' && (
          <motion.div
            key="webhooks"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <WebhooksTab
              webhooks={webhooks}
              isLoading={webhooksLoading}
              onCreateWebhook={() => setShowWebhookModal(true)}
              onCopyUrl={copyToClipboard}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// Integrations Tab Component
function IntegrationsTab({
  integrations,
  isLoading,
  onAddIntegration,
  onOpenDetail,
  onTest,
  onSync,
  testingId,
  syncingId,
}: {
  integrations: Integration[];
  isLoading: boolean;
  onAddIntegration: () => void;
  onOpenDetail: (integration: Integration) => void;
  onTest: (id: string) => void;
  onSync: (id: string) => void;
  testingId?: string;
  syncingId?: string;
}) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={onAddIntegration}>
          <Plus className="h-4 w-4 mr-2" />
          Add Integration
        </Button>
      </div>

      {integrations.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center py-12 rounded-lg border bg-card glass-panel-liquid"
        >
          <Link2 className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No integrations yet</h3>
          <p className="text-muted-foreground text-center mb-4">
            Connect external systems to sync data and receive notifications.
          </p>
          <Button onClick={onAddIntegration}>
            <Plus className="h-4 w-4 mr-2" />
            Add Your First Integration
          </Button>
        </motion.div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <AnimatePresence mode="popLayout">
            {integrations.map((integration, index) => (
              <IntegrationCard
                key={integration.id}
                integration={integration}
                index={index}
                onOpenDetail={() => onOpenDetail(integration)}
                onTest={() => onTest(integration.id)}
                onSync={() => onSync(integration.id)}
                isTesting={testingId === integration.id}
                isSyncing={syncingId === integration.id}
              />
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}

// Integration Card Component
function IntegrationCard({
  integration,
  index,
  onOpenDetail,
  onTest,
  onSync,
  isTesting,
  isSyncing,
}: {
  integration: Integration;
  index: number;
  onOpenDetail: () => void;
  onTest: () => void;
  onSync: () => void;
  isTesting: boolean;
  isSyncing: boolean;
}) {
  const Icon = integrationIcons[integration.type];
  const colors = integrationColors[integration.type];

  return (
    <motion.div
      variants={itemVariants}
      initial="hidden"
      animate="visible"
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -4, scale: 1.02 }}
      className="p-5 rounded-lg border bg-card glass-panel-liquid group cursor-pointer"
      onClick={onOpenDetail}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={cn('p-2 rounded-lg border', colors.bg, colors.border)}>
            <Icon className={cn('h-5 w-5', colors.text)} />
          </div>
          <div>
            <h3 className="font-medium group-hover:text-primary transition-colors">
              {integration.name}
            </h3>
            <p className="text-xs text-muted-foreground">
              {integrationLabels[integration.type]}
            </p>
          </div>
        </div>
        <Badge variant="outline" className={statusColors[integration.status]}>
          {integration.status === 'error' && <AlertTriangle className="h-3 w-3 mr-1" />}
          {integration.status === 'active' && <CheckCircle className="h-3 w-3 mr-1" />}
          {integration.status.toUpperCase()}
        </Badge>
      </div>

      {/* Error Indicator */}
      {integration.error_message && (
        <div className="mb-3 text-xs text-red-400 bg-red-500/10 rounded px-2 py-1 truncate">
          {integration.error_message}
        </div>
      )}

      {/* Meta */}
      <div className="flex items-center gap-2 text-xs text-muted-foreground mb-4">
        <Clock className="h-3 w-3" />
        {integration.last_sync_at
          ? `Last sync: ${new Date(integration.last_sync_at).toLocaleDateString()}`
          : 'Never synced'}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
        <Button
          size="sm"
          variant="outline"
          onClick={onTest}
          disabled={isTesting}
          className="flex-1"
        >
          {isTesting ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <>
              <Play className="h-3 w-3 mr-1" />
              Test
            </>
          )}
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={onSync}
          disabled={isSyncing}
          className="flex-1"
        >
          {isSyncing ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <>
              <RefreshCw className="h-3 w-3 mr-1" />
              Sync
            </>
          )}
        </Button>
      </div>
    </motion.div>
  );
}

// Webhooks Tab Component
function WebhooksTab({
  webhooks,
  isLoading,
  onCreateWebhook,
  onCopyUrl,
}: {
  webhooks: WebhookEndpoint[];
  isLoading: boolean;
  onCreateWebhook: () => void;
  onCopyUrl: (url: string) => void;
}) {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (id: string, url: string) => {
    onCopyUrl(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={onCreateWebhook}>
          <Plus className="h-4 w-4 mr-2" />
          Create Webhook
        </Button>
      </div>

      {webhooks.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center py-12 rounded-lg border bg-card glass-panel-liquid"
        >
          <Webhook className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No webhooks configured</h3>
          <p className="text-muted-foreground text-center mb-4">
            Create webhook endpoints to receive events from external systems.
          </p>
          <Button onClick={onCreateWebhook}>
            <Plus className="h-4 w-4 mr-2" />
            Create Your First Webhook
          </Button>
        </motion.div>
      ) : (
        <motion.div
          className="rounded-lg border bg-card glass-panel-liquid"
          initial="hidden"
          animate="visible"
          variants={containerVariants}
        >
          <div className="divide-y">
            {webhooks.map((webhook, index) => (
              <motion.div
                key={webhook.id}
                variants={itemVariants}
                custom={index}
                whileHover={{ backgroundColor: 'rgba(255,255,255,0.05)' }}
                className="p-4"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-orange-500/20 border border-orange-500/30">
                      <Webhook className="h-4 w-4 text-orange-400" />
                    </div>
                    <div>
                      <h4 className="font-medium">{webhook.name}</h4>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                        <span className="flex items-center gap-1">
                          <Activity className="h-3 w-3" />
                          {webhook.trigger_count} triggers
                        </span>
                        {webhook.last_triggered_at && (
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            Last: {new Date(webhook.last_triggered_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <Badge
                    variant="outline"
                    className={webhook.is_active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-500/20 text-gray-400'}
                  >
                    {webhook.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <div className="flex items-center gap-2 mt-3">
                  <code className="flex-1 text-xs bg-muted/50 px-3 py-2 rounded font-mono truncate">
                    {webhook.url}
                  </code>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleCopy(webhook.id, webhook.url)}
                  >
                    {copiedId === webhook.id ? (
                      <CheckCircle className="h-4 w-4 text-emerald-400" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                  <a
                    href={webhook.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 w-8"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}

// Stat Card Component
function StatCard({
  title,
  value,
  icon: Icon,
  className,
  isLoading,
}: {
  title: string;
  value: number;
  icon: React.ElementType;
  className?: string;
  isLoading?: boolean;
}) {
  return (
    <motion.div
      className={cn('rounded-lg border bg-card p-4 glass-panel-liquid', className)}
      whileHover={{ scale: 1.02, y: -2 }}
      transition={{ type: 'spring' as const, stiffness: 300, damping: 20 }}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          {isLoading ? (
            <div className="mt-1 h-8 w-12 animate-pulse rounded bg-muted"></div>
          ) : (
            <p className="mt-1 text-2xl font-bold">
              <AnimatedCounter value={value} duration={1.5} />
            </p>
          )}
        </div>
        <motion.div
          whileHover={{ rotate: 15 }}
          transition={{ type: 'spring' as const, stiffness: 200 }}
        >
          <Icon className="h-8 w-8 text-muted-foreground/50" />
        </motion.div>
      </div>
    </motion.div>
  );
}

export default Integrations;
