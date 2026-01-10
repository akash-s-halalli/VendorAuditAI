import { useQuery } from '@tanstack/react-query';
import { Building2, FileText, AlertTriangle, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, Badge } from '@/components/ui';
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
  const { data: stats, isLoading, isError, error } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/dashboard/stats');
      return response.data;
    },
  });

  const statCards = [
    {
      title: 'Total Vendors',
      value: stats?.totalVendors || 0,
      icon: Building2,
      description: 'Active vendors being monitored',
    },
    {
      title: 'Documents',
      value: stats?.totalDocuments || 0,
      icon: FileText,
      description: 'Security reports uploaded',
    },
    {
      title: 'Pending Analysis',
      value: stats?.pendingAnalysis || 0,
      icon: Clock,
      description: 'Documents awaiting review',
    },
    {
      title: 'Completed',
      value: stats?.completedAnalysis || 0,
      icon: CheckCircle,
      description: 'Analyses completed',
    },
  ];

  const findingsData = [
    { severity: 'Critical', count: stats?.criticalFindings || 0, variant: 'critical' as const },
    { severity: 'High', count: stats?.highFindings || 0, variant: 'high' as const },
    { severity: 'Medium', count: stats?.mediumFindings || 0, variant: 'medium' as const },
    { severity: 'Low', count: stats?.lowFindings || 0, variant: 'low' as const },
  ];

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Overview of your vendor security posture</p>
        </div>

        {/* Loading skeleton for stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="h-4 bg-muted rounded w-24"></div>
                <div className="h-4 w-4 bg-muted rounded"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-muted rounded w-16 mb-2"></div>
                <div className="h-3 bg-muted rounded w-32"></div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Loading skeleton for findings and activity */}
        <div className="grid gap-4 md:grid-cols-2 mb-8">
          {[1, 2].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-muted rounded w-48"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[1, 2, 3, 4].map((j) => (
                    <div key={j} className="h-4 bg-muted rounded"></div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Overview of your vendor security posture</p>
        </div>

        <Card className="border-destructive">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
            <h3 className="text-lg font-medium mb-2">Failed to load dashboard</h3>
            <p className="text-muted-foreground text-center mb-4">
              {getApiErrorMessage(error)}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Overview of your vendor security posture</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
        {statCards.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Findings Summary */}
      <div className="grid gap-4 md:grid-cols-2 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Open Findings by Severity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {findingsData.map((finding) => (
                <div key={finding.severity} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Badge variant={finding.variant}>{finding.severity}</Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-32 h-2 rounded-full bg-secondary overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          finding.variant === 'critical'
                            ? 'bg-red-500'
                            : finding.variant === 'high'
                            ? 'bg-orange-500'
                            : finding.variant === 'medium'
                            ? 'bg-yellow-500'
                            : 'bg-blue-500'
                        }`}
                        style={{
                          width: `${Math.min((finding.count / 100) * 100, 100)}%`,
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium w-8">{finding.count}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-100">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                </div>
                <div>
                  <p className="text-sm font-medium">Analysis completed</p>
                  <p className="text-xs text-muted-foreground">Acme Corp SOC 2 Type II - 2 hours ago</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100">
                  <FileText className="h-4 w-4 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium">Document uploaded</p>
                  <p className="text-xs text-muted-foreground">TechVendor SIG Lite - 4 hours ago</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-orange-100">
                  <AlertTriangle className="h-4 w-4 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm font-medium">Critical finding detected</p>
                  <p className="text-xs text-muted-foreground">CloudProvider Inc - 6 hours ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <a
              href="/documents?action=upload"
              className="flex items-center gap-3 rounded-lg border p-4 hover:bg-accent transition-colors"
            >
              <FileText className="h-8 w-8 text-primary" />
              <div>
                <p className="font-medium">Upload Document</p>
                <p className="text-sm text-muted-foreground">Add a new security report</p>
              </div>
            </a>
            <a
              href="/vendors?action=create"
              className="flex items-center gap-3 rounded-lg border p-4 hover:bg-accent transition-colors"
            >
              <Building2 className="h-8 w-8 text-primary" />
              <div>
                <p className="font-medium">Add Vendor</p>
                <p className="text-sm text-muted-foreground">Register a new vendor</p>
              </div>
            </a>
            <a
              href="/query"
              className="flex items-center gap-3 rounded-lg border p-4 hover:bg-accent transition-colors"
            >
              <TrendingUp className="h-8 w-8 text-primary" />
              <div>
                <p className="font-medium">Ask a Question</p>
                <p className="text-sm text-muted-foreground">Query your documents</p>
              </div>
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
