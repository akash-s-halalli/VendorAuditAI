import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Bell,
  Calendar,
  Clock,
  Play,
  Pause,
  Settings,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  XCircle,
  Mail,
  Slack,
  Webhook,
  Plus,
  Loader2,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  Button,
  Input,
  Label,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui';
import apiClient, { getApiErrorMessage } from '@/lib/api';

type ScheduleFrequency = 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'quarterly';
type ScheduleStatus = 'active' | 'paused' | 'disabled';
type AlertSeverity = 'critical' | 'high' | 'medium' | 'low' | 'info';
type AlertStatus = 'new' | 'acknowledged' | 'in_progress' | 'resolved' | 'dismissed';
type ChannelType = 'email' | 'slack' | 'webhook' | 'teams';

interface MonitoringSchedule {
  id: string;
  name: string;
  description?: string;
  frequency: ScheduleFrequency;
  status: ScheduleStatus;
  vendor_id?: string;
  framework?: string;
  next_run_at?: string;
  last_run_at?: string;
  created_at: string;
}

interface Alert {
  id: string;
  title: string;
  message?: string;
  severity: AlertSeverity;
  status: AlertStatus;
  vendor_id?: string;
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
}

interface NotificationChannel {
  id: string;
  name: string;
  channel_type: ChannelType;
  is_active: boolean;
  last_used_at?: string;
  created_at: string;
}

interface DashboardStats {
  active_schedules: number;
  total_alerts: number;
  open_alerts: number;
  critical_alerts: number;
  recent_runs: number;
  alerts_by_severity: Record<string, number>;
  alerts_by_status: Record<string, number>;
}

interface AlertListResponse {
  data: Alert[];
  total: number;
  page: number;
  limit: number;
}

const frequencyLabels: Record<ScheduleFrequency, string> = {
  daily: 'Daily',
  weekly: 'Weekly',
  biweekly: 'Bi-weekly',
  monthly: 'Monthly',
  quarterly: 'Quarterly',
};

const severityColors: Record<AlertSeverity, string> = {
  critical: 'bg-red-100 text-red-700 border-red-300',
  high: 'bg-orange-100 text-orange-700 border-orange-300',
  medium: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  low: 'bg-green-100 text-green-700 border-green-300',
  info: 'bg-blue-100 text-blue-700 border-blue-300',
};

const alertStatusIcons: Record<AlertStatus, React.ElementType> = {
  new: AlertCircle,
  acknowledged: Clock,
  in_progress: Play,
  resolved: CheckCircle,
  dismissed: XCircle,
};

const channelIcons: Record<ChannelType, React.ElementType> = {
  email: Mail,
  slack: Slack,
  webhook: Webhook,
  teams: Slack, // Using Slack icon as placeholder for Teams
};

export function Monitoring() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'schedules' | 'alerts' | 'channels'>('schedules');
  const [showCreateScheduleModal, setShowCreateScheduleModal] = useState(false);
  const [showCreateChannelModal, setShowCreateChannelModal] = useState(false);
  const [showAlertDetailModal, setShowAlertDetailModal] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);

  // Form state for new schedule
  const [newSchedule, setNewSchedule] = useState({
    name: '',
    description: '',
    frequency: 'weekly' as ScheduleFrequency,
    framework: '',
    include_all_vendors: true,
    notify_on_completion: true,
    notify_on_findings: true,
  });

  // Form state for new channel
  const [newChannel, setNewChannel] = useState({
    name: '',
    channel_type: 'email' as ChannelType,
    config: {} as Record<string, string>,
  });

  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ['monitoring-dashboard'],
    queryFn: async () => {
      const response = await apiClient.get('/monitoring/dashboard');
      return response.data;
    },
  });

  // Fetch schedules
  const { data: schedules, isLoading: schedulesLoading } = useQuery<MonitoringSchedule[]>({
    queryKey: ['monitoring-schedules'],
    queryFn: async () => {
      const response = await apiClient.get('/monitoring/schedules');
      return response.data;
    },
  });

  // Fetch alerts
  const { data: alertsResponse, isLoading: alertsLoading } = useQuery<AlertListResponse>({
    queryKey: ['monitoring-alerts'],
    queryFn: async () => {
      const response = await apiClient.get('/monitoring/alerts?limit=50');
      return response.data;
    },
  });

  // Fetch channels
  const { data: channels, isLoading: channelsLoading } = useQuery<NotificationChannel[]>({
    queryKey: ['monitoring-channels'],
    queryFn: async () => {
      const response = await apiClient.get('/monitoring/channels');
      return response.data;
    },
  });

  // Create schedule mutation
  const createScheduleMutation = useMutation({
    mutationFn: async (scheduleData: typeof newSchedule) => {
      const response = await apiClient.post('/monitoring/schedules', scheduleData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-schedules'] });
      queryClient.invalidateQueries({ queryKey: ['monitoring-dashboard'] });
      setShowCreateScheduleModal(false);
      setNewSchedule({
        name: '',
        description: '',
        frequency: 'weekly',
        framework: '',
        include_all_vendors: true,
        notify_on_completion: true,
        notify_on_findings: true,
      });
      setCreateError(null);
    },
    onError: (error) => {
      setCreateError(getApiErrorMessage(error));
    },
  });

  // Create channel mutation
  const createChannelMutation = useMutation({
    mutationFn: async (channelData: typeof newChannel) => {
      const response = await apiClient.post('/monitoring/channels', channelData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-channels'] });
      setShowCreateChannelModal(false);
      setNewChannel({ name: '', channel_type: 'email', config: {} });
      setCreateError(null);
    },
    onError: (error) => {
      setCreateError(getApiErrorMessage(error));
    },
  });

  // Test channel mutation
  const testChannelMutation = useMutation({
    mutationFn: async (channelId: string) => {
      const response = await apiClient.post(`/monitoring/channels/${channelId}/test`, {
        message: 'Test notification from VendorAuditAI',
      });
      return response.data;
    },
  });

  // Acknowledge alert mutation
  const acknowledgeAlertMutation = useMutation({
    mutationFn: async (alertId: string) => {
      const response = await apiClient.post(`/monitoring/alerts/${alertId}/acknowledge`, {});
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['monitoring-dashboard'] });
      setShowAlertDetailModal(false);
    },
  });

  // Resolve alert mutation
  const resolveAlertMutation = useMutation({
    mutationFn: async ({ alertId, notes }: { alertId: string; notes?: string }) => {
      const response = await apiClient.post(`/monitoring/alerts/${alertId}/resolve`, {
        resolution_notes: notes,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['monitoring-dashboard'] });
      setShowAlertDetailModal(false);
    },
  });

  const handleCreateSchedule = () => {
    if (!newSchedule.name.trim()) {
      setCreateError('Schedule name is required');
      return;
    }
    setCreateError(null);
    createScheduleMutation.mutate(newSchedule);
  };

  const handleCreateChannel = () => {
    if (!newChannel.name.trim()) {
      setCreateError('Channel name is required');
      return;
    }
    setCreateError(null);
    createChannelMutation.mutate(newChannel);
  };

  const handleAlertClick = (alert: Alert) => {
    setSelectedAlert(alert);
    setShowAlertDetailModal(true);
  };

  const dashboardStats = stats || {
    active_schedules: 0,
    total_alerts: 0,
    open_alerts: 0,
    critical_alerts: 0,
    recent_runs: 0,
    alerts_by_severity: {},
    alerts_by_status: {},
  };

  const alerts = alertsResponse?.data || [];
  const isLoading = statsLoading || schedulesLoading || alertsLoading || channelsLoading;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Monitoring & Alerts</h1>
        <p className="text-muted-foreground">
          Schedule automated assessments and manage notifications
        </p>
      </div>

      {/* Create Schedule Modal */}
      <Dialog open={showCreateScheduleModal} onOpenChange={setShowCreateScheduleModal}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create Monitoring Schedule</DialogTitle>
            <DialogDescription>
              Schedule automated security assessments for your vendors.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="schedule-name">Schedule Name *</Label>
              <Input
                id="schedule-name"
                placeholder="e.g., Weekly SOC 2 Compliance Check"
                value={newSchedule.name}
                onChange={(e) => setNewSchedule({ ...newSchedule, name: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="schedule-description">Description</Label>
              <Input
                id="schedule-description"
                placeholder="Brief description of the schedule"
                value={newSchedule.description}
                onChange={(e) => setNewSchedule({ ...newSchedule, description: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="schedule-frequency">Frequency</Label>
              <select
                id="schedule-frequency"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={newSchedule.frequency}
                onChange={(e) => setNewSchedule({ ...newSchedule, frequency: e.target.value as ScheduleFrequency })}
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="biweekly">Bi-weekly</option>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
              </select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="schedule-framework">Framework</Label>
              <Input
                id="schedule-framework"
                placeholder="e.g., SOC 2, ISO 27001"
                value={newSchedule.framework}
                onChange={(e) => setNewSchedule({ ...newSchedule, framework: e.target.value })}
              />
            </div>
            {createError && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {createError}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateScheduleModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateSchedule} disabled={createScheduleMutation.isPending}>
              {createScheduleMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Schedule
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Channel Modal */}
      <Dialog open={showCreateChannelModal} onOpenChange={setShowCreateChannelModal}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Add Notification Channel</DialogTitle>
            <DialogDescription>
              Configure a new channel to receive alerts and notifications.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="channel-name">Channel Name *</Label>
              <Input
                id="channel-name"
                placeholder="e.g., Security Team Email"
                value={newChannel.name}
                onChange={(e) => setNewChannel({ ...newChannel, name: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="channel-type">Channel Type</Label>
              <select
                id="channel-type"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={newChannel.channel_type}
                onChange={(e) => setNewChannel({ ...newChannel, channel_type: e.target.value as ChannelType })}
              >
                <option value="email">Email</option>
                <option value="slack">Slack</option>
                <option value="webhook">Webhook</option>
                <option value="teams">Microsoft Teams</option>
              </select>
            </div>
            {createError && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {createError}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateChannelModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateChannel} disabled={createChannelMutation.isPending}>
              {createChannelMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Add Channel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Alert Detail Modal */}
      <Dialog open={showAlertDetailModal} onOpenChange={setShowAlertDetailModal}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{selectedAlert?.title}</DialogTitle>
            <DialogDescription>
              View and manage this alert
            </DialogDescription>
          </DialogHeader>
          {selectedAlert && (
            <div className="space-y-4 py-4">
              <div className="flex items-center gap-2">
                <span className={cn('rounded border px-2 py-0.5 text-xs font-medium capitalize', severityColors[selectedAlert.severity])}>
                  {selectedAlert.severity}
                </span>
                <span className="rounded bg-muted px-2 py-0.5 text-xs font-medium capitalize">
                  {selectedAlert.status}
                </span>
              </div>
              {selectedAlert.message && (
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Message</h4>
                  <p className="mt-1 text-sm">{selectedAlert.message}</p>
                </div>
              )}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Created:</span>
                  <span className="ml-2">{new Date(selectedAlert.created_at).toLocaleString()}</span>
                </div>
                {selectedAlert.acknowledged_at && (
                  <div>
                    <span className="text-muted-foreground">Acknowledged:</span>
                    <span className="ml-2">{new Date(selectedAlert.acknowledged_at).toLocaleString()}</span>
                  </div>
                )}
              </div>
              <div className="border-t pt-4">
                <h4 className="text-sm font-medium mb-2">Actions</h4>
                <div className="flex gap-2">
                  {selectedAlert.status === 'new' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => acknowledgeAlertMutation.mutate(selectedAlert.id)}
                      disabled={acknowledgeAlertMutation.isPending}
                    >
                      {acknowledgeAlertMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      Acknowledge
                    </Button>
                  )}
                  {(selectedAlert.status === 'new' || selectedAlert.status === 'acknowledged') && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => resolveAlertMutation.mutate({ alertId: selectedAlert.id })}
                      disabled={resolveAlertMutation.isPending}
                    >
                      {resolveAlertMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      Resolve
                    </Button>
                  )}
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAlertDetailModal(false)}>
              <X className="h-4 w-4 mr-2" />
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Active Schedules"
          value={dashboardStats.active_schedules}
          icon={Calendar}
          className="border-l-4 border-l-blue-500"
          isLoading={isLoading}
        />
        <StatCard
          title="Open Alerts"
          value={dashboardStats.open_alerts}
          icon={Bell}
          className="border-l-4 border-l-red-500"
          isLoading={isLoading}
        />
        <StatCard
          title="Recent Runs"
          value={dashboardStats.recent_runs}
          icon={CheckCircle}
          className="border-l-4 border-l-green-500"
          isLoading={isLoading}
        />
        <StatCard
          title="Critical Alerts"
          value={dashboardStats.critical_alerts}
          icon={AlertCircle}
          className="border-l-4 border-l-purple-500"
          isLoading={isLoading}
        />
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex gap-4">
          {(['schedules', 'alerts', 'channels'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                'border-b-2 px-4 py-2 text-sm font-medium transition-colors',
                activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              {tab === 'schedules' && 'Schedules'}
              {tab === 'alerts' && `Alerts (${dashboardStats.open_alerts})`}
              {tab === 'channels' && 'Notification Channels'}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'schedules' && (
        <SchedulesTab
          schedules={schedules || []}
          isLoading={schedulesLoading}
          onAddSchedule={() => setShowCreateScheduleModal(true)}
        />
      )}
      {activeTab === 'alerts' && (
        <AlertsTab
          alerts={alerts}
          isLoading={alertsLoading}
          onAlertClick={handleAlertClick}
        />
      )}
      {activeTab === 'channels' && (
        <ChannelsTab
          channels={channels || []}
          isLoading={channelsLoading}
          onAddChannel={() => setShowCreateChannelModal(true)}
          onTestChannel={(id) => testChannelMutation.mutate(id)}
          testingChannelId={testChannelMutation.isPending ? testChannelMutation.variables : undefined}
        />
      )}
    </div>
  );
}

function SchedulesTab({
  schedules,
  isLoading,
  onAddSchedule,
}: {
  schedules: MonitoringSchedule[];
  isLoading: boolean;
  onAddSchedule: () => void;
}) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (schedules.length === 0) {
    return (
      <div className="rounded-lg border bg-card p-8 text-center">
        <Calendar className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium mb-2">No schedules yet</h3>
        <p className="text-muted-foreground mb-4">
          Create your first monitoring schedule to automate security assessments.
        </p>
        <Button onClick={onAddSchedule}>
          <Plus className="h-4 w-4 mr-2" />
          Create Schedule
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={onAddSchedule}>
          <Plus className="h-4 w-4 mr-2" />
          Create Schedule
        </Button>
      </div>
      <div className="rounded-lg border bg-card">
        <div className="divide-y">
          {schedules.map((schedule) => (
            <div
              key={schedule.id}
              className="flex items-center gap-4 p-4 hover:bg-muted/50 cursor-pointer"
            >
              <div
                className={cn(
                  'flex h-10 w-10 items-center justify-center rounded-lg',
                  schedule.status === 'active' ? 'bg-green-100' : 'bg-gray-100'
                )}
              >
                {schedule.status === 'active' ? (
                  <Play className="h-5 w-5 text-green-600" />
                ) : (
                  <Pause className="h-5 w-5 text-gray-500" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-foreground">{schedule.name}</h3>
                <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {frequencyLabels[schedule.frequency]}
                  </span>
                  {schedule.framework && <span>Framework: {schedule.framework}</span>}
                </div>
              </div>
              <div className="text-right text-sm">
                {schedule.next_run_at && (
                  <p className="text-muted-foreground">
                    Next: {new Date(schedule.next_run_at).toLocaleDateString()}
                  </p>
                )}
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AlertsTab({
  alerts,
  isLoading,
  onAlertClick,
}: {
  alerts: Alert[];
  isLoading: boolean;
  onAlertClick: (alert: Alert) => void;
}) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="rounded-lg border bg-card p-8 text-center">
        <Bell className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium mb-2">No alerts</h3>
        <p className="text-muted-foreground">
          You're all caught up. No alerts to display at this time.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card">
      <div className="divide-y">
        {alerts.map((alert) => {
          const StatusIcon = alertStatusIcons[alert.status];
          return (
            <div
              key={alert.id}
              className="flex items-center gap-4 p-4 hover:bg-muted/50 cursor-pointer"
              onClick={() => onAlertClick(alert)}
            >
              <div
                className={cn(
                  'flex h-10 w-10 items-center justify-center rounded-lg',
                  alert.severity === 'critical' && 'bg-red-100',
                  alert.severity === 'high' && 'bg-orange-100',
                  alert.severity === 'medium' && 'bg-yellow-100',
                  alert.severity === 'low' && 'bg-green-100',
                  alert.severity === 'info' && 'bg-blue-100'
                )}
              >
                <Bell
                  className={cn(
                    'h-5 w-5',
                    alert.severity === 'critical' && 'text-red-600',
                    alert.severity === 'high' && 'text-orange-600',
                    alert.severity === 'medium' && 'text-yellow-600',
                    alert.severity === 'low' && 'text-green-600',
                    alert.severity === 'info' && 'text-blue-600'
                  )}
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-foreground truncate">{alert.title}</h3>
                  <span
                    className={cn(
                      'rounded border px-2 py-0.5 text-xs font-medium capitalize',
                      severityColors[alert.severity]
                    )}
                  >
                    {alert.severity}
                  </span>
                </div>
                <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                  <span>{new Date(alert.created_at).toLocaleString()}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <StatusIcon className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground capitalize">{alert.status}</span>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ChannelsTab({
  channels,
  isLoading,
  onAddChannel,
  onTestChannel,
  testingChannelId,
}: {
  channels: NotificationChannel[];
  isLoading: boolean;
  onAddChannel: () => void;
  onTestChannel: (channelId: string) => void;
  testingChannelId?: string;
}) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={onAddChannel}>
          <Settings className="h-4 w-4 mr-2" />
          Add Channel
        </Button>
      </div>

      {channels.length === 0 ? (
        <div className="rounded-lg border bg-card p-8 text-center">
          <Mail className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No notification channels</h3>
          <p className="text-muted-foreground mb-4">
            Add a notification channel to receive alerts about your vendor security assessments.
          </p>
          <Button onClick={onAddChannel}>
            <Plus className="h-4 w-4 mr-2" />
            Add Channel
          </Button>
        </div>
      ) : (
        <div className="rounded-lg border bg-card">
          <div className="divide-y">
            {channels.map((channel) => {
              const ChannelIcon = channelIcons[channel.channel_type] || Webhook;
              return (
                <div key={channel.id} className="flex items-center gap-4 p-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                    <ChannelIcon className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-foreground">{channel.name}</h3>
                    <p className="text-sm text-muted-foreground capitalize">{channel.channel_type}</p>
                  </div>
                  <div
                    className={cn(
                      'rounded-full px-2 py-0.5 text-xs font-medium',
                      channel.is_active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    )}
                  >
                    {channel.is_active ? 'Active' : 'Inactive'}
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onTestChannel(channel.id)}
                    disabled={testingChannelId === channel.id}
                  >
                    {testingChannelId === channel.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      'Test'
                    )}
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

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
    <div className={cn('rounded-lg border bg-card p-4', className)}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          {isLoading ? (
            <div className="mt-1 h-8 w-12 animate-pulse rounded bg-muted"></div>
          ) : (
            <p className="mt-1 text-2xl font-bold">{value}</p>
          )}
        </div>
        <Icon className="h-8 w-8 text-muted-foreground/50" />
      </div>
    </div>
  );
}

export default Monitoring;
