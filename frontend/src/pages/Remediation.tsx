import { useState } from 'react';
import {
  ClipboardList,
  Clock,
  AlertTriangle,
  CheckCircle,
  Filter,
  Plus,
  ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';

type TaskStatus =
  | 'draft'
  | 'pending_assignment'
  | 'assigned'
  | 'in_progress'
  | 'pending_review'
  | 'verified'
  | 'closed';

type TaskPriority = 'critical' | 'high' | 'medium' | 'low';

interface RemediationTask {
  id: string;
  title: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee?: string;
  dueDate?: string;
  slaDays?: number;
  findingId?: string;
  vendor?: string;
}

// Mock data for demonstration
const mockTasks: RemediationTask[] = [
  {
    id: '1',
    title: 'Implement MFA for admin accounts',
    status: 'in_progress',
    priority: 'critical',
    assignee: 'John Smith',
    dueDate: '2026-01-15',
    slaDays: 5,
    vendor: 'CloudVendor Inc',
  },
  {
    id: '2',
    title: 'Update data retention policy',
    status: 'pending_review',
    priority: 'high',
    assignee: 'Sarah Johnson',
    dueDate: '2026-01-20',
    slaDays: 10,
    vendor: 'DataCorp',
  },
  {
    id: '3',
    title: 'Enable encryption at rest for backups',
    status: 'assigned',
    priority: 'medium',
    assignee: 'Mike Chen',
    dueDate: '2026-01-25',
    slaDays: 15,
    vendor: 'BackupPro',
  },
  {
    id: '4',
    title: 'Review access control policies',
    status: 'pending_assignment',
    priority: 'low',
    dueDate: '2026-02-01',
    slaDays: 30,
    vendor: 'SecureAccess',
  },
];

const statusLabels: Record<TaskStatus, string> = {
  draft: 'Draft',
  pending_assignment: 'Pending Assignment',
  assigned: 'Assigned',
  in_progress: 'In Progress',
  pending_review: 'Pending Review',
  verified: 'Verified',
  closed: 'Closed',
};

const statusColors: Record<TaskStatus, string> = {
  draft: 'bg-gray-100 text-gray-700',
  pending_assignment: 'bg-yellow-100 text-yellow-700',
  assigned: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-indigo-100 text-indigo-700',
  pending_review: 'bg-purple-100 text-purple-700',
  verified: 'bg-green-100 text-green-700',
  closed: 'bg-gray-100 text-gray-700',
};

const priorityColors: Record<TaskPriority, string> = {
  critical: 'bg-red-100 text-red-700 border-red-300',
  high: 'bg-orange-100 text-orange-700 border-orange-300',
  medium: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  low: 'bg-green-100 text-green-700 border-green-300',
};

export function Remediation() {
  const [filter, setFilter] = useState<'all' | TaskStatus>('all');

  const filteredTasks =
    filter === 'all' ? mockTasks : mockTasks.filter((t) => t.status === filter);

  const stats = {
    total: mockTasks.length,
    inProgress: mockTasks.filter((t) =>
      ['assigned', 'in_progress', 'pending_review'].includes(t.status)
    ).length,
    overdue: 1, // Mock
    closedThisMonth: 5, // Mock
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Remediation Workflow</h1>
          <p className="text-muted-foreground">
            Track and manage security finding remediation tasks
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          <Plus className="h-4 w-4" />
          New Task
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total Tasks"
          value={stats.total}
          icon={ClipboardList}
          className="border-l-4 border-l-blue-500"
        />
        <StatCard
          title="In Progress"
          value={stats.inProgress}
          icon={Clock}
          className="border-l-4 border-l-indigo-500"
        />
        <StatCard
          title="Overdue"
          value={stats.overdue}
          icon={AlertTriangle}
          className="border-l-4 border-l-red-500"
        />
        <StatCard
          title="Closed This Month"
          value={stats.closedThisMonth}
          icon={CheckCircle}
          className="border-l-4 border-l-green-500"
        />
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-2">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Filter:</span>
        {(['all', 'in_progress', 'pending_review', 'assigned'] as const).map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={cn(
              'rounded-full px-3 py-1 text-xs font-medium transition-colors',
              filter === status
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            )}
          >
            {status === 'all' ? 'All' : statusLabels[status]}
          </button>
        ))}
      </div>

      {/* Task List */}
      <div className="rounded-lg border bg-card">
        <div className="divide-y">
          {filteredTasks.map((task) => (
            <div
              key={task.id}
              className="flex items-center gap-4 p-4 hover:bg-muted/50 cursor-pointer"
            >
              <div
                className={cn('w-1 h-12 rounded-full', {
                  'bg-red-500': task.priority === 'critical',
                  'bg-orange-500': task.priority === 'high',
                  'bg-yellow-500': task.priority === 'medium',
                  'bg-green-500': task.priority === 'low',
                })}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-foreground truncate">{task.title}</h3>
                  <span
                    className={cn(
                      'rounded-full px-2 py-0.5 text-xs font-medium',
                      statusColors[task.status]
                    )}
                  >
                    {statusLabels[task.status]}
                  </span>
                </div>
                <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                  {task.vendor && <span>{task.vendor}</span>}
                  {task.assignee && <span>Assigned: {task.assignee}</span>}
                  {task.dueDate && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      Due: {new Date(task.dueDate).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
              <span
                className={cn(
                  'rounded border px-2 py-0.5 text-xs font-medium capitalize',
                  priorityColors[task.priority]
                )}
              >
                {task.priority}
              </span>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
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

export default Remediation;
