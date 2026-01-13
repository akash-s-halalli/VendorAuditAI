import { motion } from 'framer-motion';
import { Target, CheckCircle, Clock, ArrowRight } from 'lucide-react';
import { CyberCard } from '@/components/ui/CyberCard';
import { cn } from '@/lib/utils';
import { roadmapData } from '@/data/competitors';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.3,
    },
  },
};

const itemVariants = {
  hidden: { x: -30, opacity: 0 },
  visible: {
    x: 0,
    opacity: 1,
    transition: {
      type: 'spring' as const,
      stiffness: 100,
      damping: 15,
    },
  },
};

export function StrategicRoadmap() {
  return (
    <CyberCard className="p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h3 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            Strategic Roadmap 2026
          </h3>
          <p className="text-sm text-muted-foreground">
            Closing competitive gaps and building market leadership
          </p>
        </div>

        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-primary animate-pulse" />
            <span className="text-muted-foreground">In Progress</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-white/30" />
            <span className="text-muted-foreground">Planned</span>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative"
      >
        {/* Vertical line */}
        <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-primary via-primary/50 to-transparent" />

        <div className="space-y-6">
          {roadmapData.map((item) => {
            const isInProgress = item.status === 'in-progress';
            const isCompleted = item.status === 'completed';

            return (
              <motion.div
                key={item.quarter}
                variants={itemVariants}
                className="relative pl-16"
              >
                {/* Timeline node */}
                <motion.div
                  whileHover={{ scale: 1.2 }}
                  className={cn(
                    'absolute left-4 top-1 w-5 h-5 rounded-full flex items-center justify-center border-2',
                    isInProgress
                      ? 'bg-primary/20 border-primary shadow-[0_0_15px_rgba(0,212,170,0.5)]'
                      : isCompleted
                        ? 'bg-green-500/20 border-green-500'
                        : 'bg-white/10 border-white/30'
                  )}
                >
                  {isCompleted ? (
                    <CheckCircle className="h-3 w-3 text-green-400" />
                  ) : isInProgress ? (
                    <motion.div
                      className="w-2 h-2 rounded-full bg-primary"
                      animate={{ scale: [1, 1.3, 1] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                  ) : (
                    <Clock className="h-3 w-3 text-muted-foreground" />
                  )}
                </motion.div>

                {/* Content card */}
                <motion.div
                  whileHover={{ x: 5, scale: 1.01 }}
                  className={cn(
                    'p-4 rounded-xl border transition-all duration-300',
                    isInProgress
                      ? 'bg-primary/5 border-primary/30 hover:border-primary/50'
                      : 'bg-white/5 border-white/10 hover:border-white/20'
                  )}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span
                          className={cn(
                            'text-sm font-mono font-bold',
                            isInProgress ? 'text-primary' : 'text-white'
                          )}
                        >
                          {item.quarter}
                        </span>
                        {isInProgress && (
                          <span className="px-2 py-0.5 text-xs rounded bg-primary/20 text-primary uppercase">
                            Active
                          </span>
                        )}
                      </div>
                      <h4 className="text-white font-medium mb-1">{item.title}</h4>
                      <p className="text-sm text-muted-foreground">
                        {item.description}
                      </p>
                    </div>

                    <motion.div
                      whileHover={{ x: 5 }}
                      className={cn(
                        'flex-shrink-0 h-8 w-8 rounded-lg flex items-center justify-center',
                        isInProgress
                          ? 'bg-primary/20 text-primary'
                          : 'bg-white/5 text-muted-foreground'
                      )}
                    >
                      <ArrowRight className="h-4 w-4" />
                    </motion.div>
                  </div>
                </motion.div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Gap Closure Progress */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="mt-8 p-4 rounded-xl bg-white/5 border border-white/10"
      >
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-white">Competitive Gap Closure</span>
          <span className="text-sm font-mono text-primary">25% Complete</span>
        </div>
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '25%' }}
            transition={{ duration: 1.5, ease: 'easeOut', delay: 0.5 }}
            className="h-full bg-gradient-to-r from-primary to-blue-500 rounded-full"
          />
        </div>
        <div className="flex justify-between mt-2 text-xs text-muted-foreground">
          <span>Early Stage</span>
          <span>Market Leader</span>
        </div>
      </motion.div>
    </CyberCard>
  );
}
