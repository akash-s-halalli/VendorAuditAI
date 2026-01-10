import { Badge } from '@/components/ui';
import type { Severity } from '@/types/api';

interface SeverityBadgeProps {
  severity: Severity;
  size?: 'sm' | 'default';
  className?: string;
}

/**
 * SeverityBadge - Displays a colored badge based on severity level.
 * Severity levels: critical, high, medium, low, info
 */
export function SeverityBadge({ severity, size = 'default', className = '' }: SeverityBadgeProps) {
  const severityLabels: Record<Severity, string> = {
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low',
    info: 'Info',
  };

  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5' : '';

  return (
    <Badge
      variant={severity}
      className={`${sizeClasses} ${className}`.trim()}
    >
      {severityLabels[severity]}
    </Badge>
  );
}
