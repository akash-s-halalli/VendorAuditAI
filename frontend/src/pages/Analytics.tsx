import { useQuery } from '@tanstack/react-query';
import {
  BarChart3,
  PieChart,
  Activity,
  AlertTriangle,
  Building2,
  FileText,
  ClipboardList,
  TrendingUp,
  Shield,
  Clock,
  CheckCircle,
  Loader2,
} from 'lucide-react';
import { CyberCard } from '@/components/ui/CyberCard';
import apiClient, { getApiErrorMessage } from '@/lib/api';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface DashboardStats {
  total_vendors: number;
  total_documents: number;
  total_findings: number;
  open_remediation_tasks: number;
  vendors_by_tier: Record<string, number>;
  findings_by_severity: Record<string, number>;
}

interface VendorDistribution {
  category?: Record<string, number>;
  tier?: Record<string, number>;
  status?: Record<string, number>;
}

interface FindingsSummary {
  total: number;
  by_severity: Record<string, number>;
  by_category?: Record<string, number>;
}

interface ComplianceOverview {
  frameworks: Array<{
    name: string;
    coverage_percentage: number;
    total_controls: number;
    compliant_controls: number;
  }>;
}

interface ActivityItem {
  id: string;
  action: string;
  description: string;
  timestamp: string;
  actor?: string;
  entity_type?: string;
  entity_id?: string;
}

interface ActivityResponse {
  data: ActivityItem[];
  total: number;
}

// ============================================================================
// Component
// ============================================================================

export function Analytics() {
  // Fetch main dashboard stats
  const {
    data: dashboardStats,
    isLoading: dashboardLoading,
    isError: dashboardError,
    error: dashboardErrorData,
  } = useQuery<DashboardStats>({
    queryKey: ['analytics-dashboard'],
    queryFn: async () => {
      const response = await apiClient.get('/analytics/dashboard');
      return response.data;
    },
  });

  // Fetch vendor distribution by tier
  const { data: vendorDistribution, isLoading: vendorLoading } = useQuery<VendorDistribution>({
    queryKey: ['analytics-vendors-distribution', 'tier'],
    queryFn: async () => {
      const response = await apiClient.get('/analytics/vendors/distribution?group_by=tier');
      return response.data;
    },
  });

  // Fetch findings summary
  const { data: findingsSummary, isLoading: findingsLoading } = useQuery<FindingsSummary>({
    queryKey: ['analytics-findings-summary'],
    queryFn: async () => {
      const response = await apiClient.get('/analytics/findings/summary');
      return response.data;
    },
  });

  // Fetch compliance overview
  const { data: complianceOverview, isLoading: complianceLoading } = useQuery<ComplianceOverview>({
    queryKey: ['analytics-compliance-overview'],
    queryFn: async () => {
      const response = await apiClient.get('/analytics/compliance/overview');
      return response.data;
    },
  });

  // Fetch recent activity
  const { data: activityResponse, isLoading: activityLoading } = useQuery<ActivityResponse>({
    queryKey: ['analytics-activity'],
    queryFn: async () => {
      const response = await apiClient.get('/analytics/activity?limit=20');
      return response.data;
    },
  });

  const isLoading = dashboardLoading || vendorLoading || findingsLoading || complianceLoading || activityLoading;

  // Severity color mapping
  const severityColors: Record<string, { bg: string; text: string; glow: string }> = {
    critical: { bg: 'bg-red-500', text: 'text-red-500', glow: 'shadow-[0_0_10px_rgba(239,68,68,0.5)]' },
    high: { bg: 'bg-orange-500', text: 'text-orange-500', glow: 'shadow-[0_0_10px_rgba(249,115,22,0.5)]' },
    medium: { bg: 'bg-yellow-500', text: 'text-yellow-500', glow: 'shadow-[0_0_10px_rgba(234,179,8,0.5)]' },
    low: { bg: 'bg-green-500', text: 'text-green-500', glow: 'shadow-[0_0_10px_rgba(34,197,94,0.5)]' },
  };

  // Tier color mapping
  const tierColors: Record<string, { bg: string; text: string; border: string }> = {
    critical: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30' },
    high: { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/30' },
    medium: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/30' },
    low: { bg: 'bg-green-500/10', text: 'text-green-400', border: 'border-green-500/30' },
  };

  // Loading state
  if (isLoading && !dashboardStats) {
    return (
      <div className="p-8 space-y-8">
        <div className="h-12 w-1/3 bg-muted/20 animate-pulse rounded-lg" />
        <div className="grid gap-6 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-40 bg-muted/10 animate-pulse rounded-xl" />
          ))}
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {[1, 2].map((i) => (
            <div key={i} className="h-64 bg-muted/10 animate-pulse rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (dashboardError) {
    return (
      <div className="p-8 flex items-center justify-center h-[50vh]">
        <CyberCard variant="danger" className="p-8 text-center max-w-md">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4 animate-bounce" />
          <h3 className="text-xl font-bold text-white mb-2">System Error</h3>
          <p className="text-muted-foreground">{getApiErrorMessage(dashboardErrorData)}</p>
        </CyberCard>
      </div>
    );
  }

  const stats = dashboardStats || {
    total_vendors: 0,
    total_documents: 0,
    total_findings: 0,
    open_remediation_tasks: 0,
    vendors_by_tier: {},
    findings_by_severity: {},
  };

  const vendorsByTier = vendorDistribution?.tier || stats.vendors_by_tier || {};
  const findingsBySeverity = findingsSummary?.by_severity || stats.findings_by_severity || {};
  const frameworks = complianceOverview?.frameworks || [];
  const activities = activityResponse?.data || [];

  // Calculate max values for bar charts
  const maxTierCount = Math.max(...Object.values(vendorsByTier), 1);
  const maxFindingCount = Math.max(...Object.values(findingsBySeverity), 1);

  return (
    <div className="space-y-6 pb-8 animate-in fade-in duration-500">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
        <div>
          <h1 className="text-5xl font-bold tracking-tighter text-white neon-text mb-2">
            ANALYTICS<span className="text-primary">HUB</span>
          </h1>
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              DATA SYNC ACTIVE
            </span>
            <span className="text-white/10">|</span>
            <span className="font-mono text-primary/80">
              {new Date().toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })}
            </span>
          </div>
        </div>

        <div className="flex gap-3">
          <div className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-primary" />
            <span className="font-mono text-sm text-white">REAL-TIME</span>
          </div>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Vendors"
          value={stats.total_vendors}
          icon={Building2}
          variant="default"
          subtitle="Monitored entities"
          isLoading={dashboardLoading}
        />
        <KPICard
          title="Total Documents"
          value={stats.total_documents}
          icon={FileText}
          variant="default"
          subtitle="Analyzed reports"
          isLoading={dashboardLoading}
        />
        <KPICard
          title="Total Findings"
          value={stats.total_findings}
          icon={AlertTriangle}
          variant="warning"
          subtitle="Security issues identified"
          isLoading={dashboardLoading}
        />
        <KPICard
          title="Open Tasks"
          value={stats.open_remediation_tasks}
          icon={ClipboardList}
          variant="danger"
          subtitle="Pending remediation"
          isLoading={dashboardLoading}
        />
      </div>

      {/* Main Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Vendor Distribution by Tier */}
        <CyberCard className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <PieChart className="h-5 w-5 text-primary" />
              Vendor Distribution by Tier
            </h3>
            <span className="text-xs font-mono text-muted-foreground uppercase">
              {Object.values(vendorsByTier).reduce((a, b) => a + b, 0)} Total
            </span>
          </div>

          {vendorLoading ? (
            <div className="flex items-center justify-center h-48">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : Object.keys(vendorsByTier).length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
              <Building2 className="h-12 w-12 mb-4 opacity-50" />
              <p className="text-sm">No vendor data available</p>
            </div>
          ) : (
            <div className="space-y-4">
              {['critical', 'high', 'medium', 'low'].map((tier) => {
                const count = vendorsByTier[tier] || 0;
                const percentage = maxTierCount > 0 ? (count / maxTierCount) * 100 : 0;
                const colors = tierColors[tier] || tierColors.low;

                return (
                  <div key={tier} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span
                          className={cn(
                            'px-2 py-0.5 rounded text-xs font-medium uppercase border',
                            colors.bg,
                            colors.text,
                            colors.border
                          )}
                        >
                          {tier}
                        </span>
                      </div>
                      <span className="text-white font-mono text-lg">{count}</span>
                    </div>
                    <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                      <div
                        className={cn(
                          'h-full rounded-full transition-all duration-500',
                          severityColors[tier]?.bg || 'bg-gray-500'
                        )}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CyberCard>

        {/* Findings by Severity */}
        <CyberCard className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Shield className="h-5 w-5 text-red-500" />
              Findings by Severity
            </h3>
            <span className="text-xs font-mono text-muted-foreground uppercase">
              {Object.values(findingsBySeverity).reduce((a, b) => a + b, 0)} Total
            </span>
          </div>

          {findingsLoading ? (
            <div className="flex items-center justify-center h-48">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : Object.keys(findingsBySeverity).length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
              <Shield className="h-12 w-12 mb-4 opacity-50" />
              <p className="text-sm">No findings data available</p>
            </div>
          ) : (
            <div className="space-y-4">
              {['critical', 'high', 'medium', 'low'].map((severity) => {
                const count = findingsBySeverity[severity] || 0;
                const percentage = maxFindingCount > 0 ? (count / maxFindingCount) * 100 : 0;
                const colors = severityColors[severity];

                return (
                  <div key={severity} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className={cn('text-sm font-medium uppercase', colors.text)}>
                        {severity}
                      </span>
                      <span className="text-white font-mono text-lg">{count}</span>
                    </div>
                    <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                      <div
                        className={cn('h-full rounded-full transition-all duration-500', colors.bg, colors.glow)}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CyberCard>
      </div>

      {/* Compliance Coverage & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Compliance Coverage */}
        <CyberCard className="lg:col-span-2 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              Compliance Coverage
            </h3>
            <span className="text-xs font-mono text-muted-foreground uppercase">
              {frameworks.length} Frameworks
            </span>
          </div>

          {complianceLoading ? (
            <div className="flex items-center justify-center h-48">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : frameworks.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
              <CheckCircle className="h-12 w-12 mb-4 opacity-50" />
              <p className="text-sm">No compliance frameworks configured</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {frameworks.map((framework) => {
                const coverage = framework.coverage_percentage || 0;
                const coverageColor =
                  coverage >= 80
                    ? 'text-green-400'
                    : coverage >= 60
                      ? 'text-yellow-400'
                      : coverage >= 40
                        ? 'text-orange-400'
                        : 'text-red-400';
                const barColor =
                  coverage >= 80
                    ? 'bg-green-500'
                    : coverage >= 60
                      ? 'bg-yellow-500'
                      : coverage >= 40
                        ? 'bg-orange-500'
                        : 'bg-red-500';

                return (
                  <div
                    key={framework.name}
                    className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-primary/30 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-white font-medium">{framework.name}</span>
                      <span className={cn('font-mono text-lg font-bold', coverageColor)}>
                        {coverage.toFixed(0)}%
                      </span>
                    </div>
                    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden mb-2">
                      <div
                        className={cn('h-full rounded-full transition-all duration-500', barColor)}
                        style={{ width: `${coverage}%` }}
                      />
                    </div>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>
                        {framework.compliant_controls} / {framework.total_controls} controls
                      </span>
                      <TrendingUp className="h-3 w-3" />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CyberCard>

        {/* Recent Activity Timeline */}
        <CyberCard className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              Recent Activity
            </h3>
            <span className="text-xs font-mono text-muted-foreground">LIVE</span>
          </div>

          {activityLoading ? (
            <div className="flex items-center justify-center h-48">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : activities.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
              <Activity className="h-12 w-12 mb-4 opacity-50" />
              <p className="text-sm">No recent activity</p>
            </div>
          ) : (
            <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 scrollbar-thin">
              {activities.slice(0, 10).map((activity) => (
                <div
                  key={activity.id}
                  className="flex gap-3 pb-4 border-b border-white/5 last:border-0"
                >
                  <div className="flex-shrink-0">
                    <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white font-medium truncate">{activity.action}</p>
                    <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                      {activity.description}
                    </p>
                    <div className="flex items-center gap-2 mt-1.5">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground font-mono">
                        {formatRelativeTime(activity.timestamp)}
                      </span>
                      {activity.actor && (
                        <>
                          <span className="text-white/10">|</span>
                          <span className="text-xs text-primary/80">{activity.actor}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CyberCard>
      </div>
    </div>
  );
}

// ============================================================================
// KPI Card Component
// ============================================================================

interface KPICardProps {
  title: string;
  value: number;
  icon: React.ElementType;
  variant?: 'default' | 'danger' | 'warning' | 'success';
  subtitle?: string;
  isLoading?: boolean;
}

function KPICard({ title, value, icon: Icon, variant = 'default', subtitle, isLoading }: KPICardProps) {
  const iconColors = {
    default: 'text-primary',
    danger: 'text-red-500',
    warning: 'text-yellow-500',
    success: 'text-green-500',
  };

  return (
    <CyberCard variant={variant} className="p-6 group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground uppercase tracking-wider mb-2">{title}</p>
          {isLoading ? (
            <div className="h-10 w-20 bg-muted/20 animate-pulse rounded" />
          ) : (
            <p className="text-4xl font-bold text-white font-mono group-hover:scale-105 transition-transform duration-300">
              {value.toLocaleString()}
            </p>
          )}
          {subtitle && <p className="text-xs text-muted-foreground mt-2">{subtitle}</p>}
        </div>
        <div
          className={cn(
            'h-12 w-12 rounded-lg flex items-center justify-center',
            'bg-white/5 border border-white/10 group-hover:border-primary/30 transition-colors'
          )}
        >
          <Icon className={cn('h-6 w-6', iconColors[variant])} />
        </div>
      </div>
    </CyberCard>
  );
}

// ============================================================================
// Utility Functions
// ============================================================================

function formatRelativeTime(timestamp: string): string {
  const now = new Date();
  const date = new Date(timestamp);
  const diffMs = now.getTime() - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSeconds < 60) {
    return 'just now';
  } else if (diffMinutes < 60) {
    return `${diffMinutes}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
}
