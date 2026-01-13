import { useEffect, useState } from 'react';
import { useMotionValue, useTransform, animate } from 'framer-motion';

interface AnimatedCounterProps {
  value: number;
  duration?: number;
  className?: string;
  formatValue?: (value: number) => string;
}

/**
 * Animated counter component that counts up from 0 to the target value.
 * Uses Framer Motion for smooth animations.
 */
export function AnimatedCounter({
  value,
  duration = 2,
  className = '',
  formatValue = (v) => v.toLocaleString(),
}: AnimatedCounterProps) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest));
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const controls = animate(count, value, {
      duration,
      ease: 'easeOut',
    });

    const unsubscribe = rounded.on('change', (v) => setDisplayValue(v));

    return () => {
      controls.stop();
      unsubscribe();
    };
  }, [value, duration, count, rounded]);

  return <span className={className}>{formatValue(displayValue)}</span>;
}

/**
 * Animated percentage counter with optional suffix.
 */
export function AnimatedPercentage({
  value,
  duration = 2,
  className = '',
  decimals = 1,
}: {
  value: number;
  duration?: number;
  className?: string;
  decimals?: number;
}) {
  const count = useMotionValue(0);
  const [displayValue, setDisplayValue] = useState('0');

  useEffect(() => {
    const controls = animate(count, value, {
      duration,
      ease: 'easeOut',
    });

    const unsubscribe = count.on('change', (v) => {
      setDisplayValue(v.toFixed(decimals));
    });

    return () => {
      controls.stop();
      unsubscribe();
    };
  }, [value, duration, count, decimals]);

  return <span className={className}>{displayValue}%</span>;
}

export default AnimatedCounter;
