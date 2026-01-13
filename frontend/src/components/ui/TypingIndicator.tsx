import { motion } from 'framer-motion';

interface TypingIndicatorProps {
  className?: string;
  dotClassName?: string;
}

/**
 * Animated typing indicator with three bouncing dots.
 * Used in chat interfaces to show the AI is "thinking".
 */
export function TypingIndicator({ className = '', dotClassName = '' }: TypingIndicatorProps) {
  return (
    <div className={`flex items-center gap-1.5 ${className}`}>
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className={`w-2 h-2 rounded-full bg-obsidian-teal ${dotClassName}`}
          animate={{
            y: [0, -6, 0],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: i * 0.15,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}

/**
 * Loading skeleton with shimmer effect.
 */
export function SkeletonLoader({
  className = '',
  lines = 1,
}: {
  className?: string;
  lines?: number;
}) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 bg-white/5 rounded overflow-hidden relative"
          style={{ width: i === lines - 1 && lines > 1 ? '60%' : '100%' }}
        >
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
            animate={{ x: ['-100%', '100%'] }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'linear',
            }}
          />
        </div>
      ))}
    </div>
  );
}

/**
 * Premium card skeleton with glass effect.
 */
export function CardSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`glass-panel-liquid rounded-2xl p-6 ${className}`}>
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-white/5 animate-pulse" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-white/5 rounded w-3/4 animate-pulse" />
            <div className="h-3 bg-white/5 rounded w-1/2 animate-pulse" />
          </div>
        </div>
        <SkeletonLoader lines={3} />
      </div>
    </div>
  );
}

export default TypingIndicator;
