import { useRef, useState } from 'react';
import { cn } from '@/lib/utils';

interface CyberCardProps {
    children: React.ReactNode;
    className?: string;
    variant?: 'default' | 'danger' | 'warning' | 'success';
    hoverEffect?: boolean;
    onClick?: () => void;
}

export function CyberCard({
    children,
    className,
    variant = 'default',
    hoverEffect = true,
    onClick
}: CyberCardProps) {
    const divRef = useRef<HTMLDivElement>(null);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [opacity, setOpacity] = useState(0);

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!divRef.current || !hoverEffect) return;

        const div = divRef.current;
        const rect = div.getBoundingClientRect();

        setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
    };

    const handleMouseEnter = () => {
        if (hoverEffect) setOpacity(1);
    };

    const handleMouseLeave = () => {
        if (hoverEffect) setOpacity(0);
    };

    const borderColor = {
        default: 'group-hover:border-primary/50',
        danger: 'group-hover:border-red-500/50',
        warning: 'group-hover:border-yellow-500/50',
        success: 'group-hover:border-green-500/50'
    }[variant];

    const glowColor = {
        default: 'rgba(0, 242, 255, 0.15)',
        danger: 'rgba(239, 68, 68, 0.15)',
        warning: 'rgba(234, 179, 8, 0.15)',
        success: 'rgba(34, 197, 94, 0.15)'
    }[variant];

    return (
        <div
            ref={divRef}
            onMouseMove={handleMouseMove}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            onClick={onClick}
            className={cn(
                "relative rounded-xl border border-white/5 bg-black/20 backdrop-blur-sm overflow-hidden group transition-all duration-300",
                borderColor,
                onClick && "cursor-pointer",
                className
            )}
        >
            {/* Spotlight Effect */}
            <div
                className="pointer-events-none absolute -inset-px opacity-0 transition duration-300"
                style={{
                    opacity,
                    background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, ${glowColor}, transparent 40%)`,
                }}
            />

            {/* HUD Markers */}
            <div className="absolute top-0 left-0 w-2 h-2 border-l border-t border-white/20 rounded-tl-sm" />
            <div className="absolute top-0 right-0 w-2 h-2 border-r border-t border-white/20 rounded-tr-sm" />
            <div className="absolute bottom-0 left-0 w-2 h-2 border-l border-b border-white/20 rounded-bl-sm" />
            <div className="absolute bottom-0 right-0 w-2 h-2 border-r border-b border-white/20 rounded-br-sm" />

            {/* Content */}
            <div className="relative h-full">
                {children}
            </div>
        </div>
    );
}
