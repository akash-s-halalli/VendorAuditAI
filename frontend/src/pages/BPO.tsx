import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Building2, Shield, AlertTriangle, Plus, Search,
  FileText, Activity, Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { AnimatedCounter } from '@/components/ui/AnimatedCounter';
import apiClient from '@/lib/api';

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
};

// Types
interface BPOProvider {
  id: string;
  vendor_id: string;
  vendor_name?: string;
  service_type: string;
  process_category: string;
  geographic_locations: string[];
  data_access_level: string;
  employee_count?: number;
  contract_value?: number;
  contract_start_date?: string;
  contract_end_date?: string;
  created_at: string;
  updated_at: string;
}

interface BPODashboardStats {
  total_providers: number;
  active_providers: number;
  total_processes: number;
  critical_processes: number;
  total_assessments: number;
  assessments_overdue: number;
}

export function BPO() {
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['bpo-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/bpo/dashboard');
      return response.data as BPODashboardStats;
    },
  });

  // Fetch providers
  const { data: providersData, isLoading: providersLoading } = useQuery({
    queryKey: ['bpo-providers', searchQuery],
    queryFn: async () => {
      const response = await apiClient.get('/bpo/providers', {
        params: { search: searchQuery || undefined }
      });
      return response.data;
    },
  });

  const providers: BPOProvider[] = providersData?.data || [];

  const getServiceTypeBadge = (type: string) => {
    const colors: Record<string, string> = {
      call_center: 'bg-blue-500/20 text-blue-400',
      it_services: 'bg-purple-500/20 text-purple-400',
      finance: 'bg-green-500/20 text-green-400',
      hr: 'bg-yellow-500/20 text-yellow-400',
      legal: 'bg-red-500/20 text-red-400',
      back_office: 'bg-gray-500/20 text-gray-400',
    };
    return colors[type] || 'bg-slate-500/20 text-slate-400';
  };

  const getDataAccessBadge = (level: string) => {
    const colors: Record<string, string> = {
      full: 'bg-red-500/20 text-red-400',
      elevated: 'bg-orange-500/20 text-orange-400',
      standard: 'bg-yellow-500/20 text-yellow-400',
      limited: 'bg-green-500/20 text-green-400',
      none: 'bg-slate-500/20 text-slate-400',
    };
    return colors[level] || 'bg-slate-500/20 text-slate-400';
  };

  return (
    <div className="flex-1 p-6 space-y-6 overflow-y-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-white">BPO Risk Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage Business Process Outsourcing providers and risk assessments
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Add Provider
        </Button>
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <motion.div variants={itemVariants}>
          <Card className="glass-panel-liquid border-white/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Building2 className="h-4 w-4 text-blue-400" />
                Total Providers
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <AnimatedCounter value={stats?.total_providers || 0} className="text-3xl font-bold text-white" />
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="glass-panel-liquid border-white/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Activity className="h-4 w-4 text-green-400" />
                Active Providers
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <AnimatedCounter value={stats?.active_providers || 0} className="text-3xl font-bold text-white" />
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="glass-panel-liquid border-white/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <FileText className="h-4 w-4 text-purple-400" />
                Total Processes
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <AnimatedCounter value={stats?.total_processes || 0} className="text-3xl font-bold text-white" />
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="glass-panel-liquid border-white/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-red-400" />
                Assessments Overdue
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              ) : (
                <AnimatedCounter value={stats?.assessments_overdue || 0} className="text-3xl font-bold text-white" />
              )}
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="flex items-center gap-4"
      >
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search providers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-white/5 border-white/10"
          />
        </div>
      </motion.div>

      {/* Providers List */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        {providersLoading ? (
          Array(6).fill(0).map((_, i) => (
            <motion.div key={i} variants={itemVariants}>
              <Card className="glass-panel-liquid border-white/5 h-48 animate-pulse" />
            </motion.div>
          ))
        ) : providers.length === 0 ? (
          <motion.div variants={itemVariants} className="col-span-full">
            <Card className="glass-panel-liquid border-white/5 p-12 text-center">
              <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">No BPO Providers</h3>
              <p className="text-muted-foreground mb-4">
                Add your first BPO provider to start managing outsourcing risk
              </p>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Provider
              </Button>
            </Card>
          </motion.div>
        ) : (
          providers.map((provider) => (
            <motion.div key={provider.id} variants={itemVariants}>
              <Card className="glass-panel-liquid border-white/5 hover:border-white/10 transition-colors cursor-pointer">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-white">
                        {provider.vendor_name || 'Unknown Provider'}
                      </CardTitle>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge className={getServiceTypeBadge(provider.service_type)}>
                          {provider.service_type.replace('_', ' ')}
                        </Badge>
                        <Badge className={getDataAccessBadge(provider.data_access_level)}>
                          {provider.data_access_level} access
                        </Badge>
                      </div>
                    </div>
                    <Shield className="h-5 w-5 text-muted-foreground" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p>Category: {provider.process_category.replace('_', ' ')}</p>
                    {provider.geographic_locations?.length > 0 && (
                      <p>Locations: {provider.geographic_locations.join(', ')}</p>
                    )}
                    {provider.contract_end_date && (
                      <p>Contract ends: {new Date(provider.contract_end_date).toLocaleDateString()}</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))
        )}
      </motion.div>
    </div>
  );
}
