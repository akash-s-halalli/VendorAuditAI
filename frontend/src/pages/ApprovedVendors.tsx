import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckCircle,
  Clock,
  Shield,
  Building2,
  Search,
  Plus,
  AlertTriangle,
  Rocket,
  FileText,
  ExternalLink,
  Loader2,
  Check,
  Filter,
  Briefcase,
  Database,
  Zap,
  ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  Button,
  Input,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Badge,
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
import { useToast } from '@/components/ui/toast';
import apiClient, { getApiErrorMessage } from '@/lib/api';

// Animation variants
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

const cardVariants = {
  hidden: { y: 20, opacity: 0, scale: 0.95 },
  visible: {
    y: 0,
    opacity: 1,
    scale: 1,
    transition: { type: 'spring' as const, stiffness: 100, damping: 15 },
  },
  exit: { y: -20, opacity: 0, scale: 0.95, transition: { duration: 0.2 } },
};

// Types
type ApprovalStatus = 'approved' | 'conditional' | 'expired' | 'pending';
type DataClassification = 'public' | 'internal' | 'confidential' | 'restricted';
type UrgencyLevel = 'low' | 'medium' | 'high' | 'critical';
type RequestStatus = 'pending' | 'under_review' | 'approved' | 'rejected';
type DeploymentStatus = 'active' | 'pending' | 'suspended' | 'terminated';

interface UseCase {
  id: string;
  name: string;
  description: string;
  data_classification: DataClassification;
}

interface ApprovedVendor {
  id: string;
  name: string;
  website?: string;
  category: string;
  description?: string;
  logo_url?: string;
  approval_status: ApprovalStatus;
  data_classification_limit: DataClassification;
  approved_use_cases: UseCase[];
  conditions?: string[];
  expiry_date?: string;
  approved_at?: string;
  approved_by?: string;
  department_restrictions?: string[];
  created_at: string;
}

interface Deployment {
  id: string;
  vendor_id: string;
  vendor_name: string;
  use_case_id: string;
  use_case_name: string;
  department: string;
  team?: string;
  status: DeploymentStatus;
  deployed_at: string;
  deployed_by: string;
  data_classification: DataClassification;
}

interface ToolRequest {
  id: string;
  tool_name: string;
  website?: string;
  description: string;
  use_case_description: string;
  business_justification: string;
  department: string;
  urgency: UrgencyLevel;
  status: RequestStatus;
  submitted_at: string;
  submitted_by: string;
  reviewer_notes?: string;
}

interface ApprovedVendorStats {
  total_approved: number;
  active_deployments: number;
  pending_requests: number;
  conditional_approvals: number;
  expiring_soon: number;
}

// Status styling configurations
const approvalStatusConfig: Record<ApprovalStatus, { label: string; color: string; bgColor: string; icon: React.ElementType }> = {
  approved: {
    label: 'Approved',
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/20 border-emerald-500/30',
    icon: CheckCircle,
  },
  conditional: {
    label: 'Conditional',
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/20 border-yellow-500/30',
    icon: AlertTriangle,
  },
  expired: {
    label: 'Expired',
    color: 'text-red-400',
    bgColor: 'bg-red-500/20 border-red-500/30',
    icon: Clock,
  },
  pending: {
    label: 'Pending',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/20 border-blue-500/30',
    icon: Clock,
  },
};

const dataClassificationConfig: Record<DataClassification, { label: string; color: string }> = {
  public: { label: 'Public', color: 'text-green-400 bg-green-500/20 border-green-500/30' },
  internal: { label: 'Internal', color: 'text-blue-400 bg-blue-500/20 border-blue-500/30' },
  confidential: { label: 'Confidential', color: 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30' },
  restricted: { label: 'Restricted', color: 'text-red-400 bg-red-500/20 border-red-500/30' },
};

const urgencyConfig: Record<UrgencyLevel, { label: string; color: string }> = {
  low: { label: 'Low', color: 'text-gray-400 bg-gray-500/20' },
  medium: { label: 'Medium', color: 'text-blue-400 bg-blue-500/20' },
  high: { label: 'High', color: 'text-orange-400 bg-orange-500/20' },
  critical: { label: 'Critical', color: 'text-red-400 bg-red-500/20' },
};

const requestStatusConfig: Record<RequestStatus, { label: string; color: string }> = {
  pending: { label: 'Pending', color: 'text-gray-400 bg-gray-500/20' },
  under_review: { label: 'Under Review', color: 'text-blue-400 bg-blue-500/20' },
  approved: { label: 'Approved', color: 'text-emerald-400 bg-emerald-500/20' },
  rejected: { label: 'Rejected', color: 'text-red-400 bg-red-500/20' },
};

const deploymentStatusConfig: Record<DeploymentStatus, { label: string; color: string }> = {
  active: { label: 'Active', color: 'text-emerald-400 bg-emerald-500/20' },
  pending: { label: 'Pending', color: 'text-yellow-400 bg-yellow-500/20' },
  suspended: { label: 'Suspended', color: 'text-orange-400 bg-orange-500/20' },
  terminated: { label: 'Terminated', color: 'text-red-400 bg-red-500/20' },
};

const departments = [
  'Engineering',
  'Marketing',
  'Sales',
  'Human Resources',
  'Finance',
  'Legal',
  'Operations',
  'Customer Success',
  'Product',
  'Design',
  'IT',
  'Security',
];

export function ApprovedVendors() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  // Tab state
  const [activeTab, setActiveTab] = useState<'browse' | 'deployments' | 'requests'>('browse');

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | ApprovalStatus>('all');
  const [departmentFilter, setDepartmentFilter] = useState<string>('all');

  // Modal states
  const [showDeployModal, setShowDeployModal] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [selectedVendor, setSelectedVendor] = useState<ApprovedVendor | null>(null);

  // Deploy wizard state
  const [deployWizardStep, setDeployWizardStep] = useState(1);
  const [deployForm, setDeployForm] = useState({
    use_case_id: '',
    department: '',
    team: '',
    data_classification: '' as DataClassification | '',
    accept_conditions: false,
  });

  // Request form state
  const [requestForm, setRequestForm] = useState({
    tool_name: '',
    website: '',
    description: '',
    use_case_description: '',
    business_justification: '',
    department: '',
    urgency: 'medium' as UrgencyLevel,
  });

  // Fetch stats
  const { data: stats, isLoading: statsLoading } = useQuery<ApprovedVendorStats>({
    queryKey: ['approved-vendor-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/approved-vendors/stats');
      return response.data;
    },
  });

  // Fetch approved vendors
  const { data: vendorsResponse, isLoading: vendorsLoading } = useQuery<{ data: ApprovedVendor[]; total: number }>({
    queryKey: ['approved-vendors', searchQuery, statusFilter, departmentFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (departmentFilter !== 'all') params.append('department', departmentFilter);
      params.append('limit', '50');

      const response = await apiClient.get(`/approved-vendors?${params}`);
      return response.data;
    },
  });

  // Fetch user's deployments
  const { data: deploymentsResponse, isLoading: deploymentsLoading } = useQuery<{ data: Deployment[]; total: number }>({
    queryKey: ['my-deployments'],
    queryFn: async () => {
      const response = await apiClient.get('/approved-vendors/my-deployments');
      return response.data;
    },
    enabled: activeTab === 'deployments',
  });

  // Fetch user's requests
  const { data: requestsResponse, isLoading: requestsLoading } = useQuery<{ data: ToolRequest[]; total: number }>({
    queryKey: ['my-requests'],
    queryFn: async () => {
      const response = await apiClient.get('/approved-vendors/my-requests');
      return response.data;
    },
    enabled: activeTab === 'requests',
  });

  // Deploy mutation
  const deployMutation = useMutation({
    mutationFn: async ({ vendorId, data }: { vendorId: string; data: typeof deployForm }) => {
      const response = await apiClient.post(`/approved-vendors/${vendorId}/deploy`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-deployments'] });
      queryClient.invalidateQueries({ queryKey: ['approved-vendor-stats'] });
      setShowDeployModal(false);
      resetDeployForm();
      addToast({
        type: 'success',
        title: 'Deployment Initiated',
        description: 'Your tool deployment request has been submitted successfully.',
      });
    },
    onError: (error) => {
      addToast({
        type: 'error',
        title: 'Deployment Failed',
        description: getApiErrorMessage(error),
      });
    },
  });

  // Request mutation
  const requestMutation = useMutation({
    mutationFn: async (data: typeof requestForm) => {
      const response = await apiClient.post('/approved-vendors/request', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-requests'] });
      queryClient.invalidateQueries({ queryKey: ['approved-vendor-stats'] });
      setShowRequestModal(false);
      resetRequestForm();
      addToast({
        type: 'success',
        title: 'Request Submitted',
        description: 'Your tool evaluation request has been submitted for review.',
      });
    },
    onError: (error) => {
      addToast({
        type: 'error',
        title: 'Request Failed',
        description: getApiErrorMessage(error),
      });
    },
  });

  const resetDeployForm = () => {
    setDeployForm({
      use_case_id: '',
      department: '',
      team: '',
      data_classification: '',
      accept_conditions: false,
    });
    setDeployWizardStep(1);
    setSelectedVendor(null);
  };

  const resetRequestForm = () => {
    setRequestForm({
      tool_name: '',
      website: '',
      description: '',
      use_case_description: '',
      business_justification: '',
      department: '',
      urgency: 'medium',
    });
  };

  const handleOpenDeployModal = (vendor: ApprovedVendor) => {
    setSelectedVendor(vendor);
    setShowDeployModal(true);
  };

  const handleDeploy = () => {
    if (!selectedVendor) return;
    deployMutation.mutate({
      vendorId: selectedVendor.id,
      data: deployForm,
    });
  };

  const handleRequestSubmit = () => {
    if (!requestForm.tool_name.trim()) {
      addToast({ type: 'error', title: 'Validation Error', description: 'Tool name is required.' });
      return;
    }
    if (!requestForm.description.trim()) {
      addToast({ type: 'error', title: 'Validation Error', description: 'Description is required.' });
      return;
    }
    if (!requestForm.use_case_description.trim()) {
      addToast({ type: 'error', title: 'Validation Error', description: 'Use case description is required.' });
      return;
    }
    if (!requestForm.business_justification.trim()) {
      addToast({ type: 'error', title: 'Validation Error', description: 'Business justification is required.' });
      return;
    }
    if (!requestForm.department) {
      addToast({ type: 'error', title: 'Validation Error', description: 'Department is required.' });
      return;
    }
    requestMutation.mutate(requestForm);
  };

  const vendors = vendorsResponse?.data || [];
  const deployments = deploymentsResponse?.data || [];
  const requests = requestsResponse?.data || [];

  const filteredVendors = vendors.filter((vendor) => {
    const matchesSearch =
      !searchQuery ||
      vendor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      vendor.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || vendor.approval_status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <motion.div
      className="space-y-6 pb-8"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-5xl font-bold tracking-tighter text-white neon-text mb-2">
            APPROVED<span className="text-primary">AI</span>
          </h1>
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <motion.span
                className="w-2 h-2 rounded-full bg-emerald-500"
                animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              REGISTRY ACTIVE
            </span>
            <span className="text-white/10">|</span>
            <span className="font-mono text-primary/80">
              Self-Service AI Tool Deployment
            </span>
          </div>
        </div>
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button
            onClick={() => setShowRequestModal(true)}
            className="bg-primary/20 border border-primary/50 hover:bg-primary/30 hover:glow-teal transition-all duration-300"
          >
            <Plus className="h-4 w-4 mr-2" />
            Request New Tool
          </Button>
        </motion.div>
      </motion.div>

      {/* Stats Cards */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-3 lg:grid-cols-5">
        <StatCard
          title="Total Approved"
          value={stats?.total_approved || 0}
          icon={CheckCircle}
          className="border-l-4 border-l-emerald-500"
          isLoading={statsLoading}
        />
        <StatCard
          title="Active Deployments"
          value={stats?.active_deployments || 0}
          icon={Rocket}
          className="border-l-4 border-l-blue-500"
          isLoading={statsLoading}
        />
        <StatCard
          title="Pending Requests"
          value={stats?.pending_requests || 0}
          icon={Clock}
          className="border-l-4 border-l-yellow-500"
          isLoading={statsLoading}
        />
        <StatCard
          title="Conditional"
          value={stats?.conditional_approvals || 0}
          icon={AlertTriangle}
          className="border-l-4 border-l-orange-500"
          isLoading={statsLoading}
        />
        <StatCard
          title="Expiring Soon"
          value={stats?.expiring_soon || 0}
          icon={Shield}
          className="border-l-4 border-l-red-500"
          isLoading={statsLoading}
        />
      </motion.div>

      {/* Tabs */}
      <motion.div variants={itemVariants} className="flex items-center gap-2 border-b border-white/10 pb-1">
        {[
          { id: 'browse' as const, label: 'Browse Approved', icon: Building2 },
          { id: 'deployments' as const, label: 'My Deployments', icon: Rocket },
          { id: 'requests' as const, label: 'My Requests', icon: FileText },
        ].map((tab) => (
          <motion.button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={cn(
              'flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all rounded-t-lg',
              activeTab === tab.id
                ? 'bg-primary/20 text-primary border-b-2 border-primary'
                : 'text-muted-foreground hover:text-white hover:bg-white/5'
            )}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </motion.button>
        ))}
      </motion.div>

      {/* Browse Tab Content */}
      {activeTab === 'browse' && (
        <>
          {/* Filters */}
          <motion.div variants={itemVariants} className="flex flex-wrap gap-4 items-center">
            <div className="relative flex-1 min-w-[250px] max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search vendors by name or category..."
                className="pl-9 bg-white/5 border-white/10 focus:border-primary/50 focus:glow-teal transition-all"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Status:</span>
              {(['all', 'approved', 'conditional', 'expired'] as const).map((status) => (
                <motion.button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={cn(
                    'rounded-full px-3 py-1 text-xs font-medium transition-colors border',
                    statusFilter === status
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'bg-muted/50 text-muted-foreground border-white/10 hover:bg-muted/80'
                  )}
                >
                  {status === 'all' ? 'All' : approvalStatusConfig[status].label}
                </motion.button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <Briefcase className="h-4 w-4 text-muted-foreground" />
              <select
                className="h-9 rounded-md border border-white/10 bg-white/5 px-3 py-1 text-sm text-white focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50"
                value={departmentFilter}
                onChange={(e) => setDepartmentFilter(e.target.value)}
              >
                <option value="all">All Departments</option>
                {departments.map((dept) => (
                  <option key={dept} value={dept}>
                    {dept}
                  </option>
                ))}
              </select>
            </div>
          </motion.div>

          {/* Vendor Cards Grid */}
          {vendorsLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          ) : filteredVendors.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <Card className="glass-panel-liquid">
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <motion.div
                    animate={{ y: [0, -10, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <Building2 className="h-12 w-12 text-muted-foreground mb-4" />
                  </motion.div>
                  <h3 className="text-lg font-medium mb-2 text-white">No approved vendors found</h3>
                  <p className="text-muted-foreground text-center mb-4">
                    {searchQuery || statusFilter !== 'all'
                      ? 'Try adjusting your search or filters.'
                      : 'No AI tools have been approved yet.'}
                  </p>
                  <Button
                    onClick={() => setShowRequestModal(true)}
                    className="bg-primary/20 border border-primary/50 hover:bg-primary/30"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Request a Tool
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          ) : (
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
            >
              <AnimatePresence mode="popLayout">
                {filteredVendors.map((vendor, index) => (
                  <VendorCard
                    key={vendor.id}
                    vendor={vendor}
                    index={index}
                    onDeploy={() => handleOpenDeployModal(vendor)}
                  />
                ))}
              </AnimatePresence>
            </motion.div>
          )}
        </>
      )}

      {/* Deployments Tab Content */}
      {activeTab === 'deployments' && (
        <motion.div variants={itemVariants}>
          {deploymentsLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          ) : deployments.length === 0 ? (
            <Card className="glass-panel-liquid">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Rocket className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2 text-white">No active deployments</h3>
                <p className="text-muted-foreground text-center mb-4">
                  You haven't deployed any approved AI tools yet.
                </p>
                <Button
                  onClick={() => setActiveTab('browse')}
                  className="bg-primary/20 border border-primary/50 hover:bg-primary/30"
                >
                  Browse Approved Tools
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {deployments.map((deployment) => (
                <DeploymentCard key={deployment.id} deployment={deployment} />
              ))}
            </div>
          )}
        </motion.div>
      )}

      {/* Requests Tab Content */}
      {activeTab === 'requests' && (
        <motion.div variants={itemVariants}>
          {requestsLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          ) : requests.length === 0 ? (
            <Card className="glass-panel-liquid">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2 text-white">No pending requests</h3>
                <p className="text-muted-foreground text-center mb-4">
                  You haven't submitted any tool evaluation requests.
                </p>
                <Button
                  onClick={() => setShowRequestModal(true)}
                  className="bg-primary/20 border border-primary/50 hover:bg-primary/30"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Request New Tool
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {requests.map((request) => (
                <RequestCard key={request.id} request={request} />
              ))}
            </div>
          )}
        </motion.div>
      )}

      {/* Deploy Modal */}
      <Dialog open={showDeployModal} onOpenChange={(open) => { if (!open) resetDeployForm(); setShowDeployModal(open); }}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Rocket className="h-5 w-5 text-primary" />
              Deploy {selectedVendor?.name}
            </DialogTitle>
            <DialogDescription>
              Step {deployWizardStep} of 4: {['Select Use Case', 'Team Details', 'Data Classification', 'Confirm'][deployWizardStep - 1]}
            </DialogDescription>
          </DialogHeader>

          {/* Progress Bar */}
          <div className="h-2 bg-muted rounded-full overflow-hidden mb-4">
            <motion.div
              className="h-full bg-primary"
              initial={{ width: 0 }}
              animate={{ width: `${(deployWizardStep / 4) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>

          <div className="py-4 space-y-4">
            {/* Step 1: Select Use Case */}
            {deployWizardStep === 1 && selectedVendor && (
              <div className="space-y-4">
                <Label>Select Use Case *</Label>
                <div className="space-y-2">
                  {selectedVendor.approved_use_cases.map((useCase) => (
                    <motion.div
                      key={useCase.id}
                      whileHover={{ x: 4 }}
                      className={cn(
                        'flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors',
                        deployForm.use_case_id === useCase.id
                          ? 'bg-primary/10 border-primary/30'
                          : 'bg-card hover:bg-muted/50 border-white/10'
                      )}
                      onClick={() => setDeployForm({ ...deployForm, use_case_id: useCase.id })}
                    >
                      <div
                        className={cn(
                          'flex items-center justify-center w-5 h-5 rounded border mt-0.5',
                          deployForm.use_case_id === useCase.id
                            ? 'bg-primary border-primary'
                            : 'border-muted-foreground/30'
                        )}
                      >
                        {deployForm.use_case_id === useCase.id && <Check className="h-3 w-3 text-white" />}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{useCase.name}</p>
                        <p className="text-xs text-muted-foreground mt-1">{useCase.description}</p>
                        <Badge variant="outline" className={cn('mt-2 text-xs', dataClassificationConfig[useCase.data_classification].color)}>
                          {dataClassificationConfig[useCase.data_classification].label}
                        </Badge>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Step 2: Team Details */}
            {deployWizardStep === 2 && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="department">Department *</Label>
                  <select
                    id="department"
                    className="mt-2 flex h-10 w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50"
                    value={deployForm.department}
                    onChange={(e) => setDeployForm({ ...deployForm, department: e.target.value })}
                  >
                    <option value="">Select department...</option>
                    {departments.map((dept) => (
                      <option key={dept} value={dept}>
                        {dept}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label htmlFor="team">Team Name (Optional)</Label>
                  <Input
                    id="team"
                    placeholder="e.g., Frontend Team, Analytics"
                    className="mt-2 bg-white/5 border-white/10"
                    value={deployForm.team}
                    onChange={(e) => setDeployForm({ ...deployForm, team: e.target.value })}
                  />
                </div>
              </div>
            )}

            {/* Step 3: Data Classification */}
            {deployWizardStep === 3 && (
              <div className="space-y-4">
                <Label>Confirm Data Classification *</Label>
                <p className="text-sm text-muted-foreground">
                  Select the highest level of data classification that will be processed by this tool.
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {(Object.keys(dataClassificationConfig) as DataClassification[]).map((classification) => (
                    <motion.div
                      key={classification}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={cn(
                        'p-3 rounded-lg border cursor-pointer transition-colors text-center',
                        deployForm.data_classification === classification
                          ? 'bg-primary/10 border-primary/30'
                          : 'bg-card hover:bg-muted/50 border-white/10'
                      )}
                      onClick={() => setDeployForm({ ...deployForm, data_classification: classification })}
                    >
                      <Database className={cn('h-5 w-5 mx-auto mb-2', dataClassificationConfig[classification].color.split(' ')[0])} />
                      <p className="font-medium text-sm">{dataClassificationConfig[classification].label}</p>
                    </motion.div>
                  ))}
                </div>
                {selectedVendor && deployForm.data_classification && (
                  <div className={cn(
                    'p-3 rounded-lg border',
                    dataClassificationConfig[deployForm.data_classification].color.includes('red') ||
                    dataClassificationConfig[deployForm.data_classification].color.includes('yellow')
                      ? 'bg-yellow-500/10 border-yellow-500/30'
                      : 'bg-emerald-500/10 border-emerald-500/30'
                  )}>
                    <p className="text-xs">
                      {deployForm.data_classification === selectedVendor.data_classification_limit ? (
                        <span className="text-yellow-400">[!] This is the maximum allowed classification for this vendor.</span>
                      ) : (
                        <span className="text-emerald-400">[+] Classification is within vendor's approved limit.</span>
                      )}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Step 4: Confirm */}
            {deployWizardStep === 4 && selectedVendor && (
              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-muted/50 border border-white/10">
                  <h4 className="font-medium mb-3">Deployment Summary</h4>
                  <dl className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <dt className="text-muted-foreground">Vendor:</dt>
                      <dd className="font-medium">{selectedVendor.name}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-muted-foreground">Use Case:</dt>
                      <dd className="font-medium">
                        {selectedVendor.approved_use_cases.find((uc) => uc.id === deployForm.use_case_id)?.name}
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-muted-foreground">Department:</dt>
                      <dd className="font-medium">{deployForm.department}</dd>
                    </div>
                    {deployForm.team && (
                      <div className="flex justify-between">
                        <dt className="text-muted-foreground">Team:</dt>
                        <dd className="font-medium">{deployForm.team}</dd>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <dt className="text-muted-foreground">Data Classification:</dt>
                      <dd>
                        <Badge variant="outline" className={cn('text-xs', dataClassificationConfig[deployForm.data_classification as DataClassification].color)}>
                          {dataClassificationConfig[deployForm.data_classification as DataClassification].label}
                        </Badge>
                      </dd>
                    </div>
                  </dl>
                </div>

                {selectedVendor.conditions && selectedVendor.conditions.length > 0 && (
                  <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                    <h4 className="font-medium text-yellow-400 mb-2 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      Conditions of Use
                    </h4>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {selectedVendor.conditions.map((condition, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-yellow-400">[*]</span>
                          {condition}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <motion.div
                  whileHover={{ x: 4 }}
                  className={cn(
                    'flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors',
                    deployForm.accept_conditions
                      ? 'bg-emerald-500/10 border-emerald-500/30'
                      : 'bg-card hover:bg-muted/50 border-white/10'
                  )}
                  onClick={() => setDeployForm({ ...deployForm, accept_conditions: !deployForm.accept_conditions })}
                >
                  <div
                    className={cn(
                      'flex items-center justify-center w-5 h-5 rounded border',
                      deployForm.accept_conditions
                        ? 'bg-emerald-500 border-emerald-500'
                        : 'border-muted-foreground/30'
                    )}
                  >
                    {deployForm.accept_conditions && <Check className="h-3 w-3 text-white" />}
                  </div>
                  <span className="text-sm">
                    I accept the conditions and confirm the deployment details are accurate.
                  </span>
                </motion.div>
              </div>
            )}
          </div>

          <DialogFooter className="flex gap-2">
            {deployWizardStep > 1 && (
              <Button variant="outline" onClick={() => setDeployWizardStep((s) => s - 1)}>
                Back
              </Button>
            )}
            <Button variant="outline" onClick={() => { resetDeployForm(); setShowDeployModal(false); }}>
              Cancel
            </Button>
            {deployWizardStep < 4 ? (
              <Button
                onClick={() => setDeployWizardStep((s) => s + 1)}
                disabled={
                  (deployWizardStep === 1 && !deployForm.use_case_id) ||
                  (deployWizardStep === 2 && !deployForm.department) ||
                  (deployWizardStep === 3 && !deployForm.data_classification)
                }
              >
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            ) : (
              <Button
                onClick={handleDeploy}
                disabled={!deployForm.accept_conditions || deployMutation.isPending}
              >
                {deployMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                <Rocket className="h-4 w-4 mr-2" />
                Deploy
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Request New Tool Modal */}
      <Dialog open={showRequestModal} onOpenChange={(open) => { if (!open) resetRequestForm(); setShowRequestModal(open); }}>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5 text-primary" />
              Request New AI Tool Evaluation
            </DialogTitle>
            <DialogDescription>
              Submit a request to evaluate a new AI tool for organizational use.
            </DialogDescription>
          </DialogHeader>

          <div className="py-4 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="tool_name">Tool Name *</Label>
                <Input
                  id="tool_name"
                  placeholder="e.g., ChatGPT, Midjourney"
                  className="mt-2 bg-white/5 border-white/10"
                  value={requestForm.tool_name}
                  onChange={(e) => setRequestForm({ ...requestForm, tool_name: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="website">Website</Label>
                <Input
                  id="website"
                  placeholder="https://example.com"
                  className="mt-2 bg-white/5 border-white/10"
                  value={requestForm.website}
                  onChange={(e) => setRequestForm({ ...requestForm, website: e.target.value })}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="description">Tool Description *</Label>
              <textarea
                id="description"
                placeholder="Briefly describe what this tool does..."
                className="mt-2 flex min-h-[80px] w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm placeholder:text-muted-foreground focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50"
                value={requestForm.description}
                onChange={(e) => setRequestForm({ ...requestForm, description: e.target.value })}
              />
            </div>

            <div>
              <Label htmlFor="use_case">Use Case Description *</Label>
              <textarea
                id="use_case"
                placeholder="How do you plan to use this tool? What problems will it solve?"
                className="mt-2 flex min-h-[80px] w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm placeholder:text-muted-foreground focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50"
                value={requestForm.use_case_description}
                onChange={(e) => setRequestForm({ ...requestForm, use_case_description: e.target.value })}
              />
            </div>

            <div>
              <Label htmlFor="justification">Business Justification *</Label>
              <textarea
                id="justification"
                placeholder="Why is this tool needed? What business value will it provide?"
                className="mt-2 flex min-h-[80px] w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm placeholder:text-muted-foreground focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50"
                value={requestForm.business_justification}
                onChange={(e) => setRequestForm({ ...requestForm, business_justification: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="req_department">Department *</Label>
                <select
                  id="req_department"
                  className="mt-2 flex h-10 w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50"
                  value={requestForm.department}
                  onChange={(e) => setRequestForm({ ...requestForm, department: e.target.value })}
                >
                  <option value="">Select department...</option>
                  {departments.map((dept) => (
                    <option key={dept} value={dept}>
                      {dept}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <Label htmlFor="urgency">Urgency Level</Label>
                <select
                  id="urgency"
                  className="mt-2 flex h-10 w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 text-sm focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50"
                  value={requestForm.urgency}
                  onChange={(e) => setRequestForm({ ...requestForm, urgency: e.target.value as UrgencyLevel })}
                >
                  <option value="low">Low - No rush</option>
                  <option value="medium">Medium - Standard</option>
                  <option value="high">High - Needed soon</option>
                  <option value="critical">Critical - Urgent</option>
                </select>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => { resetRequestForm(); setShowRequestModal(false); }}>
              Cancel
            </Button>
            <Button onClick={handleRequestSubmit} disabled={requestMutation.isPending}>
              {requestMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              <FileText className="h-4 w-4 mr-2" />
              Submit Request
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}

// Vendor Card Component
function VendorCard({
  vendor,
  index,
  onDeploy,
}: {
  vendor: ApprovedVendor;
  index: number;
  onDeploy: () => void;
}) {
  const StatusIcon = approvalStatusConfig[vendor.approval_status].icon;

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -4, scale: 1.02 }}
      className="group"
    >
      <Card className="glass-panel-liquid border-0 h-full">
        <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-3">
          <div className="flex items-center gap-3">
            <motion.div
              whileHover={{ scale: 1.1, rotate: 5 }}
              className={cn(
                'flex h-10 w-10 items-center justify-center rounded-full border',
                approvalStatusConfig[vendor.approval_status].bgColor
              )}
            >
              <Building2 className={cn('h-5 w-5', approvalStatusConfig[vendor.approval_status].color)} />
            </motion.div>
            <div>
              <CardTitle className="text-lg text-white group-hover:text-primary transition-colors">
                {vendor.name}
              </CardTitle>
              <p className="text-xs text-muted-foreground">{vendor.category}</p>
            </div>
          </div>
          {vendor.website && (
            <a
              href={vendor.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-primary transition-colors"
              onClick={(e) => e.stopPropagation()}
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Status Badge */}
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className={cn('flex items-center gap-1', approvalStatusConfig[vendor.approval_status].bgColor)}
            >
              <StatusIcon className="h-3 w-3" />
              {approvalStatusConfig[vendor.approval_status].label}
            </Badge>
            <Badge
              variant="outline"
              className={dataClassificationConfig[vendor.data_classification_limit].color}
            >
              <Database className="h-3 w-3 mr-1" />
              {dataClassificationConfig[vendor.data_classification_limit].label}
            </Badge>
          </div>

          {/* Description */}
          {vendor.description && (
            <p className="text-sm text-muted-foreground line-clamp-2">{vendor.description}</p>
          )}

          {/* Use Cases Count */}
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-1 text-muted-foreground">
              <Zap className="h-3 w-3" />
              {vendor.approved_use_cases.length} Approved Use Cases
            </span>
            {vendor.expiry_date && (
              <span className="text-xs text-muted-foreground">
                Expires: {new Date(vendor.expiry_date).toLocaleDateString()}
              </span>
            )}
          </div>

          {/* Deploy Button */}
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button
              className="w-full bg-primary/20 border border-primary/50 hover:bg-primary/30"
              onClick={onDeploy}
              disabled={vendor.approval_status === 'expired'}
            >
              <Rocket className="h-4 w-4 mr-2" />
              {vendor.approval_status === 'expired' ? 'Approval Expired' : 'Deploy'}
            </Button>
          </motion.div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// Deployment Card Component
function DeploymentCard({ deployment }: { deployment: Deployment }) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.02 }}
      className="p-4 rounded-lg border bg-card glass-panel-liquid"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Rocket className="h-4 w-4 text-primary" />
          <span className="font-medium">{deployment.vendor_name}</span>
        </div>
        <Badge variant="outline" className={deploymentStatusConfig[deployment.status].color}>
          {deploymentStatusConfig[deployment.status].label}
        </Badge>
      </div>
      <p className="text-sm text-muted-foreground mb-2">{deployment.use_case_name}</p>
      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <Briefcase className="h-3 w-3" />
          {deployment.department}
        </span>
        <span className="flex items-center gap-1">
          <Database className="h-3 w-3" />
          {dataClassificationConfig[deployment.data_classification].label}
        </span>
      </div>
      <p className="text-xs text-muted-foreground mt-2">
        Deployed: {new Date(deployment.deployed_at).toLocaleDateString()}
      </p>
    </motion.div>
  );
}

// Request Card Component
function RequestCard({ request }: { request: ToolRequest }) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.02 }}
      className="p-4 rounded-lg border bg-card glass-panel-liquid"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-primary" />
          <span className="font-medium">{request.tool_name}</span>
        </div>
        <Badge variant="outline" className={requestStatusConfig[request.status].color}>
          {requestStatusConfig[request.status].label}
        </Badge>
      </div>
      <p className="text-sm text-muted-foreground mb-2 line-clamp-2">{request.description}</p>
      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <Briefcase className="h-3 w-3" />
          {request.department}
        </span>
        <Badge variant="outline" className={urgencyConfig[request.urgency].color}>
          {urgencyConfig[request.urgency].label}
        </Badge>
      </div>
      <p className="text-xs text-muted-foreground mt-2">
        Submitted: {new Date(request.submitted_at).toLocaleDateString()}
      </p>
      {request.reviewer_notes && (
        <div className="mt-3 p-2 rounded bg-muted/50 text-xs text-muted-foreground">
          <span className="font-medium">Reviewer Note:</span> {request.reviewer_notes}
        </div>
      )}
    </motion.div>
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
      whileHover={{ y: -4, scale: 1.02 }}
      transition={{ type: 'spring' as const, stiffness: 300, damping: 20 }}
      className={cn('rounded-lg border bg-card p-4 glass-panel-liquid', className)}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          {isLoading ? (
            <div className="mt-1 h-8 w-12 animate-pulse rounded bg-muted"></div>
          ) : (
            <motion.p
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: 'spring' as const, stiffness: 200, damping: 15 }}
              className="mt-1 text-2xl font-bold"
            >
              <AnimatedCounter value={value} duration={1.5} />
            </motion.p>
          )}
        </div>
        <motion.div
          initial={{ rotate: -180, opacity: 0 }}
          animate={{ rotate: 0, opacity: 1 }}
          transition={{ type: 'spring' as const, stiffness: 200, damping: 15, delay: 0.2 }}
        >
          <Icon className="h-8 w-8 text-muted-foreground/50" />
        </motion.div>
      </div>
    </motion.div>
  );
}

export default ApprovedVendors;
