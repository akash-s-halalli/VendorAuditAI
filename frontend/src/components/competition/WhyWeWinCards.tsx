import { motion } from 'framer-motion';
import { Brain, Cpu, Zap, Target, Layers } from 'lucide-react';
import { CyberCard } from '@/components/ui/CyberCard';
import { AnimatedCounter } from '@/components/ui/AnimatedCounter';
import { whyWeWinData } from '@/data/competitors';

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
  hidden: { y: 30, opacity: 0 },
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

const iconMap: Record<string, React.ElementType> = {
  brain: Brain,
  cpu: Cpu,
  zap: Zap,
  target: Target,
  layers: Layers,
};

export function WhyWeWinCards() {
  return (
    <div className="space-y-6">
      <div className="text-center max-w-2xl mx-auto">
        <h3 className="text-3xl font-bold text-white mb-2">
          Why <span className="text-primary">VendorAuditAI</span> Wins
        </h3>
        <p className="text-muted-foreground">
          Our competitive advantages that set us apart from the $8.6B TPRM market
        </p>
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4"
      >
        {whyWeWinData.map((item) => {
          const Icon = iconMap[item.icon] || Brain;
          const statValue = parseInt(item.stat.replace(/[^0-9]/g, '')) || 0;
          const hasPercentOrX = item.stat.includes('%') || item.stat.includes('x');

          return (
            <motion.div key={item.title} variants={itemVariants}>
              <CyberCard className="p-5 h-full text-center group hover:border-primary/30 transition-all duration-300">
                <motion.div
                  whileHover={{ scale: 1.1, rotate: 10 }}
                  className="h-14 w-14 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center mx-auto mb-4 group-hover:bg-primary/20 transition-colors"
                >
                  <Icon className="h-7 w-7 text-primary" />
                </motion.div>

                <div className="mb-3">
                  <motion.p
                    className="text-3xl font-bold text-primary font-mono"
                    whileHover={{ scale: 1.05 }}
                  >
                    {hasPercentOrX ? (
                      <>
                        <AnimatedCounter value={statValue} duration={1.5} />
                        {item.stat.includes('%') ? '%' : 'x'}
                      </>
                    ) : (
                      item.stat
                    )}
                  </motion.p>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider">
                    {item.statLabel}
                  </p>
                </div>

                <h4 className="text-white font-bold mb-2">{item.title}</h4>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {item.description}
                </p>

                {/* Hover indicator */}
                <motion.div
                  initial={{ scaleX: 0 }}
                  whileHover={{ scaleX: 1 }}
                  className="h-0.5 w-full bg-gradient-to-r from-transparent via-primary to-transparent mt-4 origin-center"
                />
              </CyberCard>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Bottom CTA */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="text-center pt-4"
      >
        <p className="text-sm text-muted-foreground">
          Only <span className="text-primary font-bold">9%</span> of organizations have advanced TPRM capabilities.
          <br />
          <span className="text-white">We&apos;re built to capture the other 91%.</span>
        </p>
      </motion.div>
    </div>
  );
}
