import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BookOpen,
  Play,
  CheckCircle2,
  Clock,
  Users,
  ChevronRight,
  Loader2,
  Filter,
  Building2,
  Sparkles,
  Shield,
  AlertTriangle,
  X,
  Check,
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
    transition: { staggerChildren: 0.1, delayChildren: 0.1 },
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

// Types
type PlaybookPhase = 'tool_selection' | 'deployment' | 'regression_protection';
type TargetAudience = 'non_technical' | 'technical' | 'mixed';
type Department = 'marketing' | 'hr' | 'finance' | 'legal' | 'it' | 'security' | 'operations' | 'all';
type ProgressStatus = 'not_started' | 'in_progress' | 'pending_approval' | 'completed' | 'blocked';

interface ChecklistItem {
  id: string;
  text: string;
  completed: boolean;
}

interface Resource {
  title: string;
  url: string;
  type: 'doc' | 'video' | 'template' | 'link';
}

interface PlaybookStep {
  id: string;
  playbook_id: string;
  step_number: number;
  title: string;
  description?: string;
  instructions?: string;
  checklist: ChecklistItem[];
  resources: Resource[];
  estimated_minutes?: number;
  requires_approval: boolean;
  approval_roles: string[];
}

interface Playbook {
  id: string;
  name: string;
  description?: string;
  phase: PlaybookPhase;
  target_audience: TargetAudience;
  department: Department;
  version: string;
  is_active: boolean;
  estimated_minutes?: number;
  steps: PlaybookStep[];
  created_at: string;
}

interface PlaybookProgress {
  id: string;
  user_id: string;
  playbook_id: string;
  vendor_id?: string;
  current_step: number;
  status: ProgressStatus;
  step_completions: Record<string, { completed_at: string; checklist_state: Record<string, boolean> }>;
  started_at: string;
  completed_at?: string;
  playbook?: Playbook;
}

interface PlaybookListResponse {
  data: Playbook[];
  total: number;
}

interface ProgressListResponse {
  data: PlaybookProgress[];
  total: number;
}

interface Vendor {
  id: string;
  name: string;
}

// Phase colors and labels
const phaseConfig: Record<PlaybookPhase, { label: string; color: string; icon: React.ElementType }> = {
  tool_selection: { label: 'Tool Selection', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30', icon: Sparkles },
  deployment: { label: 'Secure Deployment', color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', icon: Shield },
  regression_protection: { label: 'Regression Protection', color: 'bg-purple-500/20 text-purple-400 border-purple-500/30', icon: AlertTriangle },
};

const audienceLabels: Record<TargetAudience, string> = {
  non_technical: 'Non-Technical',
  technical: 'Technical',
  mixed: 'Mixed Teams',
};

const departmentLabels: Record<Department, string> = {
  marketing: 'Marketing',
  hr: 'Human Resources',
  finance: 'Finance',
  legal: 'Legal',
  it: 'IT',
  security: 'Security',
  operations: 'Operations',
  all: 'All Departments',
};

const statusColors: Record<ProgressStatus, string> = {
  not_started: 'bg-gray-500/20 text-gray-400',
  in_progress: 'bg-blue-500/20 text-blue-400',
  pending_approval: 'bg-yellow-500/20 text-yellow-400',
  completed: 'bg-emerald-500/20 text-emerald-400',
  blocked: 'bg-red-500/20 text-red-400',
};

export function Playbooks() {
  const queryClient = useQueryClient();
  const [phaseFilter, setPhaseFilter] = useState<'all' | PlaybookPhase>('all');
  const [showStartModal, setShowStartModal] = useState(false);
  const [showWizardModal, setShowWizardModal] = useState(false);
  const [selectedPlaybook, setSelectedPlaybook] = useState<Playbook | null>(null);
  const [selectedProgress, setSelectedProgress] = useState<PlaybookProgress | null>(null);
  const [selectedVendorId, setSelectedVendorId] = useState<string>('');
  const [startError, setStartError] = useState<string | null>(null);

  // Fetch playbooks
  const { data: playbooksResponse, isLoading: playbooksLoading } = useQuery<PlaybookListResponse>({
    queryKey: ['playbooks', phaseFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (phaseFilter !== 'all') {
        params.append('phase', phaseFilter);
      }
      const response = await apiClient.get(`/playbooks/?${params}`);
      return response.data;
    },
  });

  // Fetch user's progress
  const { data: progressResponse, isLoading: progressLoading } = useQuery<ProgressListResponse>({
    queryKey: ['playbook-progress'],
    queryFn: async () => {
      const response = await apiClient.get('/playbooks/progress/');
      return response.data;
    },
  });

  // Fetch vendors for selection
  const { data: vendorsResponse } = useQuery<{ data: Vendor[] }>({
    queryKey: ['vendors-list'],
    queryFn: async () => {
      const response = await apiClient.get('/vendors?limit=100');
      return response.data;
    },
  });

  // Start playbook mutation
  const startPlaybookMutation = useMutation({
    mutationFn: async ({ playbookId, vendorId }: { playbookId: string; vendorId?: string }) => {
      const response = await apiClient.post(`/playbooks/${playbookId}/start`, {
        vendor_id: vendorId || null,
      });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['playbook-progress'] });
      setShowStartModal(false);
      setSelectedVendorId('');
      setStartError(null);
      // Open wizard with the new progress
      setSelectedProgress(data);
      setShowWizardModal(true);
    },
    onError: (error) => {
      setStartError(getApiErrorMessage(error));
    },
  });

  // Complete step mutation
  const completeStepMutation = useMutation({
    mutationFn: async ({
      progressId,
      stepNumber,
      checklistState,
      notes,
    }: {
      progressId: string;
      stepNumber: number;
      checklistState: Record<string, boolean>;
      notes?: string;
    }) => {
      const response = await apiClient.post(`/playbooks/progress/${progressId}/complete-step`, {
        step_number: stepNumber,
        checklist_state: checklistState,
        notes,
      });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['playbook-progress'] });
      setSelectedProgress(data);
    },
  });

  const handleStartPlaybook = (playbook: Playbook) => {
    setSelectedPlaybook(playbook);
    setShowStartModal(true);
  };

  const handleContinuePlaybook = (progress: PlaybookProgress) => {
    setSelectedProgress(progress);
    setShowWizardModal(true);
  };

  const handleConfirmStart = () => {
    if (!selectedPlaybook) return;
    startPlaybookMutation.mutate({
      playbookId: selectedPlaybook.id,
      vendorId: selectedVendorId || undefined,
    });
  };

  const playbooks = playbooksResponse?.data || [];
  const progressList = progressResponse?.data || [];
  const vendors = vendorsResponse?.data || [];
  const isLoading = playbooksLoading || progressLoading;

  // Stats
  const stats = {
    total: playbooks.length,
    inProgress: progressList.filter((p) => p.status === 'in_progress').length,
    completed: progressList.filter((p) => p.status === 'completed').length,
    pendingApproval: progressList.filter((p) => p.status === 'pending_approval').length,
  };

  return (
    <motion.div
      className="space-y-6"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold neon-text">AI Governance Playbooks</h1>
              <motion.div
                className="flex items-center gap-2 px-3 py-1 rounded-full bg-obsidian-teal/10 border border-obsidian-teal/30"
                animate={{ opacity: [0.7, 1, 0.7] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              >
                <motion.span
                  className="w-2 h-2 rounded-full bg-obsidian-teal"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                />
                <span className="text-xs text-obsidian-teal font-medium">
                  <AnimatedCounter value={stats.inProgress} duration={1} /> In Progress
                </span>
              </motion.div>
            </div>
            <p className="text-muted-foreground">
              Guided workflows for safe AI tool adoption across your organization
            </p>
          </div>
        </div>
      </motion.div>

      {/* Start Playbook Modal */}
      <Dialog open={showStartModal} onOpenChange={setShowStartModal}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Start Playbook</DialogTitle>
            <DialogDescription>
              Begin the {selectedPlaybook?.name} workflow
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {selectedPlaybook && (
              <div className="p-4 rounded-lg bg-muted/50 border">
                <div className="flex items-center gap-2 mb-2">
                  {(() => {
                    const PhaseIcon = phaseConfig[selectedPlaybook.phase].icon;
                    return <PhaseIcon className="h-4 w-4" />;
                  })()}
                  <span className={cn('text-xs px-2 py-0.5 rounded-full border', phaseConfig[selectedPlaybook.phase].color)}>
                    {phaseConfig[selectedPlaybook.phase].label}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">{selectedPlaybook.description}</p>
                <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <BookOpen className="h-3 w-3" />
                    {selectedPlaybook.steps?.length || 0} Steps
                  </span>
                  {selectedPlaybook.estimated_minutes && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      ~{selectedPlaybook.estimated_minutes} min
                    </span>
                  )}
                </div>
              </div>
            )}
            <div className="grid gap-2">
              <Label htmlFor="vendor">Associate with Vendor (Optional)</Label>
              <select
                id="vendor"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={selectedVendorId}
                onChange={(e) => setSelectedVendorId(e.target.value)}
              >
                <option value="">No vendor association</option>
                {vendors.map((vendor) => (
                  <option key={vendor.id} value={vendor.id}>
                    {vendor.name}
                  </option>
                ))}
              </select>
              <p className="text-xs text-muted-foreground">
                Link this playbook run to a specific AI vendor for tracking
              </p>
            </div>
            {startError && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {startError}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowStartModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleConfirmStart} disabled={startPlaybookMutation.isPending}>
              {startPlaybookMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              <Play className="mr-2 h-4 w-4" />
              Start Playbook
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Playbook Wizard Modal */}
      <PlaybookWizard
        open={showWizardModal}
        onOpenChange={setShowWizardModal}
        progress={selectedProgress}
        onCompleteStep={(stepNumber, checklistState, notes) => {
          if (!selectedProgress) return;
          completeStepMutation.mutate({
            progressId: selectedProgress.id,
            stepNumber,
            checklistState,
            notes,
          });
        }}
        isSubmitting={completeStepMutation.isPending}
      />

      {/* Stats Cards */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Available Playbooks"
          value={stats.total}
          icon={BookOpen}
          className="border-l-4 border-l-blue-500"
          isLoading={isLoading}
        />
        <StatCard
          title="In Progress"
          value={stats.inProgress}
          icon={Play}
          className="border-l-4 border-l-yellow-500"
          isLoading={isLoading}
        />
        <StatCard
          title="Pending Approval"
          value={stats.pendingApproval}
          icon={Clock}
          className="border-l-4 border-l-orange-500"
          isLoading={isLoading}
        />
        <StatCard
          title="Completed"
          value={stats.completed}
          icon={CheckCircle2}
          className="border-l-4 border-l-emerald-500"
          isLoading={isLoading}
        />
      </motion.div>

      {/* My Progress Section */}
      {progressList.length > 0 && (
        <motion.div variants={itemVariants}>
          <h2 className="text-lg font-semibold mb-4">My Progress</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {progressList.map((progress) => (
              <motion.div
                key={progress.id}
                whileHover={{ y: -4, scale: 1.02 }}
                className="p-4 rounded-lg border bg-card glass-panel-liquid cursor-pointer"
                onClick={() => handleContinuePlaybook(progress)}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className={cn('text-xs px-2 py-0.5 rounded-full', statusColors[progress.status])}>
                    {progress.status.replace('_', ' ').toUpperCase()}
                  </span>
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                </div>
                <h3 className="font-medium mb-1">{progress.playbook?.name || 'Loading...'}</h3>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span>Step {progress.current_step} of {progress.playbook?.steps?.length || '?'}</span>
                </div>
                {/* Progress bar */}
                <div className="mt-3 h-1.5 bg-muted rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-obsidian-teal"
                    initial={{ width: 0 }}
                    animate={{
                      width: `${((progress.current_step - 1) / (progress.playbook?.steps?.length || 1)) * 100}%`,
                    }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Filter Bar */}
      <motion.div variants={itemVariants} className="flex items-center gap-2">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Phase:</span>
        {(['all', 'tool_selection', 'deployment', 'regression_protection'] as const).map((phase) => (
          <motion.button
            key={phase}
            onClick={() => setPhaseFilter(phase)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={cn(
              'rounded-full px-3 py-1 text-xs font-medium transition-colors',
              phaseFilter === phase
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            )}
          >
            {phase === 'all' ? 'All Phases' : phaseConfig[phase].label}
          </motion.button>
        ))}
      </motion.div>

      {/* Playbooks Grid */}
      <motion.div variants={itemVariants}>
        <h2 className="text-lg font-semibold mb-4">Available Playbooks</h2>
        {playbooksLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
        ) : playbooks.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-12 rounded-lg border bg-card glass-panel-liquid"
          >
            <BookOpen className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No playbooks found</h3>
            <p className="text-muted-foreground text-center">
              {phaseFilter === 'all'
                ? 'No playbooks are available yet.'
                : `No playbooks in the "${phaseConfig[phaseFilter].label}" phase.`}
            </p>
          </motion.div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <AnimatePresence mode="popLayout">
              {playbooks.map((playbook, index) => (
                <PlaybookCard
                  key={playbook.id}
                  playbook={playbook}
                  index={index}
                  onStart={() => handleStartPlaybook(playbook)}
                />
              ))}
            </AnimatePresence>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}

// Playbook Card Component
function PlaybookCard({
  playbook,
  index,
  onStart,
}: {
  playbook: Playbook;
  index: number;
  onStart: () => void;
}) {
  const PhaseIcon = phaseConfig[playbook.phase].icon;

  return (
    <motion.div
      variants={itemVariants}
      initial="hidden"
      animate="visible"
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -4, scale: 1.02 }}
      className="p-5 rounded-lg border bg-card glass-panel-liquid group"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={cn('p-2 rounded-lg', phaseConfig[playbook.phase].color)}>
            <PhaseIcon className="h-4 w-4" />
          </div>
          <Badge variant="outline" className={phaseConfig[playbook.phase].color}>
            {phaseConfig[playbook.phase].label}
          </Badge>
        </div>
        <span className="text-xs text-muted-foreground">v{playbook.version}</span>
      </div>

      {/* Content */}
      <h3 className="font-semibold text-lg mb-2 group-hover:text-obsidian-teal transition-colors">
        {playbook.name}
      </h3>
      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
        {playbook.description}
      </p>

      {/* Meta */}
      <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
        <span className="flex items-center gap-1">
          <BookOpen className="h-3 w-3" />
          {playbook.steps?.length || 0} Steps
        </span>
        {playbook.estimated_minutes && (
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            ~{playbook.estimated_minutes} min
          </span>
        )}
        <span className="flex items-center gap-1">
          <Users className="h-3 w-3" />
          {audienceLabels[playbook.target_audience]}
        </span>
      </div>

      {/* Department Badge */}
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1 text-xs text-muted-foreground">
          <Building2 className="h-3 w-3" />
          {departmentLabels[playbook.department]}
        </span>
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Button size="sm" onClick={onStart}>
            <Play className="h-3 w-3 mr-1" />
            Start
          </Button>
        </motion.div>
      </div>
    </motion.div>
  );
}

// Playbook Wizard Component
function PlaybookWizard({
  open,
  onOpenChange,
  progress,
  onCompleteStep,
  isSubmitting,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  progress: PlaybookProgress | null;
  onCompleteStep: (stepNumber: number, checklistState: Record<string, boolean>, notes?: string) => void;
  isSubmitting: boolean;
}) {
  const [checklistState, setChecklistState] = useState<Record<string, boolean>>({});
  const [notes, setNotes] = useState('');

  if (!progress || !progress.playbook) {
    return null;
  }

  const playbook = progress.playbook;
  const currentStepIndex = progress.current_step - 1;
  const currentStep = playbook.steps?.[currentStepIndex];

  if (!currentStep) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[700px]">
          <DialogHeader>
            <DialogTitle>Playbook Complete!</DialogTitle>
          </DialogHeader>
          <div className="py-8 text-center">
            <CheckCircle2 className="h-16 w-16 text-emerald-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Congratulations!</h3>
            <p className="text-muted-foreground">
              You have completed all steps in the {playbook.name} playbook.
            </p>
          </div>
          <DialogFooter>
            <Button onClick={() => onOpenChange(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  const allChecked = currentStep.checklist?.every((item) => checklistState[item.id]) ?? true;

  const handleToggleChecklist = (itemId: string) => {
    setChecklistState((prev) => ({
      ...prev,
      [itemId]: !prev[itemId],
    }));
  };

  const handleCompleteStep = () => {
    onCompleteStep(progress.current_step, checklistState, notes || undefined);
    setChecklistState({});
    setNotes('');
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="outline" className={phaseConfig[playbook.phase as PlaybookPhase].color}>
              {phaseConfig[playbook.phase as PlaybookPhase].label}
            </Badge>
            <span className="text-xs text-muted-foreground">
              Step {progress.current_step} of {playbook.steps?.length || 0}
            </span>
          </div>
          <DialogTitle>{currentStep.title}</DialogTitle>
          <DialogDescription>{currentStep.description}</DialogDescription>
        </DialogHeader>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-obsidian-teal"
              initial={{ width: 0 }}
              animate={{
                width: `${((progress.current_step - 1) / (playbook.steps?.length || 1)) * 100}%`,
              }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        {/* Instructions */}
        {currentStep.instructions && (
          <div className="mb-6 p-4 rounded-lg bg-muted/50 border">
            <h4 className="text-sm font-medium mb-2">Instructions</h4>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">
              {currentStep.instructions}
            </p>
          </div>
        )}

        {/* Checklist */}
        {currentStep.checklist && currentStep.checklist.length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium mb-3">Checklist</h4>
            <div className="space-y-2">
              {currentStep.checklist.map((item) => (
                <motion.div
                  key={item.id}
                  whileHover={{ x: 4 }}
                  className={cn(
                    'flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors',
                    checklistState[item.id]
                      ? 'bg-emerald-500/10 border-emerald-500/30'
                      : 'bg-card hover:bg-muted/50'
                  )}
                  onClick={() => handleToggleChecklist(item.id)}
                >
                  <div
                    className={cn(
                      'flex items-center justify-center w-5 h-5 rounded border transition-colors',
                      checklistState[item.id]
                        ? 'bg-emerald-500 border-emerald-500'
                        : 'border-muted-foreground/30'
                    )}
                  >
                    {checklistState[item.id] && <Check className="h-3 w-3 text-white" />}
                  </div>
                  <span
                    className={cn(
                      'text-sm',
                      checklistState[item.id] && 'line-through text-muted-foreground'
                    )}
                  >
                    {item.text}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Resources */}
        {currentStep.resources && currentStep.resources.length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium mb-3">Resources</h4>
            <div className="flex flex-wrap gap-2">
              {currentStep.resources.map((resource, idx) => (
                <a
                  key={idx}
                  href={resource.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 px-3 py-1.5 text-xs rounded-full bg-muted hover:bg-muted/80 transition-colors"
                >
                  <BookOpen className="h-3 w-3" />
                  {resource.title}
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Notes */}
        <div className="mb-6">
          <Label htmlFor="notes">Notes (Optional)</Label>
          <Input
            id="notes"
            placeholder="Add any notes or comments about this step..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="mt-2"
          />
        </div>

        {/* Approval Warning */}
        {currentStep.requires_approval && (
          <div className="mb-6 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
            <div className="flex items-center gap-2 text-yellow-400">
              <AlertTriangle className="h-4 w-4" />
              <span className="text-sm font-medium">Approval Required</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Completing this step will require approval from: {currentStep.approval_roles?.join(', ') || 'Admin'}
            </p>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            <X className="h-4 w-4 mr-2" />
            Save & Exit
          </Button>
          <Button
            onClick={handleCompleteStep}
            disabled={!allChecked || isSubmitting}
          >
            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            <CheckCircle2 className="mr-2 h-4 w-4" />
            Complete Step
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
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

export default Playbooks;
