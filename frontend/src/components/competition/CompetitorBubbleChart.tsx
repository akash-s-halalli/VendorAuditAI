import { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { CyberCard } from '@/components/ui/CyberCard';
import {
  competitors,
  vendorAuditAI,
  tierColors,
  tierLabels,
  formatValuation,
  type Competitor,
} from '@/data/competitors';

interface BubbleData {
  name: string;
  aiCapabilityScore: number;
  annualCostMax: number;
  valuation: number;
  tier: number;
  isVendorAuditAI: boolean;
  competitor: Competitor;
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: BubbleData }> }) => {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;
  const tierColor = tierColors[data.tier];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-black/90 backdrop-blur-xl border border-white/20 rounded-xl p-4 shadow-2xl max-w-xs"
    >
      <div className="flex items-center gap-2 mb-3">
        <span
          className={`px-2 py-0.5 rounded text-xs font-medium uppercase ${tierColor.bg} ${tierColor.text} ${tierColor.border} border`}
        >
          Tier {data.tier}
        </span>
        <span className="text-white font-bold">{data.name}</span>
      </div>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">AI Capability</span>
          <span className="text-white font-mono">{data.aiCapabilityScore}/100</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Annual Cost</span>
          <span className="text-white font-mono">${data.competitor.annualCost.min}K - ${data.competitor.annualCost.max}K</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Valuation</span>
          <span className="text-white font-mono">{formatValuation(data.valuation)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Customers</span>
          <span className="text-white font-mono">{data.competitor.customers.toLocaleString()}</span>
        </div>
        <div className="pt-2 border-t border-white/10">
          <p className="text-xs text-muted-foreground">{data.competitor.keyStrength}</p>
        </div>
      </div>
      {data.isVendorAuditAI && (
        <div className="mt-3 pt-2 border-t border-primary/30">
          <p className="text-xs text-primary font-medium">Our Position</p>
        </div>
      )}
    </motion.div>
  );
};

export function CompetitorBubbleChart() {
  const bubbleData = useMemo<BubbleData[]>(() => {
    const allCompetitors = [...competitors, vendorAuditAI];
    return allCompetitors.map((c) => ({
      name: c.name,
      aiCapabilityScore: c.aiCapabilityScore,
      annualCostMax: c.annualCost.max,
      valuation: c.valuation,
      tier: c.tier,
      isVendorAuditAI: c.id === 'vendorauditai',
      competitor: c,
    }));
  }, []);

  // Calculate bubble sizes based on valuation (log scale for better visualization)
  const getSize = (valuation: number): number => {
    const minSize = 60;
    const maxSize = 400;
    const logVal = Math.log10(valuation + 1);
    const maxLogVal = Math.log10(200000); // Max valuation (SAP)
    return minSize + (logVal / maxLogVal) * (maxSize - minSize);
  };

  return (
    <CyberCard className="p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <h3 className="text-xl font-bold text-white mb-1">Competitive Landscape</h3>
          <p className="text-sm text-muted-foreground">
            AI Capability vs. Annual Cost | Bubble size = Valuation
          </p>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap gap-3">
          {[1, 2, 3, 4, 5].map((tier) => (
            <div key={tier} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: tierColors[tier].primary }}
              />
              <span className="text-xs text-muted-foreground">{tierLabels[tier]}</span>
            </div>
          ))}
          <div className="flex items-center gap-2">
            <div
              className="w-4 h-4 rounded-full border-2"
              style={{
                borderColor: '#00D4AA',
                boxShadow: '0 0 10px #00D4AA',
              }}
            />
            <span className="text-xs text-primary font-medium">VendorAuditAI</span>
          </div>
        </div>
      </div>

      <div className="h-[500px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 40, bottom: 40, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis
              type="number"
              dataKey="aiCapabilityScore"
              domain={[25, 100]}
              name="AI Capability"
              tick={{ fill: '#9CA3AF', fontSize: 12 }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              label={{
                value: 'AI Capability Score',
                position: 'bottom',
                offset: 20,
                fill: '#9CA3AF',
                fontSize: 12,
              }}
            />
            <YAxis
              type="number"
              dataKey="annualCostMax"
              domain={[0, 850]}
              name="Annual Cost ($K)"
              tick={{ fill: '#9CA3AF', fontSize: 12 }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              tickLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              label={{
                value: 'Annual Cost ($K)',
                angle: -90,
                position: 'insideLeft',
                offset: 10,
                fill: '#9CA3AF',
                fontSize: 12,
              }}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* Reference lines for VendorAuditAI position */}
            <ReferenceLine
              x={vendorAuditAI.aiCapabilityScore}
              stroke="#00D4AA"
              strokeDasharray="5 5"
              strokeOpacity={0.3}
            />
            <ReferenceLine
              y={vendorAuditAI.annualCost.max}
              stroke="#00D4AA"
              strokeDasharray="5 5"
              strokeOpacity={0.3}
            />

            <Scatter data={bubbleData} shape="circle">
              {bubbleData.map((entry, index) => {
                const isVendorAuditAI = entry.isVendorAuditAI;
                return (
                  <Cell
                    key={`cell-${index}`}
                    fill={isVendorAuditAI ? '#00D4AA' : tierColors[entry.tier].primary}
                    fillOpacity={isVendorAuditAI ? 1 : 0.7}
                    stroke={isVendorAuditAI ? '#00D4AA' : 'transparent'}
                    strokeWidth={isVendorAuditAI ? 3 : 0}
                    r={getSize(entry.valuation) / 10}
                    style={{
                      filter: isVendorAuditAI ? 'drop-shadow(0 0 15px #00D4AA)' : 'none',
                    }}
                  />
                );
              })}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Quadrant Labels */}
      <div className="grid grid-cols-2 gap-4 mt-6 text-center text-xs">
        <div className="p-3 rounded-lg bg-green-500/5 border border-green-500/20">
          <p className="text-green-400 font-medium">High AI + Low Cost</p>
          <p className="text-muted-foreground mt-1">Optimal Position (VendorAuditAI)</p>
        </div>
        <div className="p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/20">
          <p className="text-yellow-400 font-medium">High AI + High Cost</p>
          <p className="text-muted-foreground mt-1">Premium Enterprise (Drata, Vanta)</p>
        </div>
        <div className="p-3 rounded-lg bg-blue-500/5 border border-blue-500/20">
          <p className="text-blue-400 font-medium">Low AI + Low Cost</p>
          <p className="text-muted-foreground mt-1">Basic Solutions (Scrut, Sprinto)</p>
        </div>
        <div className="p-3 rounded-lg bg-red-500/5 border border-red-500/20">
          <p className="text-red-400 font-medium">Low AI + High Cost</p>
          <p className="text-muted-foreground mt-1">Legacy Enterprise (SAP, ServiceNow)</p>
        </div>
      </div>
    </CyberCard>
  );
}
