import { motion } from 'framer-motion';
import { AlertTriangle, AlertCircle, Activity, Clock, Archive } from 'lucide-react';
import { CyberCard } from '@/components/ui/CyberCard';
import { cn } from '@/lib/utils';
import {
  competitors,
  tierColors,
  tierLabels,
  getCompetitorsByTier,
  formatValuation,
  type Competitor,
} from '@/data/competitors';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: 'spring' as const,
      stiffness: 100,
      damping: 15,
    },
  },
};

const tierIcons: Record<number, React.ElementType> = {
  1: AlertTriangle,
  2: AlertCircle,
  3: Activity,
  4: Clock,
  5: Archive,
};

const tierDescriptions: Record<number, string> = {
  1: 'Require direct differentiation strategy',
  2: 'Significant market presence, watch closely',
  3: 'Fast-growing, potential future threats',
  4: 'Established but slow to innovate',
  5: 'Niche focus, limited direct competition',
};

interface TierCardProps {
  tier: number;
  competitors: Competitor[];
}

function TierCard({ tier, competitors }: TierCardProps) {
  const Icon = tierIcons[tier];
  const colors = tierColors[tier];
  const totalFunding = competitors.reduce((sum, c) => sum + c.funding, 0);
  const totalCustomers = competitors.reduce((sum, c) => sum + c.customers, 0);

  return (
    <motion.div variants={itemVariants}>
      <CyberCard className="p-5 h-full">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <motion.div
              whileHover={{ scale: 1.1, rotate: 5 }}
              className={cn(
                'h-10 w-10 rounded-lg flex items-center justify-center',
                colors.bg,
                colors.border,
                'border'
              )}
            >
              <Icon className={cn('h-5 w-5', colors.text)} />
            </motion.div>
            <div>
              <h4 className={cn('font-bold text-lg', colors.text)}>
                Tier {tier} - {tierLabels[tier]}
              </h4>
              <p className="text-xs text-muted-foreground">{tierDescriptions[tier]}</p>
            </div>
          </div>
          <span
            className={cn(
              'text-2xl font-bold font-mono',
              colors.text
            )}
          >
            {competitors.length}
          </span>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3 mb-4 p-3 rounded-lg bg-white/5">
          <div>
            <p className="text-xs text-muted-foreground uppercase">Total Funding</p>
            <p className="text-white font-mono font-bold">
              ${(totalFunding / 1000).toFixed(1)}B
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground uppercase">Total Customers</p>
            <p className="text-white font-mono font-bold">
              {totalCustomers.toLocaleString()}
            </p>
          </div>
        </div>

        {/* Competitor List */}
        <div className="space-y-2">
          {competitors.map((competitor, index) => (
            <motion.div
              key={competitor.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center justify-between p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors group"
            >
              <div className="flex items-center gap-2 min-w-0">
                <span className="text-sm font-medium text-white truncate group-hover:text-primary transition-colors">
                  {competitor.name}
                </span>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                <span className="text-xs text-muted-foreground font-mono">
                  {formatValuation(competitor.valuation)}
                </span>
                <span className="text-xs text-primary/80 font-mono">
                  {competitor.aiCapabilityScore}/100
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </CyberCard>
    </motion.div>
  );
}

export function ThreatTierCards() {
  const tiers = [1, 2, 3, 4, 5];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-white mb-1">Threat Assessment by Tier</h3>
          <p className="text-sm text-muted-foreground">
            {competitors.length} competitors analyzed across 5 threat levels
          </p>
        </div>

        {/* Summary Stats */}
        <div className="flex gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-red-400 font-mono">
              {getCompetitorsByTier(1).length}
            </p>
            <p className="text-xs text-muted-foreground">Critical</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-yellow-400 font-mono">
              {getCompetitorsByTier(2).length}
            </p>
            <p className="text-xs text-muted-foreground">High</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-400 font-mono">
              {getCompetitorsByTier(3).length}
            </p>
            <p className="text-xs text-muted-foreground">Medium</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-teal-400 font-mono">
              {getCompetitorsByTier(4).length + getCompetitorsByTier(5).length}
            </p>
            <p className="text-xs text-muted-foreground">Low</p>
          </div>
        </div>
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4"
      >
        {tiers.map((tier) => (
          <TierCard
            key={tier}
            tier={tier}
            competitors={getCompetitorsByTier(tier)}
          />
        ))}
      </motion.div>
    </div>
  );
}
