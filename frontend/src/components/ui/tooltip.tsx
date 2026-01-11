import * as React from 'react';
import { cn } from '@/lib/utils';

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

/**
 * Tooltip component for displaying helpful information on hover.
 *
 * @example
 * <Tooltip content="CAIQ: Cloud Security Alliance's questionnaire for vendor assessments">
 *   <span>CAIQ</span>
 * </Tooltip>
 */
export function Tooltip({ content, children, position = 'top', className }: TooltipProps) {
  const [isVisible, setIsVisible] = React.useState(false);

  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  return (
    <div
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div
          className={cn(
            'absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-md shadow-lg whitespace-nowrap',
            'animate-in fade-in-0 zoom-in-95 duration-200',
            positionClasses[position],
            className
          )}
        >
          {content}
          <div
            className={cn(
              'absolute w-2 h-2 bg-gray-900 rotate-45',
              position === 'top' && 'top-full left-1/2 -translate-x-1/2 -mt-1',
              position === 'bottom' && 'bottom-full left-1/2 -translate-x-1/2 mb-1',
              position === 'left' && 'left-full top-1/2 -translate-y-1/2 -ml-1',
              position === 'right' && 'right-full top-1/2 -translate-y-1/2 mr-1'
            )}
          />
        </div>
      )}
    </div>
  );
}

/**
 * InfoTooltip - A tooltip with an info icon trigger.
 */
export function InfoTooltip({ content, className }: { content: string; className?: string }) {
  return (
    <Tooltip content={content} className={className}>
      <button
        type="button"
        className="inline-flex items-center justify-center w-4 h-4 ml-1 text-muted-foreground hover:text-foreground rounded-full border"
        aria-label="More information"
      >
        <span className="text-xs">?</span>
      </button>
    </Tooltip>
  );
}
