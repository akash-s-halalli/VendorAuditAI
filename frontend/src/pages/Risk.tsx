import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  TrendingUp,
  AlertTriangle,
  RefreshCw,
  Building2,
  Shield,
  Loader2,
  ChevronUp,
  ChevronDown,
  Activity,
} from 'lucide-react';
import {
  Button,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui';
import { CyberCard } from '@/components/ui/CyberCard';
import apiClient, { getApiErrorMessage } from '@/lib/api';

// Types for Risk API responses - matches backend schemas
interface RiskFactor {
  name: string;
  description: string;
  raw_value: number;
  weighted_value: number;
  weight: number;
  max_possible: number;
}

interface VendorRisk {
  vendor_id: string;
  vendor_name: string;
  overall_score: number;
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  risk_color: string;
  factors: RiskFactor[];
  calculated_at: string;
  findings_critical: number;
  findings_high: number;
  findings_medium: number;
  findings_low: number;
  total_findings: number;
  compliance_coverage: number;
  vendor_tier: string;
  data_classification: string | null;
  document_age_days: number | null;
}

interface RiskVendorsResponse {
  data: VendorRisk[];
  total: number;
  average_score: number;
  high_risk_count: number;
}

type VendorRiskDetail = VendorRisk;

interface CalculateRiskRequest {
  vendor_ids?: string[];
  force?: boolean;
}

type SortField = 'vendor_name' | 'overall_score' | 'risk_level' | 'total_findings';
type SortDirection = 'asc' | 'desc';

/**
 * Risk Dashboard - Vendor risk assessment and monitoring
 */
export function Risk() {
  const queryClient = useQueryClient();
  const [sortField, setSortField] = useState<SortField>('overall_score');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [selectedVendorId, setSelectedVendorId] = useState<string | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Fetch all vendor risk data
  const {
    data: riskResponse,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<RiskVendorsResponse>({
    queryKey: ['risk-vendors'],
    queryFn: async () => {
      const response = await apiClient.get('/risk/vendors');
      return response.data;
    },
  });

  // Fetch detailed vendor risk when modal is open
  const { data: vendorDetail, isLoading: isLoadingDetail } = useQuery<VendorRiskDetail>({
    queryKey: ['risk-vendor-detail', selectedVendorId],
    queryFn: async () => {
      const response = await apiClient.get(`/risk/vendors/${selectedVendorId}`);
      return response.data;
    },
    enabled: !!selectedVendorId && showDetailModal,
  });

  // Recalculate risk mutation
  const recalculateMutation = useMutation({
    mutationFn: async (request: CalculateRiskRequest) => {
      const response = await apiClient.post('/risk/calculate', request);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risk-vendors'] });
      queryClient.invalidateQueries({ queryKey: ['risk-vendor-detail'] });
    },
  });

  // Sort vendors
  const sortedVendors = [...(riskResponse?.data || [])].sort((a, b) => {
    let comparison = 0;

    switch (sortField) {
      case 'vendor_name':
        comparison = a.vendor_name.localeCompare(b.vendor_name);
        break;
      case 'overall_score':
        comparison = a.overall_score - b.overall_score;
        break;
      case 'risk_level': {
        const riskOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        comparison = riskOrder[a.risk_level] - riskOrder[b.risk_level];
        break;
      }
      case 'total_findings':
        comparison = a.total_findings - b.total_findings;
        break;
    }

    return sortDirection === 'asc' ? comparison : -comparison;
  });

  // Toggle sort
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Open detail modal
  const handleRowClick = (vendorId: string) => {
    setSelectedVendorId(vendorId);
    setShowDetailModal(true);
  };

  // Close detail modal
  const handleCloseModal = () => {
    setShowDetailModal(false);
    setSelectedVendorId(null);
  };

  // Get risk level badge variant
  const getRiskBadgeClasses = (level: string): string => {
    switch (level) {
      case 'critical':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'high':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  // Get score color based on value (lower is better for risk)
  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-red-500';
    if (score >= 60) return 'text-orange-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-green-500';
  };

  // Sort indicator component
  const SortIndicator = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? (
      <ChevronUp className="h-4 w-4 inline ml-1" />
    ) : (
      <ChevronDown className="h-4 w-4 inline ml-1" />
    );
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="p-8 space-y-8">
        <div className="h-12 w-1/3 bg-muted/20 animate-pulse rounded-lg" />
        <div className="grid gap-6 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-muted/10 animate-pulse rounded-xl" />
          ))}
        </div>
        <div className="h-96 bg-muted/10 animate-pulse rounded-xl" />
      </div>
    );
  }

  // Error state
  if (isError) {
    return (
      <div className="p-8 flex items-center justify-center h-[50vh]">
        <CyberCard variant="danger" className="p-8 text-center max-w-md">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4 animate-bounce" />
          <h3 className="text-xl font-bold text-white mb-2">Error Loading Risk Data</h3>
          <p className="text-muted-foreground mb-4">{getApiErrorMessage(error)}</p>
          <Button onClick={() => refetch()} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CyberCard>
      </div>
    );
  }

  const { total = 0, average_score = 0, high_risk_count = 0 } = riskResponse || {};

  return (
    <div className="space-y-6 pb-8 animate-in fade-in duration-500">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
        <div>
          <h1 className="text-5xl font-bold tracking-tighter text-white neon-text mb-2">
            RISK<span className="text-primary">DASHBOARD</span>
          </h1>
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              RISK ENGINE ACTIVE
            </span>
            <span className="text-white/10">|</span>
            <span className="font-mono text-primary/80">
              {total} VENDORS MONITORED
            </span>
          </div>
        </div>

        <Button
          onClick={() => recalculateMutation.mutate({ force: true })}
          disabled={recalculateMutation.isPending}
          className="bg-primary/20 border border-primary/50 hover:bg-primary/30"
        >
          {recalculateMutation.isPending ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Recalculating...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-2" />
              Recalculate All
            </>
          )}
        </Button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Total Vendors */}
        <CyberCard className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm uppercase tracking-wider mb-2">
                Total Vendors
              </p>
              <div className="text-4xl font-bold text-white font-mono">{total}</div>
            </div>
            <div className="h-14 w-14 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
              <Building2 className="h-7 w-7 text-primary" />
            </div>
          </div>
        </CyberCard>

        {/* High Risk Count */}
        <CyberCard variant="danger" className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm uppercase tracking-wider mb-2">
                High Risk Vendors
              </p>
              <div className="text-4xl font-bold text-white font-mono flex items-baseline gap-2">
                {high_risk_count}
                {high_risk_count > 0 && (
                  <span className="text-sm text-red-400 font-sans">
                    <TrendingUp className="h-4 w-4 inline" /> Alert
                  </span>
                )}
              </div>
            </div>
            <div className="h-14 w-14 rounded-full bg-red-500/10 flex items-center justify-center border border-red-500/20">
              <AlertTriangle className="h-7 w-7 text-red-500" />
            </div>
          </div>
        </CyberCard>

        {/* Average Score */}
        <CyberCard className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted-foreground text-sm uppercase tracking-wider mb-2">
                Average Risk Score
              </p>
              <div className={`text-4xl font-bold font-mono ${getScoreColor(average_score)}`}>
                {average_score.toFixed(1)}
              </div>
            </div>
            <div className="h-14 w-14 rounded-full bg-yellow-500/10 flex items-center justify-center border border-yellow-500/20">
              <Activity className="h-7 w-7 text-yellow-500" />
            </div>
          </div>
          <div className="mt-4">
            <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  average_score >= 80
                    ? 'bg-red-500'
                    : average_score >= 60
                    ? 'bg-orange-500'
                    : average_score >= 40
                    ? 'bg-yellow-500'
                    : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(average_score, 100)}%` }}
              />
            </div>
          </div>
        </CyberCard>
      </div>

      {/* Vendors Table */}
      <CyberCard className="p-0 overflow-hidden">
        <div className="p-6 border-b border-white/10">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            Vendor Risk Assessment
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Click on a vendor row to view detailed risk breakdown
          </p>
        </div>

        {sortedVendors.length === 0 ? (
          <div className="p-12 text-center">
            <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No Vendor Risk Data</h3>
            <p className="text-muted-foreground mb-4">
              No vendors have been assessed yet. Add vendors and run analysis to see risk scores.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-white/5">
                <tr>
                  <th
                    className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort('vendor_name')}
                  >
                    Vendor Name
                    <SortIndicator field="vendor_name" />
                  </th>
                  <th
                    className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort('overall_score')}
                  >
                    Risk Score
                    <SortIndicator field="overall_score" />
                  </th>
                  <th
                    className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort('risk_level')}
                  >
                    Risk Level
                    <SortIndicator field="risk_level" />
                  </th>
                  <th className="px-6 py-4 text-center text-xs font-semibold text-red-400 uppercase tracking-wider">
                    Critical
                  </th>
                  <th className="px-6 py-4 text-center text-xs font-semibold text-orange-400 uppercase tracking-wider">
                    High
                  </th>
                  <th className="px-6 py-4 text-center text-xs font-semibold text-yellow-400 uppercase tracking-wider">
                    Medium
                  </th>
                  <th className="px-6 py-4 text-center text-xs font-semibold text-green-400 uppercase tracking-wider">
                    Low
                  </th>
                  <th
                    className="px-6 py-4 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort('total_findings')}
                  >
                    Total
                    <SortIndicator field="total_findings" />
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {sortedVendors.map((vendor) => (
                  <tr
                    key={vendor.vendor_id}
                    className="hover:bg-white/5 cursor-pointer transition-colors"
                    onClick={() => handleRowClick(vendor.vendor_id)}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                          <Building2 className="h-4 w-4 text-primary" />
                        </div>
                        <span className="font-medium text-white">{vendor.vendor_name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`font-mono font-bold ${getScoreColor(vendor.overall_score)}`}>
                        {vendor.overall_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold uppercase border ${getRiskBadgeClasses(
                          vendor.risk_level
                        )}`}
                      >
                        {vendor.risk_level}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span
                        className={`font-mono ${
                          vendor.findings_critical > 0 ? 'text-red-500 font-bold' : 'text-muted-foreground'
                        }`}
                      >
                        {vendor.findings_critical}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span
                        className={`font-mono ${
                          vendor.findings_high > 0 ? 'text-orange-500 font-bold' : 'text-muted-foreground'
                        }`}
                      >
                        {vendor.findings_high}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span
                        className={`font-mono ${
                          vendor.findings_medium > 0 ? 'text-yellow-500' : 'text-muted-foreground'
                        }`}
                      >
                        {vendor.findings_medium}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="font-mono text-muted-foreground">{vendor.findings_low}</span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="font-mono text-white font-medium">{vendor.total_findings}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CyberCard>

      {/* Vendor Detail Modal */}
      <Dialog open={showDetailModal} onOpenChange={handleCloseModal}>
        <DialogContent className="sm:max-w-[600px] bg-background/95 backdrop-blur border-white/10">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-white flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              {vendorDetail?.vendor_name || 'Vendor'} Risk Breakdown
            </DialogTitle>
            <DialogDescription>
              Detailed risk assessment and contributing factors
            </DialogDescription>
          </DialogHeader>

          {isLoadingDetail ? (
            <div className="py-12 flex items-center justify-center">
              <Loader2 className="h-8 w-8 text-primary animate-spin" />
            </div>
          ) : vendorDetail ? (
            <div className="space-y-6">
              {/* Risk Score Overview */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                  <p className="text-sm text-muted-foreground uppercase tracking-wider mb-1">
                    Overall Score
                  </p>
                  <p className={`text-3xl font-bold font-mono ${getScoreColor(vendorDetail.overall_score)}`}>
                    {vendorDetail.overall_score.toFixed(1)}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-white/5 border border-white/10">
                  <p className="text-sm text-muted-foreground uppercase tracking-wider mb-1">
                    Risk Level
                  </p>
                  <span
                    className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-semibold uppercase border ${getRiskBadgeClasses(
                      vendorDetail.risk_level
                    )}`}
                  >
                    {vendorDetail.risk_level}
                  </span>
                </div>
              </div>

              {/* Findings Breakdown */}
              <div>
                <h4 className="text-sm font-semibold text-white mb-3 uppercase tracking-wider">
                  Findings by Severity
                </h4>
                <div className="grid grid-cols-4 gap-3">
                  <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-center">
                    <p className="text-2xl font-bold font-mono text-red-500">
                      {vendorDetail.findings_critical}
                    </p>
                    <p className="text-xs text-red-400 uppercase">Critical</p>
                  </div>
                  <div className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/20 text-center">
                    <p className="text-2xl font-bold font-mono text-orange-500">
                      {vendorDetail.findings_high}
                    </p>
                    <p className="text-xs text-orange-400 uppercase">High</p>
                  </div>
                  <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-center">
                    <p className="text-2xl font-bold font-mono text-yellow-500">
                      {vendorDetail.findings_medium}
                    </p>
                    <p className="text-xs text-yellow-400 uppercase">Medium</p>
                  </div>
                  <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-center">
                    <p className="text-2xl font-bold font-mono text-green-500">
                      {vendorDetail.findings_low}
                    </p>
                    <p className="text-xs text-green-400 uppercase">Low</p>
                  </div>
                </div>
              </div>

              {/* Risk Factors */}
              {vendorDetail.factors && vendorDetail.factors.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-white mb-3 uppercase tracking-wider">
                    Contributing Factors
                  </h4>
                  <div className="space-y-3">
                    {[...vendorDetail.factors]
                      .sort((a, b) => b.weighted_value - a.weighted_value)
                      .map((factor) => (
                        <div key={factor.name}>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-muted-foreground capitalize">
                              {factor.name}
                            </span>
                            <span className={`font-mono ${getScoreColor(factor.weighted_value)}`}>
                              {factor.weighted_value.toFixed(1)}
                            </span>
                          </div>
                          <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                            <div
                              className={`h-full transition-all duration-300 ${
                                factor.weighted_value >= 80
                                  ? 'bg-red-500'
                                  : factor.weighted_value >= 60
                                  ? 'bg-orange-500'
                                  : factor.weighted_value >= 40
                                  ? 'bg-yellow-500'
                                  : 'bg-green-500'
                              }`}
                              style={{ width: `${Math.min(factor.weighted_value, 100)}%` }}
                            />
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Last Calculated */}
              {vendorDetail.calculated_at && (
                <p className="text-xs text-muted-foreground text-center pt-2 border-t border-white/10">
                  Last calculated: {new Date(vendorDetail.calculated_at).toLocaleString()}
                </p>
              )}
            </div>
          ) : (
            <div className="py-12 text-center text-muted-foreground">
              Unable to load vendor details
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
