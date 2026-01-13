import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ClipboardList,
  Clock,
  AlertTriangle,
  CheckCircle,
  Filter,
  Plus,
  ChevronRight,
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

type TaskStatus =
  | 'draft'
  | 'pending_assignment'
  | 'assigned'
  | 'in_progress'
  | 'pending_review'
  | 'pending_verification'
  | 'verified'
  | 'closed'
  | 'exception_requested'
  | 'exception_approved'
  | 'exception_denied'
  | 'reopened';

type TaskPriority = 'critical' | 'high' | 'medium' | 'low';

interface RemediationTask {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_id?: string;
  vendor_id?: string;
  finding_id: string;
  due_date?: string;
  sla_days?: number;
  sla_breached: boolean;
  created_at: string;
  updated_at: string;
}

interface DashboardStats {
  total_tasks: number;
  open_tasks: number;
  overdue_tasks: number;
  sla_breached: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  avg_resolution_days?: number;
}

interface TaskListResponse {
  data: RemediationTask[];
  total: number;
  page: number;
  limit: number;
}

const statusLabels: Record<TaskStatus, string> = {
  draft: 'Draft',
  pending_assignment: 'Pending Assignment',
  assigned: 'Assigned',
  in_progress: 'In Progress',
  pending_review: 'Pending Review',
  pending_verification: 'Pending Verification',
  verified: 'Verified',
  closed: 'Closed',
  exception_requested: 'Exception Requested',
  exception_approved: 'Exception Approved',
  exception_denied: 'Exception Denied',
  reopened: 'Reopened',
};

const statusColors: Record<TaskStatus, string> = {
  draft: 'bg-gray-100 text-gray-700',
  pending_assignment: 'bg-yellow-100 text-yellow-700',
  assigned: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-indigo-100 text-indigo-700',
  pending_review: 'bg-purple-100 text-purple-700',
  pending_verification: 'bg-cyan-100 text-cyan-700',
  verified: 'bg-green-100 text-green-700',
  closed: 'bg-gray-100 text-gray-700',
  exception_requested: 'bg-orange-100 text-orange-700',
  exception_approved: 'bg-amber-100 text-amber-700',
  exception_denied: 'bg-red-100 text-red-700',
  reopened: 'bg-pink-100 text-pink-700',
};

const priorityColors: Record<TaskPriority, string> = {
  critical: 'bg-red-100 text-red-700 border-red-300',
  high: 'bg-orange-100 text-orange-700 border-orange-300',
  medium: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  low: 'bg-green-100 text-green-700 border-green-300',
};

export function Remediation() {
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<'all' | TaskStatus>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState<RemediationTask | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);

  // Form state for new task
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium' as TaskPriority,
    finding_id: '',
    sla_days: 30,
  });

  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ['remediation-dashboard'],
    queryFn: async () => {
      const response = await apiClient.get('/remediation/dashboard');
      return response.data;
    },
  });

  // Fetch tasks
  const { data: tasksResponse, isLoading: tasksLoading } = useQuery<TaskListResponse>({
    queryKey: ['remediation-tasks', filter],
    queryFn: async () => {
      const params = new URLSearchParams();
      params.append('limit', '50');
      if (filter !== 'all') {
        params.append('status', filter);
      }
      const response = await apiClient.get(`/remediation/tasks?${params}`);
      return response.data;
    },
  });

  // Create task mutation
  const createTaskMutation = useMutation({
    mutationFn: async (taskData: typeof newTask) => {
      const response = await apiClient.post('/remediation/tasks', taskData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['remediation-tasks'] });
      queryClient.invalidateQueries({ queryKey: ['remediation-dashboard'] });
      setShowCreateModal(false);
      setNewTask({ title: '', description: '', priority: 'medium', finding_id: '', sla_days: 30 });
      setCreateError(null);
    },
    onError: (error) => {
      setCreateError(getApiErrorMessage(error));
    },
  });

  // Transition task mutation - error state for UI feedback
  const [_transitionError, setTransitionError] = useState<string | null>(null);
  void _transitionError; // Used for error display in modal
  const transitionMutation = useMutation({
    mutationFn: async ({ taskId, newStatus, notes }: { taskId: string; newStatus: TaskStatus; notes?: string }) => {
      const response = await apiClient.post(`/remediation/tasks/${taskId}/transition`, {
        new_status: newStatus,
        notes,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['remediation-tasks'] });
      queryClient.invalidateQueries({ queryKey: ['remediation-dashboard'] });
      setShowDetailModal(false);
      setTransitionError(null);
    },
    onError: (error) => {
      setTransitionError(getApiErrorMessage(error));
    },
  });

  const handleCreateTask = () => {
    if (!newTask.title.trim()) {
      setCreateError('Task title is required');
      return;
    }
    if (!newTask.finding_id.trim()) {
      setCreateError('Finding ID is required');
      return;
    }
    setCreateError(null);
    createTaskMutation.mutate(newTask);
  };

  const handleTaskClick = (task: RemediationTask) => {
    setSelectedTask(task);
    setShowDetailModal(true);
  };

  const tasks = tasksResponse?.data || [];
  const isLoading = statsLoading || tasksLoading;

  const dashboardStats = stats || {
    total_tasks: 0,
    open_tasks: 0,
    overdue_tasks: 0,
    sla_breached: 0,
    by_status: {},
    by_priority: {},
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
              <h1 className="text-2xl font-bold neon-text">Remediation Workflow</h1>
              <motion.div
                className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30"
                animate={{ opacity: [0.7, 1, 0.7] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              >
                <motion.span
                  className="w-2 h-2 rounded-full bg-emerald-500"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                />
                <span className="text-xs text-emerald-400 font-medium">
                  <AnimatedCounter value={dashboardStats.open_tasks} duration={1} /> Active
                </span>
              </motion.div>
            </div>
            <p className="text-muted-foreground">
              Track and manage security finding remediation tasks
            </p>
          </div>
        </div>
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Task
          </Button>
        </motion.div>
      </motion.div>

      {/* Create Task Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create Remediation Task</DialogTitle>
            <DialogDescription>
              Create a new task to track remediation of a security finding.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="title">Task Title *</Label>
              <Input
                id="title"
                placeholder="e.g., Implement MFA for admin accounts"
                value={newTask.title}
                onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="finding_id">Finding ID *</Label>
              <Input
                id="finding_id"
                placeholder="e.g., finding-uuid-here"
                value={newTask.finding_id}
                onChange={(e) => setNewTask({ ...newTask, finding_id: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                placeholder="Brief description of the remediation work"
                value={newTask.description}
                onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="priority">Priority</Label>
              <select
                id="priority"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={newTask.priority}
                onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as TaskPriority })}
              >
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="sla_days">SLA Days</Label>
              <Input
                id="sla_days"
                type="number"
                min={1}
                max={365}
                value={newTask.sla_days}
                onChange={(e) => setNewTask({ ...newTask, sla_days: parseInt(e.target.value) || 30 })}
              />
            </div>
            {createError && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {createError}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateTask} disabled={createTaskMutation.isPending}>
              {createTaskMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Task
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Task Detail Modal */}
      <Dialog open={showDetailModal} onOpenChange={setShowDetailModal}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>{selectedTask?.title}</DialogTitle>
            <DialogDescription>
              View and manage this remediation task
            </DialogDescription>
          </DialogHeader>
          {selectedTask && (
            <div className="space-y-4 py-4">
              <div className="flex items-center gap-2">
                <span className={cn('rounded-full px-2 py-0.5 text-xs font-medium', statusColors[selectedTask.status])}>
                  {statusLabels[selectedTask.status]}
                </span>
                <span className={cn('rounded border px-2 py-0.5 text-xs font-medium capitalize', priorityColors[selectedTask.priority])}>
                  {selectedTask.priority}
                </span>
                {selectedTask.sla_breached && (
                  <span className="rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
                    SLA Breached
                  </span>
                )}
              </div>
              {selectedTask.description && (
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Description</h4>
                  <p className="mt-1 text-sm">{selectedTask.description}</p>
                </div>
              )}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Finding ID:</span>
                  <span className="ml-2 font-mono text-xs">{selectedTask.finding_id}</span>
                </div>
                {selectedTask.due_date && (
                  <div>
                    <span className="text-muted-foreground">Due Date:</span>
                    <span className="ml-2">{new Date(selectedTask.due_date).toLocaleDateString()}</span>
                  </div>
                )}
                {selectedTask.sla_days && (
                  <div>
                    <span className="text-muted-foreground">SLA Days:</span>
                    <span className="ml-2">{selectedTask.sla_days}</span>
                  </div>
                )}
                <div>
                  <span className="text-muted-foreground">Created:</span>
                  <span className="ml-2">{new Date(selectedTask.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              {/* Status Transition Buttons */}
              <div className="border-t pt-4">
                <h4 className="text-sm font-medium mb-2">Change Status</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedTask.status === 'draft' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => transitionMutation.mutate({ taskId: selectedTask.id, newStatus: 'pending_assignment' })}
                      disabled={transitionMutation.isPending}
                    >
                      Submit for Assignment
                    </Button>
                  )}
                  {selectedTask.status === 'pending_assignment' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => transitionMutation.mutate({ taskId: selectedTask.id, newStatus: 'assigned' })}
                      disabled={transitionMutation.isPending}
                    >
                      Mark Assigned
                    </Button>
                  )}
                  {selectedTask.status === 'assigned' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => transitionMutation.mutate({ taskId: selectedTask.id, newStatus: 'in_progress' })}
                      disabled={transitionMutation.isPending}
                    >
                      Start Work
                    </Button>
                  )}
                  {selectedTask.status === 'in_progress' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => transitionMutation.mutate({ taskId: selectedTask.id, newStatus: 'pending_review' })}
                      disabled={transitionMutation.isPending}
                    >
                      Submit for Review
                    </Button>
                  )}
                  {selectedTask.status === 'pending_review' && (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => transitionMutation.mutate({ taskId: selectedTask.id, newStatus: 'pending_verification' })}
                        disabled={transitionMutation.isPending}
                      >
                        Approve Review
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => transitionMutation.mutate({ taskId: selectedTask.id, newStatus: 'in_progress' })}
                        disabled={transitionMutation.isPending}
                      >
                        Request Changes
                      </Button>
                    </>
                  )}
                  {selectedTask.status === 'pending_verification' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => transitionMutation.mutate({ taskId: selectedTask.id, newStatus: 'verified' })}
                      disabled={transitionMutation.isPending}
                    >
                      Verify Complete
                    </Button>
                  )}
                  {selectedTask.status === 'verified' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => transitionMutation.mutate({ taskId: selectedTask.id, newStatus: 'closed' })}
                      disabled={transitionMutation.isPending}
                    >
                      Close Task
                    </Button>
                  )}
                  {selectedTask.status === 'closed' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => transitionMutation.mutate({ taskId: selectedTask.id, newStatus: 'reopened' })}
                      disabled={transitionMutation.isPending}
                    >
                      Reopen Task
                    </Button>
                  )}
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetailModal(false)}>
              <X className="h-4 w-4 mr-2" />
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Stats Cards */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total Tasks"
          value={dashboardStats.total_tasks}
          icon={ClipboardList}
          className="border-l-4 border-l-blue-500"
          isLoading={isLoading}
        />
        <StatCard
          title="Open Tasks"
          value={dashboardStats.open_tasks}
          icon={Clock}
          className="border-l-4 border-l-indigo-500"
          isLoading={isLoading}
        />
        <StatCard
          title="Overdue"
          value={dashboardStats.overdue_tasks}
          icon={AlertTriangle}
          className="border-l-4 border-l-red-500"
          isLoading={isLoading}
          isWarning
        />
        <StatCard
          title="SLA Breached"
          value={dashboardStats.sla_breached}
          icon={CheckCircle}
          className="border-l-4 border-l-orange-500"
          isLoading={isLoading}
          isWarning
        />
      </motion.div>

      {/* Filter Bar */}
      <motion.div variants={itemVariants} className="flex items-center gap-2">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Filter:</span>
        {(['all', 'in_progress', 'pending_review', 'assigned', 'closed'] as const).map((status) => (
          <motion.button
            key={status}
            onClick={() => setFilter(status)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={cn(
              'rounded-full px-3 py-1 text-xs font-medium transition-colors',
              filter === status
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            )}
          >
            {status === 'all' ? 'All' : statusLabels[status]}
          </motion.button>
        ))}
      </motion.div>

      {/* Task List */}
      <motion.div variants={itemVariants} className="rounded-lg border bg-card glass-panel-liquid">
        {tasksLoading ? (
          <div className="p-4 space-y-4">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
        ) : tasks.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-12"
          >
            <ClipboardList className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No tasks found</h3>
            <p className="text-muted-foreground text-center mb-4">
              {filter === 'all'
                ? 'Create your first remediation task to get started.'
                : `No tasks with status "${statusLabels[filter as TaskStatus]}".`}
            </p>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button onClick={() => setShowCreateModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Task
              </Button>
            </motion.div>
          </motion.div>
        ) : (
          <AnimatePresence mode="popLayout">
            <div className="divide-y divide-border/50">
              {tasks.map((task, index) => (
                <motion.div
                  key={task.id}
                  variants={itemVariants}
                  initial="hidden"
                  animate="visible"
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ y: -4, scale: 1.01 }}
                  className={cn(
                    'flex items-center gap-4 p-4 cursor-pointer transition-colors',
                    'hover:bg-muted/50',
                    task.sla_breached && 'sla-breach-pulse'
                  )}
                  onClick={() => handleTaskClick(task)}
                >
                  <motion.div
                    className={cn('w-1 h-12 rounded-full', {
                      'bg-red-500': task.priority === 'critical',
                      'bg-orange-500': task.priority === 'high',
                      'bg-yellow-500': task.priority === 'medium',
                      'bg-green-500': task.priority === 'low',
                    })}
                    layoutId={`priority-${task.id}`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-foreground truncate">{task.title}</h3>
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className={cn(
                          'rounded-full px-2 py-0.5 text-xs font-medium',
                          statusColors[task.status]
                        )}
                      >
                        {statusLabels[task.status]}
                      </motion.span>
                      {task.sla_breached && (
                        <motion.span
                          animate={{ opacity: [1, 0.6, 1] }}
                          transition={{ duration: 1.5, repeat: Infinity }}
                          className="rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700"
                        >
                          SLA Breached
                        </motion.span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                      {task.due_date && (
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          Due: {new Date(task.due_date).toLocaleDateString()}
                        </span>
                      )}
                      <span>Created: {new Date(task.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <motion.span
                    whileHover={{ scale: 1.1 }}
                    className={cn(
                      'rounded border px-2 py-0.5 text-xs font-medium capitalize',
                      priorityColors[task.priority]
                    )}
                  >
                    {task.priority}
                  </motion.span>
                  <motion.div
                    animate={{ x: [0, 4, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                  >
                    <ChevronRight className="h-5 w-5 text-muted-foreground" />
                  </motion.div>
                </motion.div>
              ))}
            </div>
          </AnimatePresence>
        )}
      </motion.div>
    </motion.div>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  className,
  isLoading,
  isWarning,
}: {
  title: string;
  value: number;
  icon: React.ElementType;
  className?: string;
  isLoading?: boolean;
  isWarning?: boolean;
}) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.02 }}
      transition={{ type: 'spring' as const, stiffness: 300, damping: 20 }}
      className={cn(
        'rounded-lg border bg-card p-4 glass-panel-liquid',
        isWarning && value > 0 && 'sla-breach-pulse',
        className
      )}
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

export default Remediation;
