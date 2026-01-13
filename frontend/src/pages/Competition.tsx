import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { TrendingUp, Target, Users, Layers, ExternalLink, Shield, ArrowLeft } from 'lucide-react';
import { CyberCard } from '@/components/ui/CyberCard';
import { AnimatedCounter, AnimatedPercentage } from '@/components/ui/AnimatedCounter';
import {
  CompetitorBubbleChart,
  ThreatTierCards,
  FeatureComparisonTable,
  SpeedComparisonChart,
  WhyWeWinCards,
  StrategicRoadmap,
} from '@/components/competition';
import { marketData } from '@/data/competitors';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
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

export function Competition() {
  return (
    <div className="min-h-screen bg-background">
      {/* Public Navigation Header */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="sticky top-0 z-50 backdrop-blur-xl bg-background/80 border-b border-white/10"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/30 flex items-center justify-center group-hover:scale-105 transition-transform">
                <Shield className="h-5 w-5 text-primary" />
              </div>
              <span className="text-lg font-bold text-white">
                VendorAudit<span className="text-primary">AI</span>
              </span>
            </Link>

            {/* Navigation */}
            <div className="flex items-center gap-4">
              <Link
                to="/"
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-white transition-colors"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Home
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 rounded-lg bg-primary text-black font-medium text-sm hover:bg-primary/90 transition-colors"
              >
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8"
      >
      {/* Hero Section - Market Overview */}
      <motion.div variants={itemVariants} className="relative overflow-hidden">
        <CyberCard className="p-8 relative">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-blue-500/5 pointer-events-none" />

          <div className="relative z-10">
            <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6 mb-8">
              <div>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/30 mb-4"
                >
                  <Target className="h-4 w-4 text-primary" />
                  <span className="text-sm text-primary font-medium">Market Intelligence</span>
                </motion.div>

                <h1 className="text-5xl font-bold tracking-tighter text-white mb-2">
                  COMPETITIVE<span className="text-primary">ANALYSIS</span>
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl">
                  Comprehensive analysis of the $8.6B Third-Party Risk Management market.
                  24 competitors analyzed across 5 threat tiers.
                </p>
              </div>

              <motion.div
                whileHover={{ scale: 1.02 }}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10"
              >
                <span className="text-xs text-muted-foreground uppercase">Research Date</span>
                <span className="font-mono text-white">Jan 2026</span>
              </motion.div>
            </div>

            {/* Market Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <motion.div
                variants={itemVariants}
                whileHover={{ scale: 1.03, y: -2 }}
                className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-primary/30 transition-all"
              >
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  <span className="text-xs text-muted-foreground uppercase">Market Size</span>
                </div>
                <p className="text-3xl font-bold text-white font-mono">
                  $<AnimatedCounter value={marketData.totalSize} duration={2} formatValue={(v) => v.toFixed(1)} />B
                </p>
                <p className="text-xs text-muted-foreground mt-1">2025 Valuation</p>
              </motion.div>

              <motion.div
                variants={itemVariants}
                whileHover={{ scale: 1.03, y: -2 }}
                className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-primary/30 transition-all"
              >
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-green-400" />
                  <span className="text-xs text-muted-foreground uppercase">CAGR Growth</span>
                </div>
                <p className="text-3xl font-bold text-green-400 font-mono">
                  <AnimatedPercentage value={marketData.cagr} duration={2} decimals={0} />
                </p>
                <p className="text-xs text-muted-foreground mt-1">Annual Growth Rate</p>
              </motion.div>

              <motion.div
                variants={itemVariants}
                whileHover={{ scale: 1.03, y: -2 }}
                className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-primary/30 transition-all"
              >
                <div className="flex items-center gap-2 mb-2">
                  <Users className="h-4 w-4 text-yellow-400" />
                  <span className="text-xs text-muted-foreground uppercase">Competitors</span>
                </div>
                <p className="text-3xl font-bold text-white font-mono">
                  <AnimatedCounter value={marketData.competitorsAnalyzed} duration={1.5} />
                </p>
                <p className="text-xs text-muted-foreground mt-1">Analyzed in Detail</p>
              </motion.div>

              <motion.div
                variants={itemVariants}
                whileHover={{ scale: 1.03, y: -2 }}
                className="p-4 rounded-xl bg-primary/5 border border-primary/30 hover:border-primary/50 transition-all"
              >
                <div className="flex items-center gap-2 mb-2">
                  <Layers className="h-4 w-4 text-primary" />
                  <span className="text-xs text-muted-foreground uppercase">Opportunity</span>
                </div>
                <p className="text-3xl font-bold text-primary font-mono">
                  <AnimatedPercentage value={marketData.marketOpportunity} duration={2} decimals={0} />
                </p>
                <p className="text-xs text-muted-foreground mt-1">Without Advanced TPRM</p>
              </motion.div>
            </div>
          </div>
        </CyberCard>
      </motion.div>

      {/* Competitor Bubble Chart */}
      <motion.div variants={itemVariants}>
        <CompetitorBubbleChart />
      </motion.div>

      {/* Threat Tier Cards */}
      <motion.div variants={itemVariants}>
        <ThreatTierCards />
      </motion.div>

      {/* Feature Comparison Table */}
      <motion.div variants={itemVariants}>
        <FeatureComparisonTable />
      </motion.div>

      {/* Speed Comparison Chart */}
      <motion.div variants={itemVariants}>
        <SpeedComparisonChart />
      </motion.div>

      {/* Why We Win Cards */}
      <motion.div variants={itemVariants}>
        <WhyWeWinCards />
      </motion.div>

      {/* Strategic Roadmap */}
      <motion.div variants={itemVariants}>
        <StrategicRoadmap />
      </motion.div>

      {/* Market Forces Section */}
      <motion.div variants={itemVariants}>
        <CyberCard className="p-6">
          <h3 className="text-xl font-bold text-white mb-4">Market Forces Reshaping Competition</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-4 rounded-lg bg-red-500/5 border border-red-500/20"
            >
              <p className="text-sm font-bold text-red-400 mb-1">DORA Mandatory</p>
              <p className="text-2xl font-mono text-white">Jan 17, 2025</p>
              <p className="text-xs text-muted-foreground mt-2">
                2% global revenue penalties for non-compliance
              </p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-4 rounded-lg bg-yellow-500/5 border border-yellow-500/20"
            >
              <p className="text-sm font-bold text-yellow-400 mb-1">NIS2 Supply Chain</p>
              <p className="text-2xl font-mono text-white">62%</p>
              <p className="text-xs text-muted-foreground mt-2">
                Of breaches originate from third parties
              </p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/20"
            >
              <p className="text-sm font-bold text-blue-400 mb-1">SEC Disclosure Rules</p>
              <p className="text-2xl font-mono text-white">4 Days</p>
              <p className="text-xs text-muted-foreground mt-2">
                To report material cyber incidents
              </p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="p-4 rounded-lg bg-primary/5 border border-primary/20"
            >
              <p className="text-sm font-bold text-primary mb-1">Market Opportunity</p>
              <p className="text-2xl font-mono text-white">$20-28B</p>
              <p className="text-xs text-muted-foreground mt-2">
                Projected market size by 2030
              </p>
            </motion.div>
          </div>
        </CyberCard>
      </motion.div>

      {/* Footer CTA */}
      <motion.div variants={itemVariants}>
        <CyberCard className="p-8 text-center bg-gradient-to-br from-primary/5 to-blue-500/5">
          <h3 className="text-2xl font-bold text-white mb-2">
            Ready to Lead the Market?
          </h3>
          <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
            VendorAuditAI combines Claude Opus 4.5 reasoning with autonomous AI agents
            to deliver 15-minute vendor assessments.
          </p>
          <div className="flex items-center justify-center gap-4">
            <a
              href="https://github.com/MikeDominic92/VendorAuditAI"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-white/10 border border-white/20 text-white hover:bg-white/20 transition-colors"
            >
              View on GitHub
              <ExternalLink className="h-4 w-4" />
            </a>
            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-primary text-black font-medium hover:bg-primary/90 transition-colors"
            >
              Try VendorAuditAI Free
            </Link>
          </div>
        </CyberCard>
      </motion.div>
      </motion.div>
    </div>
  );
}
