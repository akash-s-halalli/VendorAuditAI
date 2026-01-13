// ============================================================================
// VendorAuditAI Competitive Analysis Data
// Research Date: January 2026
// Market Size: $8.6B TPRM Market
// ============================================================================

export interface Competitor {
  id: string;
  name: string;
  tier: 1 | 2 | 3 | 4 | 5;
  threatLevel: 'critical' | 'high' | 'medium' | 'low';
  valuation: number; // millions USD
  funding: number; // millions USD
  customers: number;
  founded: number;
  annualCost: { min: number; max: number }; // thousands USD
  docAnalysisTime: string;
  aiModel: string;
  nlQueryCitations: boolean;
  autonomousAgents: number;
  frameworksSupported: number;
  keyStrength: string;
  keyWeakness: string;
  aiCapabilityScore: number; // 0-100 for chart
}

// VendorAuditAI Entry (for comparison)
export const vendorAuditAI: Competitor = {
  id: 'vendorauditai',
  name: 'VendorAuditAI',
  tier: 1,
  threatLevel: 'critical',
  valuation: 10, // Pre-seed
  funding: 0,
  customers: 50, // Demo users
  founded: 2024,
  annualCost: { min: 5, max: 15 },
  docAnalysisTime: '15 min',
  aiModel: 'Claude Opus 4.5',
  nlQueryCitations: true,
  autonomousAgents: 4,
  frameworksSupported: 12,
  keyStrength: 'Claude Opus 4.5 reasoning, 4 autonomous agents, 15-min analysis',
  keyWeakness: 'Early stage, building market presence',
  aiCapabilityScore: 92,
};

// 24 Competitors across 5 Threat Tiers
export const competitors: Competitor[] = [
  // ============================================================================
  // TIER 1 - CRITICAL THREATS (Require Direct Differentiation)
  // ============================================================================
  {
    id: 'drata',
    name: 'Drata',
    tier: 1,
    threatLevel: 'critical',
    valuation: 2000,
    funding: 328,
    customers: 8000,
    founded: 2020,
    annualCost: { min: 7.5, max: 25 },
    docAnalysisTime: 'Minutes',
    aiModel: 'Proprietary + SafeBase',
    nlQueryCitations: false,
    autonomousAgents: 1,
    frameworksSupported: 23,
    keyStrength: '$250M SafeBase acquisition, VRM AI Agent',
    keyWeakness: 'Compliance-first, retrofitted TPRM',
    aiCapabilityScore: 85,
  },
  {
    id: 'vanta',
    name: 'Vanta',
    tier: 1,
    threatLevel: 'critical',
    valuation: 4150,
    funding: 504,
    customers: 12000,
    founded: 2018,
    annualCost: { min: 10, max: 50 },
    docAnalysisTime: 'Hours',
    aiModel: 'Proprietary + MCP',
    nlQueryCitations: false,
    autonomousAgents: 1,
    frameworksSupported: 30,
    keyStrength: 'MCP Server integration, 12K customers, market leader',
    keyWeakness: 'Enterprise-heavy, slower AI adoption',
    aiCapabilityScore: 78,
  },
  {
    id: 'securityscorecard',
    name: 'SecurityScorecard',
    tier: 1,
    threatLevel: 'critical',
    valuation: 2500,
    funding: 540,
    customers: 50000,
    founded: 2013,
    annualCost: { min: 20, max: 100 },
    docAnalysisTime: 'Seconds',
    aiModel: 'HyperComply AI',
    nlQueryCitations: false,
    autonomousAgents: 1,
    frameworksSupported: 15,
    keyStrength: 'HyperComply acquisition, 92% workload reduction',
    keyWeakness: 'Ratings-focused, limited document analysis',
    aiCapabilityScore: 82,
  },
  {
    id: 'processunity',
    name: 'ProcessUnity',
    tier: 1,
    threatLevel: 'critical',
    valuation: 500,
    funding: 150,
    customers: 1200,
    founded: 2008,
    annualCost: { min: 50, max: 200 },
    docAnalysisTime: 'Seconds',
    aiModel: 'Evidence Evaluator AI',
    nlQueryCitations: false,
    autonomousAgents: 1,
    frameworksSupported: 20,
    keyStrength: '370K vendor profiles, Evidence Evaluator',
    keyWeakness: 'Legacy architecture, enterprise pricing',
    aiCapabilityScore: 75,
  },

  // ============================================================================
  // TIER 2 - SIGNIFICANT COMPETITORS
  // ============================================================================
  {
    id: 'onetrust',
    name: 'OneTrust',
    tier: 2,
    threatLevel: 'high',
    valuation: 4500,
    funding: 920,
    customers: 14000,
    founded: 2016,
    annualCost: { min: 100, max: 500 },
    docAnalysisTime: 'Hours',
    aiModel: 'Third-Party Risk Agent',
    nlQueryCitations: false,
    autonomousAgents: 1,
    frameworksSupported: 50,
    keyStrength: '14K customers, comprehensive privacy platform',
    keyWeakness: 'Privacy-first, TPRM secondary focus',
    aiCapabilityScore: 70,
  },
  {
    id: 'bitsight',
    name: 'BitSight',
    tier: 2,
    threatLevel: 'high',
    valuation: 2400,
    funding: 350,
    customers: 3500,
    founded: 2011,
    annualCost: { min: 30, max: 150 },
    docAnalysisTime: 'Minutes',
    aiModel: 'Instant Insights AI',
    nlQueryCitations: false,
    autonomousAgents: 1,
    frameworksSupported: 12,
    keyStrength: 'Cybersixgill acquisition, threat intelligence',
    keyWeakness: 'Ratings-focused, limited questionnaire automation',
    aiCapabilityScore: 72,
  },
  {
    id: 'whistic',
    name: 'Whistic',
    tier: 2,
    threatLevel: 'high',
    valuation: 150,
    funding: 51,
    customers: 2000,
    founded: 2015,
    annualCost: { min: 15, max: 60 },
    docAnalysisTime: 'Minutes',
    aiModel: 'Smart AI (91% accuracy)',
    nlQueryCitations: false,
    autonomousAgents: 1,
    frameworksSupported: 10,
    keyStrength: '91% AI accuracy, 50K vendor profiles',
    keyWeakness: 'Smaller scale, limited enterprise features',
    aiCapabilityScore: 74,
  },
  {
    id: 'panorays',
    name: 'Panorays',
    tier: 2,
    threatLevel: 'high',
    valuation: 200,
    funding: 62,
    customers: 800,
    founded: 2016,
    annualCost: { min: 25, max: 100 },
    docAnalysisTime: 'Minutes',
    aiModel: 'Smart Match AI',
    nlQueryCitations: false,
    autonomousAgents: 1,
    frameworksSupported: 15,
    keyStrength: 'Forrester Wave Leader, Smart Match AI',
    keyWeakness: 'Mid-market focus, smaller customer base',
    aiCapabilityScore: 76,
  },
  {
    id: 'prevalent',
    name: 'Prevalent',
    tier: 2,
    threatLevel: 'high',
    valuation: 300,
    funding: 92,
    customers: 1500,
    founded: 2013,
    annualCost: { min: 40, max: 150 },
    docAnalysisTime: 'Hours',
    aiModel: 'Alfred AI',
    nlQueryCitations: false,
    autonomousAgents: 1,
    frameworksSupported: 25,
    keyStrength: '800+ assessment templates, Alfred AI',
    keyWeakness: 'Traditional approach, slower innovation',
    aiCapabilityScore: 68,
  },

  // ============================================================================
  // TIER 3 - EMERGING COMPETITORS
  // ============================================================================
  {
    id: 'hyperproof',
    name: 'Hyperproof',
    tier: 3,
    threatLevel: 'medium',
    valuation: 200,
    funding: 67,
    customers: 1200,
    founded: 2018,
    annualCost: { min: 20, max: 80 },
    docAnalysisTime: 'Hours',
    aiModel: 'Hypersync AI',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 25,
    keyStrength: 'Risk management integration, compliance automation',
    keyWeakness: 'Compliance-focused, limited TPRM depth',
    aiCapabilityScore: 62,
  },
  {
    id: 'sprinto',
    name: 'Sprinto',
    tier: 3,
    threatLevel: 'medium',
    valuation: 200,
    funding: 32,
    customers: 2000,
    founded: 2020,
    annualCost: { min: 10, max: 40 },
    docAnalysisTime: 'Hours',
    aiModel: 'Basic AI',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 15,
    keyStrength: 'Fast growing SMB focus, affordable pricing',
    keyWeakness: 'SMB-only, limited enterprise capabilities',
    aiCapabilityScore: 55,
  },
  {
    id: 'anecdotes',
    name: 'Anecdotes',
    tier: 3,
    threatLevel: 'medium',
    valuation: 100,
    funding: 55,
    customers: 500,
    founded: 2020,
    annualCost: { min: 30, max: 100 },
    docAnalysisTime: 'Hours',
    aiModel: 'GRC AI',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 20,
    keyStrength: 'GRC automation, compliance workflows',
    keyWeakness: 'Newer player, building market presence',
    aiCapabilityScore: 58,
  },
  {
    id: 'blackkite',
    name: 'Black Kite',
    tier: 3,
    threatLevel: 'medium',
    valuation: 150,
    funding: 56,
    customers: 1000,
    founded: 2018,
    annualCost: { min: 25, max: 80 },
    docAnalysisTime: 'Minutes',
    aiModel: 'Cyber Risk AI',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 10,
    keyStrength: 'Standards-based risk quantification',
    keyWeakness: 'Ratings-focused, limited document analysis',
    aiCapabilityScore: 60,
  },
  {
    id: 'upguard',
    name: 'UpGuard',
    tier: 3,
    threatLevel: 'medium',
    valuation: 230,
    funding: 69,
    customers: 900,
    founded: 2012,
    annualCost: { min: 15, max: 50 },
    docAnalysisTime: 'Hours',
    aiModel: 'Basic ML',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 8,
    keyStrength: 'Data leak detection, breach monitoring',
    keyWeakness: 'Monitoring-focused, limited assessment automation',
    aiCapabilityScore: 52,
  },
  {
    id: 'secureframe',
    name: 'Secureframe',
    tier: 3,
    threatLevel: 'medium',
    valuation: 450,
    funding: 79,
    customers: 3000,
    founded: 2019,
    annualCost: { min: 15, max: 60 },
    docAnalysisTime: 'Hours',
    aiModel: 'Comply AI',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 20,
    keyStrength: 'Fast compliance automation, SMB friendly',
    keyWeakness: 'Compliance-first, TPRM as add-on',
    aiCapabilityScore: 64,
  },

  // ============================================================================
  // TIER 4 - LEGACY ENTERPRISE
  // ============================================================================
  {
    id: 'servicenow',
    name: 'ServiceNow GRC',
    tier: 4,
    threatLevel: 'low',
    valuation: 180000, // Public company market cap
    funding: 0,
    customers: 8000,
    founded: 2004,
    annualCost: { min: 100, max: 500 },
    docAnalysisTime: 'Days',
    aiModel: 'Now AI (Limited)',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 40,
    keyStrength: 'Enterprise platform, IT integration',
    keyWeakness: 'Slow AI adoption, complex implementation',
    aiCapabilityScore: 45,
  },
  {
    id: 'metricstream',
    name: 'MetricStream',
    tier: 4,
    threatLevel: 'low',
    valuation: 500,
    funding: 250,
    customers: 800,
    founded: 1999,
    annualCost: { min: 150, max: 600 },
    docAnalysisTime: 'Days',
    aiModel: 'Legacy + Basic ML',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 35,
    keyStrength: 'Enterprise GRC experience, large deployments',
    keyWeakness: 'Legacy architecture, slow innovation',
    aiCapabilityScore: 38,
  },
  {
    id: 'archer',
    name: 'Archer',
    tier: 4,
    threatLevel: 'low',
    valuation: 400,
    funding: 0,
    customers: 1000,
    founded: 2001,
    annualCost: { min: 100, max: 400 },
    docAnalysisTime: 'Days',
    aiModel: 'Limited AI',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 30,
    keyStrength: 'Deep GRC experience, configurable platform',
    keyWeakness: 'Complex implementation, aging technology',
    aiCapabilityScore: 35,
  },
  {
    id: 'sapgrc',
    name: 'SAP GRC',
    tier: 4,
    threatLevel: 'low',
    valuation: 250000, // SAP market cap
    funding: 0,
    customers: 5000,
    founded: 1972,
    annualCost: { min: 200, max: 800 },
    docAnalysisTime: 'Days',
    aiModel: 'SAP AI (Limited TPRM)',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 25,
    keyStrength: 'SAP ecosystem integration',
    keyWeakness: 'ERP-focused, TPRM as afterthought',
    aiCapabilityScore: 32,
  },

  // ============================================================================
  // TIER 5 - SPECIALIZED/NICHE
  // ============================================================================
  {
    id: 'riskrecon',
    name: 'RiskRecon',
    tier: 5,
    threatLevel: 'low',
    valuation: 200,
    funding: 40,
    customers: 500,
    founded: 2015,
    annualCost: { min: 20, max: 80 },
    docAnalysisTime: 'Minutes',
    aiModel: 'Security Ratings AI',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 5,
    keyStrength: 'Mastercard backing, security ratings focus',
    keyWeakness: 'Ratings-only, no document analysis',
    aiCapabilityScore: 48,
  },
  {
    id: 'venminder',
    name: 'Venminder',
    tier: 5,
    threatLevel: 'low',
    valuation: 100,
    funding: 30,
    customers: 800,
    founded: 2013,
    annualCost: { min: 30, max: 100 },
    docAnalysisTime: 'Hours',
    aiModel: 'Basic AI',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 8,
    keyStrength: 'Financial services focus, managed services',
    keyWeakness: 'Niche market, limited AI capabilities',
    aiCapabilityScore: 42,
  },
  {
    id: 'scrut',
    name: 'Scrut',
    tier: 5,
    threatLevel: 'low',
    valuation: 80,
    funding: 16,
    customers: 300,
    founded: 2021,
    annualCost: { min: 8, max: 30 },
    docAnalysisTime: 'Hours',
    aiModel: 'Basic AI',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 10,
    keyStrength: 'Affordable pricing, SMB focus',
    keyWeakness: 'Early stage, limited features',
    aiCapabilityScore: 40,
  },
  {
    id: 'ketch',
    name: 'Ketch',
    tier: 5,
    threatLevel: 'low',
    valuation: 150,
    funding: 53,
    customers: 400,
    founded: 2020,
    annualCost: { min: 20, max: 80 },
    docAnalysisTime: 'Hours',
    aiModel: 'Privacy AI',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 5,
    keyStrength: 'Data privacy automation',
    keyWeakness: 'Privacy-only, not a TPRM platform',
    aiCapabilityScore: 38,
  },
  {
    id: 'safesecurity',
    name: 'SAFE Security',
    tier: 5,
    threatLevel: 'low',
    valuation: 120,
    funding: 45,
    customers: 200,
    founded: 2012,
    annualCost: { min: 40, max: 120 },
    docAnalysisTime: 'Hours',
    aiModel: 'FAIR Quantification AI',
    nlQueryCitations: false,
    autonomousAgents: 0,
    frameworksSupported: 3,
    keyStrength: 'FAIR risk quantification',
    keyWeakness: 'Quantification-only, limited TPRM features',
    aiCapabilityScore: 44,
  },
];

// ============================================================================
// Market Data
// ============================================================================

export const marketData = {
  totalSize: 8.6, // billions USD
  projectedSize2030: 24, // billions USD (midpoint of $20-28B)
  cagr: 16, // percent (midpoint of 15-17%)
  competitorsAnalyzed: 24,
  threatTiers: 5,
  advancedTPRMAdoption: 9, // percent with advanced capabilities
  marketOpportunity: 91, // percent without advanced TPRM
};

// ============================================================================
// Speed Comparison Data (for horizontal bar chart)
// ============================================================================

export const speedComparisonData = [
  { name: 'Industry Standard', time: 480, display: '8 hours', color: '#6B7280' },
  { name: 'Legacy Enterprise', time: 240, display: '4 hours', color: '#EF4444' },
  { name: 'Drata/Vanta', time: 60, display: '1 hour', color: '#F59E0B' },
  { name: 'BitSight/Whistic', time: 30, display: '30 min', color: '#3B82F6' },
  { name: 'VendorAuditAI', time: 15, display: '15 min', color: '#00D4AA' },
  { name: 'ProcessUnity', time: 1, display: 'Seconds', color: '#10B981' },
];

// ============================================================================
// Feature Comparison Data
// ============================================================================

export const featureComparisonHeaders = [
  'Company',
  'Doc Analysis',
  'AI Model',
  'NL Query',
  'AI Agents',
  'Frameworks',
  'Cost Tier',
];

export const costTiers = {
  '$': '< $15K/year',
  '$$': '$15-50K/year',
  '$$$': '$50-150K/year',
  '$$$$': '$150K+/year',
};

// ============================================================================
// Why We Win Data
// ============================================================================

export const whyWeWinData = [
  {
    title: 'Claude Opus 4.5',
    description: 'Superior reasoning vs proprietary models used by competitors',
    icon: 'brain',
    stat: '92/100',
    statLabel: 'AI Score',
  },
  {
    title: '4 Autonomous Agents',
    description: 'Multi-agent system vs single-purpose AI in competitor products',
    icon: 'cpu',
    stat: '4x',
    statLabel: 'More Agents',
  },
  {
    title: '15-Minute Analysis',
    description: '97% faster than industry benchmark of 2-4 hours',
    icon: 'zap',
    stat: '97%',
    statLabel: 'Time Saved',
  },
  {
    title: 'HECVAT + SIG 2026',
    description: 'Support for underserved higher education and healthcare verticals',
    icon: 'target',
    stat: '12',
    statLabel: 'Frameworks',
  },
  {
    title: 'Modern Architecture',
    description: 'React 18 + FastAPI vs legacy monolithic competitor systems',
    icon: 'layers',
    stat: '2024',
    statLabel: 'Tech Stack',
  },
];

// ============================================================================
// Strategic Roadmap Data
// ============================================================================

export const roadmapData = [
  {
    quarter: 'Q1 2026',
    title: 'Vendor Exchange Network',
    description: 'Compete with ProcessUnity 370K vendor profiles',
    status: 'in-progress',
  },
  {
    quarter: 'Q2 2026',
    title: 'Trust Center',
    description: 'Compete with Drata/SafeBase trust portals',
    status: 'planned',
  },
  {
    quarter: 'Q3 2026',
    title: 'Financial Risk Quantification',
    description: 'FAIR methodology integration',
    status: 'planned',
  },
  {
    quarter: 'Q4 2026',
    title: '200+ Integrations',
    description: 'ServiceNow, Jira, Slack, and more',
    status: 'planned',
  },
];

// ============================================================================
// Tier Colors (Digital Obsidian Theme)
// ============================================================================

export const tierColors: Record<number, { primary: string; bg: string; border: string; text: string }> = {
  1: { primary: '#E63946', bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400' },
  2: { primary: '#FFB800', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400' },
  3: { primary: '#0066FF', bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400' },
  4: { primary: '#00D4AA', bg: 'bg-teal-500/10', border: 'border-teal-500/30', text: 'text-teal-400' },
  5: { primary: '#6B7280', bg: 'bg-gray-500/10', border: 'border-gray-500/30', text: 'text-gray-400' },
};

export const tierLabels: Record<number, string> = {
  1: 'Critical',
  2: 'Significant',
  3: 'Emerging',
  4: 'Legacy',
  5: 'Specialized',
};

// ============================================================================
// Helper Functions
// ============================================================================

export function getCompetitorsByTier(tier: number): Competitor[] {
  return competitors.filter((c) => c.tier === tier);
}

export function getTierCount(): Record<number, number> {
  return competitors.reduce(
    (acc, c) => {
      acc[c.tier] = (acc[c.tier] || 0) + 1;
      return acc;
    },
    {} as Record<number, number>
  );
}

export function formatCost(competitor: Competitor): string {
  const { max } = competitor.annualCost;
  if (max <= 15) return '$';
  if (max <= 50) return '$$';
  if (max <= 150) return '$$$';
  return '$$$$';
}

export function formatValuation(valuation: number): string {
  if (valuation >= 1000) {
    return `$${(valuation / 1000).toFixed(1)}B`;
  }
  return `$${valuation}M`;
}
