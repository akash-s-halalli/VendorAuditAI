import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from 'recharts';
import { Zap, Clock } from 'lucide-react';
import { CyberCard } from '@/components/ui/CyberCard';
import { AnimatedCounter } from '@/components/ui/AnimatedCounter';
import { speedComparisonData } from '@/data/competitors';

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: typeof speedComparisonData[0] }> }) => {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;
  const isVendorAuditAI = data.name === 'VendorAuditAI';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-black/90 backdrop-blur-xl border border-white/20 rounded-xl p-4 shadow-2xl"
    >
      <p className={`font-bold ${isVendorAuditAI ? 'text-primary' : 'text-white'}`}>
        {data.name}
      </p>
      <p className="text-sm text-muted-foreground mt-1">
        Document Analysis: <span className="text-white font-mono">{data.display}</span>
      </p>
      {isVendorAuditAI && (
        <p className="text-xs text-primary mt-2">
          97% faster than industry standard
        </p>
      )}
    </motion.div>
  );
};

export function SpeedComparisonChart() {
  // Calculate time savings
  const industryStandard = speedComparisonData.find((d) => d.name === 'Industry Standard')?.time || 480;
  const vendorAuditAITime = speedComparisonData.find((d) => d.name === 'VendorAuditAI')?.time || 15;
  const timeSavingsPercent = Math.round(((industryStandard - vendorAuditAITime) / industryStandard) * 100);

  return (
    <CyberCard className="p-6">
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6 mb-6">
        <div>
          <h3 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
            <Zap className="h-5 w-5 text-primary" />
            Document Analysis Speed
          </h3>
          <p className="text-sm text-muted-foreground">
            Time required to analyze a standard vendor security document
          </p>
        </div>

        {/* Time Savings Highlight */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="flex items-center gap-4 p-4 rounded-xl bg-primary/10 border border-primary/30"
        >
          <div className="text-center">
            <p className="text-4xl font-bold text-primary font-mono">
              <AnimatedCounter value={timeSavingsPercent} duration={2} />%
            </p>
            <p className="text-xs text-primary/80 uppercase tracking-wider">Time Saved</p>
          </div>
          <div className="w-px h-12 bg-primary/30" />
          <div className="text-center">
            <p className="text-2xl font-bold text-white font-mono">15 min</p>
            <p className="text-xs text-muted-foreground uppercase tracking-wider">VendorAuditAI</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-muted-foreground font-mono">8 hrs</p>
            <p className="text-xs text-muted-foreground uppercase tracking-wider">Industry</p>
          </div>
        </motion.div>
      </div>

      <div className="h-[350px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={speedComparisonData}
            layout="vertical"
            margin={{ top: 10, right: 80, bottom: 10, left: 130 }}
          >
            <XAxis
              type="number"
              domain={[0, 500]}
              tick={{ fill: '#9CA3AF', fontSize: 12 }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              tickFormatter={(value) => `${value} min`}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: '#9CA3AF', fontSize: 12 }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              tickLine={false}
              width={120}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
            <Bar dataKey="time" radius={[0, 4, 4, 0]} barSize={24}>
              {speedComparisonData.map((entry, index) => {
                const isVendorAuditAI = entry.name === 'VendorAuditAI';
                return (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.color}
                    style={{
                      filter: isVendorAuditAI ? 'drop-shadow(0 0 10px #00D4AA)' : 'none',
                    }}
                  />
                );
              })}
              <LabelList
                dataKey="display"
                position="right"
                fill="#9CA3AF"
                fontSize={12}
                fontFamily="monospace"
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="p-4 rounded-lg bg-white/5 border border-white/10"
        >
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4 text-red-400" />
            <span className="text-sm font-medium text-white">Legacy Enterprise</span>
          </div>
          <p className="text-xs text-muted-foreground">
            SAP, ServiceNow, MetricStream require <span className="text-red-400 font-mono">days</span> for manual review processes
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="p-4 rounded-lg bg-white/5 border border-white/10"
        >
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4 text-yellow-400" />
            <span className="text-sm font-medium text-white">Modern Competitors</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Drata, Vanta offer <span className="text-yellow-400 font-mono">hours</span> with AI-assisted workflows
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="p-4 rounded-lg bg-primary/5 border border-primary/30"
        >
          <div className="flex items-center gap-2 mb-2">
            <Zap className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">VendorAuditAI</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Claude Opus 4.5 enables <span className="text-primary font-mono">15-minute</span> comprehensive analysis
          </p>
        </motion.div>
      </div>
    </CyberCard>
  );
}
