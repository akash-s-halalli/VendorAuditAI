import { useState } from 'react';
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
} from 'lucide-react';
import { cn } from '@/lib/utils';

type ScheduleFrequency = 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'quarterly';
type ScheduleStatus = 'active' | 'paused' | 'disabled';
type AlertSeverity = 'critical' | 'high' | 'medium' | 'low' | 'info';
type AlertStatus = 'new' | 'acknowledged' | 'resolved' | 'dismissed';

interface MonitoringSchedule {
  id: string;
  name: string;
  frequency: ScheduleFrequency;
  status: ScheduleStatus;
  vendor?: string;
  framework?: string;
  nextRun?: string;
  lastRun?: string;
}

interface Alert {
  id: string;
  title: string;
  severity: AlertSeverity;
  status: AlertStatus;
  vendor?: string;
  createdAt: string;
}

// Mock data
const mockSchedules: MonitoringSchedule[] = [
  {
    id: '1',
    name: 'Weekly SOC 2 Compliance Check',
    frequency: 'weekly',
    status: 'active',
    framework: 'SOC 2',
    nextRun: '2026-01-17T09:00:00Z',
    lastRun: '2026-01-10T09:00:00Z',
  },
  {
    id: '2',
    name: 'Monthly CAIQ Assessment',
    frequency: 'monthly',
    status: 'active',
    vendor: 'CloudVendor Inc',
    framework: 'CAIQ',
    nextRun: '2026-02-01T09:00:00Z',
    lastRun: '2026-01-01T09:00:00Z',
  },
  {
    id: '3',
    name: 'Quarterly AI Risk Review',
    frequency: 'quarterly',
    status: 'paused',
    framework: 'AI Risk',
    nextRun: '2026-04-01T09:00:00Z',
    lastRun: '2025-10-01T09:00:00Z',
  },
];

const mockAlerts: Alert[] = [
  {
    id: '1',
    title: 'Critical finding detected in CloudVendor SOC 2 report',
    severity: 'critical',
    status: 'new',
    vendor: 'CloudVendor Inc',
    createdAt: '2026-01-10T14:30:00Z',
  },
  {
    id: '2',
    title: 'SLA breach: Remediation task overdue',
    severity: 'high',
    status: 'acknowledged',
    createdAt: '2026-01-09T10:00:00Z',
  },
  {
    id: '3',
    title: 'New vendor document uploaded for review',
    severity: 'info',
    status: 'new',
    vendor: 'DataCorp',
    createdAt: '2026-01-10T11:15:00Z',
  },
];

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
  resolved: CheckCircle,
  dismissed: XCircle,
};

export function Monitoring() {
  const [activeTab, setActiveTab] = useState<'schedules' | 'alerts' | 'channels'>('schedules');

  const stats = {
    activeSchedules: mockSchedules.filter((s) => s.status === 'active').length,
    pendingAlerts: mockAlerts.filter((a) => a.status === 'new').length,
    assessmentsThisMonth: 12,
    alertsResolved: 8,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Monitoring & Alerts</h1>
        <p className="text-muted-foreground">
          Schedule automated assessments and manage notifications
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Active Schedules"
          value={stats.activeSchedules}
          icon={Calendar}
          className="border-l-4 border-l-blue-500"
        />
        <StatCard
          title="Pending Alerts"
          value={stats.pendingAlerts}
          icon={Bell}
          className="border-l-4 border-l-red-500"
        />
        <StatCard
          title="Assessments This Month"
          value={stats.assessmentsThisMonth}
          icon={CheckCircle}
          className="border-l-4 border-l-green-500"
        />
        <StatCard
          title="Alerts Resolved"
          value={stats.alertsResolved}
          icon={CheckCircle}
          className="border-l-4 border-l-purple-500"
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
              {tab === 'alerts' && `Alerts (${stats.pendingAlerts})`}
              {tab === 'channels' && 'Notification Channels'}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'schedules' && <SchedulesTab schedules={mockSchedules} />}
      {activeTab === 'alerts' && <AlertsTab alerts={mockAlerts} />}
      {activeTab === 'channels' && <ChannelsTab />}
    </div>
  );
}

function SchedulesTab({ schedules }: { schedules: MonitoringSchedule[] }) {
  return (
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
                {schedule.vendor && <span>Vendor: {schedule.vendor}</span>}
              </div>
            </div>
            <div className="text-right text-sm">
              {schedule.nextRun && (
                <p className="text-muted-foreground">
                  Next: {new Date(schedule.nextRun).toLocaleDateString()}
                </p>
              )}
            </div>
            <ChevronRight className="h-5 w-5 text-muted-foreground" />
          </div>
        ))}
      </div>
    </div>
  );
}

function AlertsTab({ alerts }: { alerts: Alert[] }) {
  return (
    <div className="rounded-lg border bg-card">
      <div className="divide-y">
        {alerts.map((alert) => {
          const StatusIcon = alertStatusIcons[alert.status];
          return (
            <div
              key={alert.id}
              className="flex items-center gap-4 p-4 hover:bg-muted/50 cursor-pointer"
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
                  {alert.vendor && <span>{alert.vendor}</span>}
                  <span>{new Date(alert.createdAt).toLocaleString()}</span>
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

function ChannelsTab() {
  const channels = [
    { name: 'Security Team Email', type: 'email', icon: Mail, active: true },
    { name: '#security-alerts', type: 'slack', icon: Slack, active: true },
    { name: 'SIEM Webhook', type: 'webhook', icon: Webhook, active: false },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          <Settings className="h-4 w-4" />
          Add Channel
        </button>
      </div>
      <div className="rounded-lg border bg-card">
        <div className="divide-y">
          {channels.map((channel, i) => (
            <div key={i} className="flex items-center gap-4 p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                <channel.icon className="h-5 w-5 text-muted-foreground" />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-foreground">{channel.name}</h3>
                <p className="text-sm text-muted-foreground capitalize">{channel.type}</p>
              </div>
              <div
                className={cn(
                  'rounded-full px-2 py-0.5 text-xs font-medium',
                  channel.active
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-700'
                )}
              >
                {channel.active ? 'Active' : 'Inactive'}
              </div>
              <button className="text-sm text-primary hover:underline">Test</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  className,
}: {
  title: string;
  value: number;
  icon: React.ElementType;
  className?: string;
}) {
  return (
    <div className={cn('rounded-lg border bg-card p-4', className)}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="mt-1 text-2xl font-bold">{value}</p>
        </div>
        <Icon className="h-8 w-8 text-muted-foreground/50" />
      </div>
    </div>
  );
}

export default Monitoring;
