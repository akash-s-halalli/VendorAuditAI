import { Cpu, Shield, Zap, Activity, Terminal, Eye, Server, FileText } from 'lucide-react';
import { Badge } from '@/components/ui';

export function Agents() {
    const agents = [
        {
            id: 'sentinel',
            name: 'Sentinel Prime',
            role: 'Threat Detection',
            status: 'active',
            icon: Shield,
            color: 'text-primary',
            description: 'Continuous monitoring of vendor security posture and real-time threat detection.',
            tasks: ['Scanning inbound reports', 'Analyzing traffic patterns', 'Verifying signatures'],
            uptime: '99.99%',
        },
        {
            id: 'audit',
            name: 'Audit Core',
            role: 'Compliance Verification',
            status: 'idle',
            icon: FileText,
            color: 'text-purple-400',
            description: 'Automated analysis of SOC2, ISO27001, and SIG reports against compliance frameworks.',
            tasks: ['Waiting for queue', 'Index updated'],
            uptime: '98.50%',
        },
        {
            id: 'vector',
            name: 'Vector Analyst',
            role: 'Risk Assessment',
            status: 'processing',
            icon: Activity,
            color: 'text-yellow-400',
            description: 'Vector-based risk scoring and anomaly detection in vendor responses.',
            tasks: ['Calculating risk scores', 'Updating vendor profiles'],
            uptime: '99.95%',
        },
        {
            id: 'watchdog',
            name: 'Watchdog Zero',
            role: 'Vulnerability Scanner',
            status: 'active',
            icon: Eye,
            color: 'text-red-400',
            description: 'Deep scanning of public facing assets and dark web monitoring.',
            tasks: ['Scanning port 443', 'Checks complete'],
            uptime: '99.10%',
        },
    ];

    return (
        <div className="space-y-8 pb-8 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
                <div>
                    <h1 className="text-4xl font-bold tracking-tight text-white neon-text flex items-center gap-3">
                        <Cpu className="h-10 w-10 text-primary animate-pulse" />
                        AI Agent Network
                    </h1>
                    <p className="text-muted-foreground mt-2 text-lg">
                        Autonomous agents managing your third-party risk ecosystem.
                    </p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-panel border-green-500/20 shadow-[0_0_15px_rgba(34,197,94,0.2)]">
                        <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_green]" />
                        <span className="text-xs font-mono text-green-400 tracking-wider">NETWORK STABLE</span>
                    </div>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {agents.map((agent) => (
                    <div key={agent.id} className="glass-card rounded-xl border-white/5 overflow-hidden flex flex-col group hover:border-primary/30 transition-all duration-300 hover:shadow-2xl hover:shadow-primary/5">
                        {/* Header */}
                        <div className="p-6 border-b border-white/5 bg-white/5 flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className={`p-3 rounded-lg bg-black/40 ${agent.color} shadow-lg ring-1 ring-white/5`}>
                                    <agent.icon className="h-6 w-6" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg text-white group-hover:text-primary transition-colors tracking-tight">{agent.name}</h3>
                                    <p className="text-xs text-muted-foreground uppercase tracking-wider font-mono">{agent.role}</p>
                                </div>
                            </div>
                            <Badge variant="outline" className={`glass-panel border-0 ${agent.status === 'active' ? 'text-green-400 bg-green-500/10 shadow-[0_0_10px_rgba(34,197,94,0.2)]' : agent.status === 'processing' ? 'text-yellow-400 bg-yellow-500/10' : 'text-gray-400 bg-gray-500/10'} uppercase font-mono`}>
                                {agent.status}
                            </Badge>
                        </div>

                        {/* Body */}
                        <div className="p-6 space-y-6 flex-1 bg-black/20">
                            <p className="text-sm text-gray-400 leading-relaxed font-medium">
                                {agent.description}
                            </p>

                            {/* Stats */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-3 rounded-lg bg-black/40 border border-white/5 group-hover:border-white/10 transition-colors">
                                    <p className="text-xs text-muted-foreground mb-1 uppercase tracking-wider">Uptime</p>
                                    <p className="text-sm font-mono text-white font-bold">{agent.uptime}</p>
                                </div>
                                <div className="p-3 rounded-lg bg-black/40 border border-white/5 group-hover:border-white/10 transition-colors">
                                    <p className="text-xs text-muted-foreground mb-1 uppercase tracking-wider">Threads</p>
                                    <p className="text-sm font-mono text-white flex items-center gap-2 font-bold">
                                        <Server className="h-3 w-3 text-primary/70" />
                                        {Math.floor(Math.random() * 20) + 4}
                                    </p>
                                </div>
                            </div>

                            {/* Terminal / Tasks */}
                            <div className="rounded-lg bg-black border border-white/10 p-4 font-mono text-xs space-y-2 h-32 overflow-hidden relative shadow-inner">
                                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/80 pointer-events-none" />
                                <div className="absolute top-0 right-0 p-2 opacity-50">
                                    <Terminal className="h-4 w-4 text-muted-foreground" />
                                </div>
                                {agent.tasks.map((task, idx) => (
                                    <div key={idx} className="flex items-center gap-2 text-gray-500/80">
                                        <span className="text-primary">{'>'}</span>
                                        <span className={idx === agent.tasks.length - 1 ? "text-primary/90 animate-pulse" : ""}>{task}...</span>
                                    </div>
                                ))}
                                <div className="flex items-center gap-2 text-primary/50">
                                    <span className="animate-bounce">_</span>
                                </div>
                            </div>
                        </div>

                        {/* Footer Actions */}
                        <div className="px-6 py-4 border-t border-white/5 bg-white/5 flex items-center justify-between group-hover:bg-white/10 transition-colors">
                            <button className="text-xs uppercase tracking-wider font-bold text-muted-foreground hover:text-white transition-colors">
                                View Logs
                            </button>
                            <button className="text-xs uppercase tracking-wider font-bold text-primary hover:text-white transition-colors flex items-center gap-2">
                                <Zap className="h-3 w-3" />
                                Configure
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
