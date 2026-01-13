import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  useReactTable,
  SortingState,
} from '@tanstack/react-table';
import { ArrowUpDown, Check, X, Search } from 'lucide-react';
import { CyberCard } from '@/components/ui/CyberCard';
import { cn } from '@/lib/utils';
import {
  competitors,
  vendorAuditAI,
  tierColors,
  formatCost,
  type Competitor,
} from '@/data/competitors';

interface TableData extends Competitor {
  costTier: string;
}

const columnHelper = createColumnHelper<TableData>();

const columns = [
  columnHelper.accessor('name', {
    header: ({ column }) => (
      <button
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        className="flex items-center gap-1 hover:text-primary transition-colors"
      >
        Company
        <ArrowUpDown className="h-3 w-3" />
      </button>
    ),
    cell: ({ row }) => {
      const isVendorAuditAI = row.original.id === 'vendorauditai';
      const tierColor = tierColors[row.original.tier];
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn(
              'w-2 h-2 rounded-full',
              isVendorAuditAI && 'animate-pulse'
            )}
            style={{
              backgroundColor: isVendorAuditAI ? '#00D4AA' : tierColor.primary,
              boxShadow: isVendorAuditAI ? '0 0 10px #00D4AA' : 'none',
            }}
          />
          <span className={cn(
            'font-medium',
            isVendorAuditAI ? 'text-primary' : 'text-white'
          )}>
            {row.original.name}
          </span>
        </div>
      );
    },
  }),
  columnHelper.accessor('docAnalysisTime', {
    header: ({ column }) => (
      <button
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        className="flex items-center gap-1 hover:text-primary transition-colors"
      >
        Analysis Time
        <ArrowUpDown className="h-3 w-3" />
      </button>
    ),
    cell: ({ getValue }) => {
      const value = getValue();
      const isfast = value.includes('min') || value === 'Seconds';
      return (
        <span className={cn(
          'font-mono text-sm',
          isfast ? 'text-green-400' : 'text-muted-foreground'
        )}>
          {value}
        </span>
      );
    },
  }),
  columnHelper.accessor('aiModel', {
    header: 'AI Model',
    cell: ({ getValue, row }) => {
      const isVendorAuditAI = row.original.id === 'vendorauditai';
      return (
        <span className={cn(
          'text-sm',
          isVendorAuditAI ? 'text-primary font-medium' : 'text-muted-foreground'
        )}>
          {getValue()}
        </span>
      );
    },
  }),
  columnHelper.accessor('nlQueryCitations', {
    header: 'NL Query',
    cell: ({ getValue }) => (
      getValue() ? (
        <Check className="h-4 w-4 text-green-400" />
      ) : (
        <X className="h-4 w-4 text-red-400/50" />
      )
    ),
  }),
  columnHelper.accessor('autonomousAgents', {
    header: ({ column }) => (
      <button
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        className="flex items-center gap-1 hover:text-primary transition-colors"
      >
        AI Agents
        <ArrowUpDown className="h-3 w-3" />
      </button>
    ),
    cell: ({ getValue, row }) => {
      const value = getValue();
      const isVendorAuditAI = row.original.id === 'vendorauditai';
      return (
        <span className={cn(
          'font-mono font-bold',
          value >= 4 ? 'text-primary' : value >= 1 ? 'text-yellow-400' : 'text-muted-foreground'
        )}>
          {value}
          {isVendorAuditAI && <span className="text-xs text-muted-foreground ml-1">(4x)</span>}
        </span>
      );
    },
  }),
  columnHelper.accessor('frameworksSupported', {
    header: ({ column }) => (
      <button
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        className="flex items-center gap-1 hover:text-primary transition-colors"
      >
        Frameworks
        <ArrowUpDown className="h-3 w-3" />
      </button>
    ),
    cell: ({ getValue }) => (
      <span className="font-mono text-white">{getValue()}</span>
    ),
  }),
  columnHelper.accessor('aiCapabilityScore', {
    header: ({ column }) => (
      <button
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        className="flex items-center gap-1 hover:text-primary transition-colors"
      >
        AI Score
        <ArrowUpDown className="h-3 w-3" />
      </button>
    ),
    cell: ({ getValue, row }) => {
      const value = getValue();
      const isVendorAuditAI = row.original.id === 'vendorauditai';
      return (
        <div className="flex items-center gap-2">
          <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${value}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className={cn(
                'h-full rounded-full',
                isVendorAuditAI ? 'bg-primary' : value >= 80 ? 'bg-green-500' : value >= 60 ? 'bg-yellow-500' : 'bg-red-500'
              )}
            />
          </div>
          <span className={cn(
            'font-mono text-sm',
            isVendorAuditAI ? 'text-primary font-bold' : 'text-white'
          )}>
            {value}
          </span>
        </div>
      );
    },
  }),
  columnHelper.accessor('costTier', {
    header: ({ column }) => (
      <button
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        className="flex items-center gap-1 hover:text-primary transition-colors"
      >
        Cost
        <ArrowUpDown className="h-3 w-3" />
      </button>
    ),
    cell: ({ getValue }) => {
      const value = getValue();
      const colorClass = value === '$' || value === '$$' ? 'text-green-400' : value === '$$$' ? 'text-yellow-400' : 'text-red-400';
      return (
        <span className={cn('font-mono font-bold', colorClass)}>
          {value}
        </span>
      );
    },
  }),
];

export function FeatureComparisonTable() {
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'aiCapabilityScore', desc: true },
  ]);
  const [globalFilter, setGlobalFilter] = useState('');

  const tableData = useMemo<TableData[]>(() => {
    const allCompetitors = [vendorAuditAI, ...competitors];
    return allCompetitors.map((c) => ({
      ...c,
      costTier: formatCost(c),
    }));
  }, []);

  const table = useReactTable({
    data: tableData,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return (
    <CyberCard className="p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <h3 className="text-xl font-bold text-white mb-1">Feature Comparison Matrix</h3>
          <p className="text-sm text-muted-foreground">
            Compare AI capabilities across {tableData.length} competitors
          </p>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search competitors..."
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-muted-foreground focus:outline-none focus:border-primary/50 transition-colors w-64"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="border-b border-white/10">
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row, index) => {
              const isVendorAuditAI = row.original.id === 'vendorauditai';
              return (
                <motion.tr
                  key={row.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.02 }}
                  className={cn(
                    'border-b border-white/5 hover:bg-white/5 transition-colors',
                    isVendorAuditAI && 'bg-primary/5 border-primary/20'
                  )}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-3 whitespace-nowrap">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="mt-4 pt-4 border-t border-white/10 flex flex-wrap gap-6 text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <span className="font-mono text-green-400">$</span>
          <span>{'< $15K/year'}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-green-400">$$</span>
          <span>$15-50K/year</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-yellow-400">$$$</span>
          <span>$50-150K/year</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-red-400">$$$$</span>
          <span>$150K+/year</span>
        </div>
      </div>
    </CyberCard>
  );
}
