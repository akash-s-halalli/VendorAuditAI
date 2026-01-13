import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
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

  // Test channel mutation - error state for UI feedback
  const [_testError, setTestError] = useState<string | null>(null);
  void _testError; // Used for error display
  const [testingChannelId, setTestingChannelId] = useState<string | null>(null);
  const testChannelMutation = useMutation({
    mutationFn: async (channelId: string) => {
      setTestingChannelId(channelId);
      const response = await apiClient.post(`/monitoring/channels/${channelId}/test`, {
        message: 'Test notification from VendorAuditAI',
      });
      return response.data;
    },
    onSuccess: () => {
      setTestError(null);
      setTestingChannelId(null);
    },
    onError: (error) => {
      setTestError(getApiErrorMessage(error));
      setTestingChannelId(null);
    },
  });

  // Acknowledge alert mutation - error state for UI feedback
  const [_alertActionError, setAlertActionError] = useState<string | null>(null);
  void _alertActionError; // Used for error display
  const acknowledgeAlertMutation = useMutation({
    mutationFn: async (alertId: string) => {
      const response = await apiClient.post(`/monitoring/alerts/${alertId}/acknowledge`, {});
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['monitoring-dashboard'] });
      setShowAlertDetailModal(false);
      setAlertActionError(null);
    },
    onError: (error) => {
      setAlertActionError(getApiErrorMessage(error));
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
      setAlertActionError(null);
    },
    onError: (error) => {
      setAlertActionError(getApiErrorMessage(error));
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
            MONITORING<span className="text-primary">CENTER</span>
          </h1>
          <div className="realtime-pulse flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/20 border border-green-500/30">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-green-400 font-medium">LIVE</span>
          </div>
        </div>
        <p className="text-muted-foreground mt-1">
          Schedule automated assessments and manage notifications
        </p>
      </motion.div>

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
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-4">
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
      </motion.div>

      {/* Tabs */}
      <motion.div variants={itemVariants} className="border-b">
        <nav className="-mb-px flex gap-4">
          {(['schedules', 'alerts', 'channels'] as const).map((tab) => (
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
                  layoutId="tab-active-indicator"
                  className="absolute inset-0 bg-primary/10 rounded-t-lg"
                  initial={false}
                  transition={{ type: 'spring' as const, stiffness: 300, damping: 30 }}
                />
              )}
              <span className="relative z-10">
                {tab === 'schedules' && 'Schedules'}
                {tab === 'alerts' && (
                  <>
                    Alerts (<AnimatedCounter value={dashboardStats.open_alerts} duration={1} />)
                  </>
                )}
                {tab === 'channels' && 'Notification Channels'}
              </span>
            </motion.button>
          ))}
        </nav>
      </motion.div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'schedules' && (
          <motion.div
            key="schedules"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <SchedulesTab
              schedules={schedules || []}
              isLoading={schedulesLoading}
              onAddSchedule={() => setShowCreateScheduleModal(true)}
            />
          </motion.div>
        )}
        {activeTab === 'alerts' && (
          <motion.div
            key="alerts"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <AlertsTab
              alerts={alerts}
              isLoading={alertsLoading}
              onAlertClick={handleAlertClick}
            />
          </motion.div>
        )}
        {activeTab === 'channels' && (
          <motion.div
            key="channels"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <ChannelsTab
              channels={channels || []}
              isLoading={channelsLoading}
              onAddChannel={() => setShowCreateChannelModal(true)}
              onTestChannel={(id) => testChannelMutation.mutate(id)}
              testingChannelId={testChannelMutation.isPending ? testingChannelId ?? undefined : undefined}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
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
      <div className="space-y-4">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
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
      <div className="space-y-4">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
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
    <motion.div
      className="rounded-lg border bg-card glass-panel-liquid"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <div className="divide-y">
        {alerts.map((alert, index) => {
          const StatusIcon = alertStatusIcons[alert.status];
          const isHighSeverity = alert.severity === 'critical' || alert.severity === 'high';
          return (
            <motion.div
              key={alert.id}
              variants={itemVariants}
              custom={index}
              whileHover={{ scale: 1.01, backgroundColor: 'rgba(255,255,255,0.05)' }}
              whileTap={{ scale: 0.99 }}
              className={cn(
                'flex items-center gap-4 p-4 cursor-pointer transition-colors',
                isHighSeverity && 'warning-pulse'
              )}
              onClick={() => onAlertClick(alert)}
            >
              <motion.div
                className={cn(
                  'flex h-10 w-10 items-center justify-center rounded-lg',
                  alert.severity === 'critical' && 'bg-red-100',
                  alert.severity === 'high' && 'bg-orange-100',
                  alert.severity === 'medium' && 'bg-yellow-100',
                  alert.severity === 'low' && 'bg-green-100',
                  alert.severity === 'info' && 'bg-blue-100'
                )}
                whileHover={{ rotate: [0, -10, 10, -10, 0] }}
                transition={{ duration: 0.5 }}
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
              </motion.div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-foreground truncate">{alert.title}</h3>
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className={cn(
                      'rounded border px-2 py-0.5 text-xs font-medium capitalize',
                      severityColors[alert.severity]
                    )}
                  >
                    {alert.severity}
                  </motion.span>
                </div>
                <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                  <span>{new Date(alert.created_at).toLocaleString()}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <StatusIcon className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground capitalize">{alert.status}</span>
              </div>
              <motion.div
                whileHover={{ x: 5 }}
                transition={{ type: 'spring' as const, stiffness: 300 }}
              >
                <ChevronRight className="h-5 w-5 text-muted-foreground" />
              </motion.div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
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
      <div className="space-y-4">
        <CardSkeleton />
        <CardSkeleton />
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

export default Monitoring;
