import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Brain,
  Key,
  Zap,
  Database,
  AlertTriangle,
  Check,
  Loader2,
  Plus,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  Button,
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
import apiClient, { getApiErrorMessage } from '@/lib/api';

// Types
type AIStackType =
  | 'foundation_model'
  | 'genai_application'
  | 'inference_optimization'
  | 'fine_tuning_platform'
  | 'autonomous_agent'
  | 'horizontal_layer'
  | 'embedding_service'
  | 'mlops_platform'
  | 'not_ai_tool';

type AutonomyLevel = 'none' | 'low' | 'medium' | 'high' | 'critical';
type BlastRadius = 'minimal' | 'limited' | 'significant' | 'severe' | 'catastrophic';

interface AIClassification {
  id: string;
  vendor_id: string;
  stack_type: AIStackType;
  has_credential_access: boolean;
  has_autonomous_actions: boolean;
  has_data_training: boolean;
  has_external_integrations: boolean;
  has_code_execution: boolean;
  credential_types: string[] | null;
  action_types: string[] | null;
  requires_human_approval: boolean;
  trains_on_customer_data: boolean;
  data_sharing_third_parties: boolean;
  autonomy_level: AutonomyLevel;
  blast_radius: BlastRadius;
  ai_risk_score: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

interface StackTypeDefinition {
  id: string;
  name: string;
  description: string;
  examples: string[];
  typical_risks: string[];
  base_risk_score: number;
  typical_credential_access: boolean;
  typical_autonomous_actions: boolean;
}

// Stack type colors and display names
const stackTypeConfig: Record<AIStackType, { label: string; color: string; description: string }> = {
  foundation_model: {
    label: 'Foundation Model',
    color: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    description: 'Pure LLM provider (GPT, Claude, Gemini)',
  },
  genai_application: {
    label: 'GenAI Application',
    color: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    description: 'Application built on foundation models',
  },
  autonomous_agent: {
    label: 'Autonomous Agent',
    color: 'bg-red-500/20 text-red-400 border-red-500/30',
    description: 'AI agents that take autonomous actions',
  },
  fine_tuning_platform: {
    label: 'Fine-tuning Platform',
    color: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    description: 'Training/fine-tuning on your data',
  },
  inference_optimization: {
    label: 'Inference Optimization',
    color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    description: 'LLM inference and deployment tools',
  },
  horizontal_layer: {
    label: 'Horizontal Layer',
    color: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
    description: 'AI infrastructure and orchestration',
  },
  embedding_service: {
    label: 'Embedding Service',
    color: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
    description: 'Vector DB and embedding services',
  },
  mlops_platform: {
    label: 'MLOps Platform',
    color: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    description: 'ML operations and monitoring',
  },
  not_ai_tool: {
    label: 'Not an AI Tool',
    color: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    description: 'No AI capabilities',
  },
};

const autonomyColors: Record<AutonomyLevel, string> = {
  none: 'bg-gray-500/20 text-gray-400',
  low: 'bg-green-500/20 text-green-400',
  medium: 'bg-yellow-500/20 text-yellow-400',
  high: 'bg-orange-500/20 text-orange-400',
  critical: 'bg-red-500/20 text-red-400',
};

const blastRadiusColors: Record<BlastRadius, string> = {
  minimal: 'bg-green-500/20 text-green-400',
  limited: 'bg-blue-500/20 text-blue-400',
  significant: 'bg-yellow-500/20 text-yellow-400',
  severe: 'bg-orange-500/20 text-orange-400',
  catastrophic: 'bg-red-500/20 text-red-400',
};

interface AIClassificationPanelProps {
  vendorId: string;
  vendorName: string;
}

export function AIClassificationPanel({ vendorId, vendorName }: AIClassificationPanelProps) {
  const queryClient = useQueryClient();
  const [showClassifyModal, setShowClassifyModal] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [classifyError, setClassifyError] = useState<string | null>(null);

  // Form state for classification
  const [formData, setFormData] = useState({
    stack_type: 'not_ai_tool' as AIStackType,
    has_credential_access: false,
    has_autonomous_actions: false,
    has_data_training: false,
    has_external_integrations: false,
    has_code_execution: false,
    trains_on_customer_data: false,
    data_sharing_third_parties: false,
    requires_human_approval: true,
    autonomy_level: 'none' as AutonomyLevel,
    blast_radius: 'minimal' as BlastRadius,
    notes: '',
  });

  // Fetch existing classification
  const { data: classification, isLoading } = useQuery<AIClassification | null>({
    queryKey: ['ai-classification', vendorId],
    queryFn: async () => {
      try {
        const response = await apiClient.get(`/ai-classification/vendor/${vendorId}`);
        return response.data;
      } catch {
        return null;
      }
    },
  });

  // Fetch stack type definitions
  const { data: stackTypesResponse } = useQuery<{ stack_types: StackTypeDefinition[] }>({
    queryKey: ['stack-types'],
    queryFn: async () => {
      const response = await apiClient.get('/ai-classification/stack-types');
      return response.data;
    },
  });

  // Create classification mutation
  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const response = await apiClient.post('/ai-classification/', {
        vendor_id: vendorId,
        ...data,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-classification', vendorId] });
      setShowClassifyModal(false);
      setClassifyError(null);
    },
    onError: (error) => {
      setClassifyError(getApiErrorMessage(error));
    },
  });

  // Update classification mutation
  const updateMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      if (!classification) return;
      const response = await apiClient.put(`/ai-classification/${classification.id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-classification', vendorId] });
      setShowClassifyModal(false);
      setClassifyError(null);
    },
    onError: (error) => {
      setClassifyError(getApiErrorMessage(error));
    },
  });

  const handleOpenClassify = () => {
    if (classification) {
      // Pre-populate form with existing data
      setFormData({
        stack_type: classification.stack_type,
        has_credential_access: classification.has_credential_access,
        has_autonomous_actions: classification.has_autonomous_actions,
        has_data_training: classification.has_data_training,
        has_external_integrations: classification.has_external_integrations,
        has_code_execution: classification.has_code_execution,
        trains_on_customer_data: classification.trains_on_customer_data,
        data_sharing_third_parties: classification.data_sharing_third_parties,
        requires_human_approval: classification.requires_human_approval,
        autonomy_level: classification.autonomy_level,
        blast_radius: classification.blast_radius,
        notes: classification.notes || '',
      });
    }
    setClassifyError(null);
    setShowClassifyModal(true);
  };

  const handleSubmit = () => {
    if (classification) {
      updateMutation.mutate(formData);
    } else {
      createMutation.mutate(formData);
    }
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;
  const stackTypes = stackTypesResponse?.stack_types || [];

  // Get risk score color
  const getRiskScoreColor = (score: number) => {
    if (score >= 80) return 'text-red-400';
    if (score >= 60) return 'text-orange-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-green-400';
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-8 flex items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card className="glass-panel-liquid">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-obsidian-teal" />
              AI Tool Classification
            </div>
            {classification ? (
              <Button size="sm" variant="outline" onClick={handleOpenClassify}>
                Edit
              </Button>
            ) : (
              <Button size="sm" onClick={handleOpenClassify}>
                <Plus className="h-4 w-4 mr-1" />
                Classify
              </Button>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!classification ? (
            <div className="text-center py-6 text-muted-foreground">
              <Brain className="h-10 w-10 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Not yet classified as an AI tool</p>
              <p className="text-xs mt-1">Click "Classify" to add AI-specific risk factors</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Stack Type */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Stack Type</span>
                <Badge
                  variant="outline"
                  className={cn('font-medium', stackTypeConfig[classification.stack_type].color)}
                >
                  {stackTypeConfig[classification.stack_type].label}
                </Badge>
              </div>

              {/* AI Risk Score */}
              {classification.ai_risk_score !== null && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">AI Risk Score</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                      <motion.div
                        className={cn(
                          'h-full rounded-full',
                          classification.ai_risk_score >= 80
                            ? 'bg-red-500'
                            : classification.ai_risk_score >= 60
                              ? 'bg-orange-500'
                              : classification.ai_risk_score >= 40
                                ? 'bg-yellow-500'
                                : 'bg-green-500'
                        )}
                        initial={{ width: 0 }}
                        animate={{ width: `${classification.ai_risk_score}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                    <span className={cn('text-sm font-bold', getRiskScoreColor(classification.ai_risk_score))}>
                      {classification.ai_risk_score}/100
                    </span>
                  </div>
                </div>
              )}

              {/* Capability Flags */}
              <div className="grid grid-cols-2 gap-2">
                <CapabilityFlag
                  label="Credential Access"
                  value={classification.has_credential_access}
                  icon={Key}
                />
                <CapabilityFlag
                  label="Autonomous Actions"
                  value={classification.has_autonomous_actions}
                  icon={Zap}
                />
                <CapabilityFlag
                  label="Trains on Data"
                  value={classification.trains_on_customer_data}
                  icon={Database}
                />
                <CapabilityFlag
                  label="Code Execution"
                  value={classification.has_code_execution}
                  icon={AlertTriangle}
                />
              </div>

              {/* Expandable Details */}
              <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors w-full justify-center pt-2 border-t"
              >
                {expanded ? (
                  <>
                    <ChevronUp className="h-3 w-3" />
                    Show Less
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-3 w-3" />
                    Show More Details
                  </>
                )}
              </button>

              {expanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-3 pt-2"
                >
                  {/* Risk Levels */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs text-muted-foreground">Autonomy Level</label>
                      <Badge
                        variant="outline"
                        className={cn('mt-1 w-full justify-center', autonomyColors[classification.autonomy_level])}
                      >
                        {classification.autonomy_level.toUpperCase()}
                      </Badge>
                    </div>
                    <div>
                      <label className="text-xs text-muted-foreground">Blast Radius</label>
                      <Badge
                        variant="outline"
                        className={cn('mt-1 w-full justify-center', blastRadiusColors[classification.blast_radius])}
                      >
                        {classification.blast_radius.toUpperCase()}
                      </Badge>
                    </div>
                  </div>

                  {/* Additional Flags */}
                  <div className="text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Human Approval Required</span>
                      <span>{classification.requires_human_approval ? 'Yes' : 'No'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Shares Data with 3rd Parties</span>
                      <span>{classification.data_sharing_third_parties ? 'Yes' : 'No'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">External Integrations</span>
                      <span>{classification.has_external_integrations ? 'Yes' : 'No'}</span>
                    </div>
                  </div>

                  {/* Notes */}
                  {classification.notes && (
                    <div>
                      <label className="text-xs text-muted-foreground">Notes</label>
                      <p className="text-sm mt-1 p-2 bg-muted/50 rounded">{classification.notes}</p>
                    </div>
                  )}
                </motion.div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Classification Modal */}
      <Dialog open={showClassifyModal} onOpenChange={setShowClassifyModal}>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {classification ? 'Edit AI Classification' : 'Classify AI Tool'}
            </DialogTitle>
            <DialogDescription>
              Classify {vendorName} by AI stack type and risk factors
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Stack Type Selection */}
            <div>
              <Label>AI Stack Type</Label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {stackTypes.map((st) => (
                  <button
                    key={st.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, stack_type: st.id as AIStackType })}
                    className={cn(
                      'p-3 rounded-lg border text-left transition-all',
                      formData.stack_type === st.id
                        ? 'border-obsidian-teal bg-obsidian-teal/10'
                        : 'border-border hover:border-muted-foreground/30'
                    )}
                  >
                    <div className="font-medium text-sm">{st.name}</div>
                    <div className="text-xs text-muted-foreground mt-1">{st.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Capability Flags */}
            <div>
              <Label>Capability Flags</Label>
              <div className="grid grid-cols-2 gap-3 mt-2">
                <CheckboxField
                  label="Has Credential Access"
                  description="Can access user credentials or API keys"
                  checked={formData.has_credential_access}
                  onChange={(v) => setFormData({ ...formData, has_credential_access: v })}
                />
                <CheckboxField
                  label="Has Autonomous Actions"
                  description="Can take actions without human intervention"
                  checked={formData.has_autonomous_actions}
                  onChange={(v) => setFormData({ ...formData, has_autonomous_actions: v })}
                />
                <CheckboxField
                  label="Trains on Customer Data"
                  description="Uses your data for training or fine-tuning"
                  checked={formData.trains_on_customer_data}
                  onChange={(v) => setFormData({ ...formData, trains_on_customer_data: v })}
                />
                <CheckboxField
                  label="Has Code Execution"
                  description="Can execute code on your systems"
                  checked={formData.has_code_execution}
                  onChange={(v) => setFormData({ ...formData, has_code_execution: v })}
                />
                <CheckboxField
                  label="External Integrations"
                  description="Connects to external services"
                  checked={formData.has_external_integrations}
                  onChange={(v) => setFormData({ ...formData, has_external_integrations: v })}
                />
                <CheckboxField
                  label="Shares with Third Parties"
                  description="Shares data with other vendors"
                  checked={formData.data_sharing_third_parties}
                  onChange={(v) => setFormData({ ...formData, data_sharing_third_parties: v })}
                />
              </div>
            </div>

            {/* Risk Levels */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Autonomy Level</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-2"
                  value={formData.autonomy_level}
                  onChange={(e) => setFormData({ ...formData, autonomy_level: e.target.value as AutonomyLevel })}
                >
                  <option value="none">None</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div>
                <Label>Blast Radius</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-2"
                  value={formData.blast_radius}
                  onChange={(e) => setFormData({ ...formData, blast_radius: e.target.value as BlastRadius })}
                >
                  <option value="minimal">Minimal</option>
                  <option value="limited">Limited</option>
                  <option value="significant">Significant</option>
                  <option value="severe">Severe</option>
                  <option value="catastrophic">Catastrophic</option>
                </select>
              </div>
            </div>

            {/* Human Approval */}
            <CheckboxField
              label="Requires Human Approval"
              description="Actions require human approval before execution"
              checked={formData.requires_human_approval}
              onChange={(v) => setFormData({ ...formData, requires_human_approval: v })}
            />

            {/* Notes */}
            <div>
              <Label>Notes</Label>
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-2"
                placeholder="Additional notes about this AI tool classification..."
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              />
            </div>

            {classifyError && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {classifyError}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowClassifyModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {classification ? 'Save Changes' : 'Create Classification'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

// Helper component for capability flags
function CapabilityFlag({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: boolean;
  icon: React.ElementType;
}) {
  return (
    <div
      className={cn(
        'flex items-center gap-2 p-2 rounded-lg text-xs',
        value ? 'bg-red-500/10 text-red-400' : 'bg-muted/50 text-muted-foreground'
      )}
    >
      <Icon className="h-3 w-3" />
      <span>{label}</span>
      {value && <Check className="h-3 w-3 ml-auto" />}
    </div>
  );
}

// Helper component for checkbox fields
function CheckboxField({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="flex items-start gap-3 p-3 rounded-lg border cursor-pointer hover:bg-muted/30 transition-colors">
      <input
        type="checkbox"
        className="mt-1"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <div>
        <div className="text-sm font-medium">{label}</div>
        <div className="text-xs text-muted-foreground">{description}</div>
      </div>
    </label>
  );
}

export default AIClassificationPanel;
