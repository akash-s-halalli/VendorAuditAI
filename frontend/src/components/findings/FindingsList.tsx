import { useMemo, useState } from 'react';
import { Filter, SortAsc, SortDesc, Search } from 'lucide-react';
import { Button, Input, Card, CardContent } from '@/components/ui';
import { FindingCard } from './FindingCard';
import { SeverityBadge } from './SeverityBadge';
import type { Finding, Severity } from '@/types/api';

interface FindingsListProps {
  findings: Finding[];
  isLoading?: boolean;
}

type SortField = 'severity' | 'confidence' | 'date';
type SortOrder = 'asc' | 'desc';

const severityOrder: Record<Severity, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
  info: 4,
};

const severityFilters: Severity[] = ['critical', 'high', 'medium', 'low'];

/**
 * FindingsList - Displays a filterable and sortable list of findings.
 * Includes severity filters, search, and sorting options.
 */
export function FindingsList({ findings, isLoading = false }: FindingsListProps) {
  const [selectedSeverities, setSelectedSeverities] = useState<Set<Severity>>(
    new Set(severityFilters)
  );
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState<SortField>('severity');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');

  const toggleSeverity = (severity: Severity) => {
    setSelectedSeverities((prev) => {
      const next = new Set(prev);
      if (next.has(severity)) {
        next.delete(severity);
      } else {
        next.add(severity);
      }
      return next;
    });
  };

  const selectAllSeverities = () => {
    setSelectedSeverities(new Set(severityFilters));
  };

  const clearAllSeverities = () => {
    setSelectedSeverities(new Set());
  };

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const filteredAndSortedFindings = useMemo(() => {
    let result = findings.filter((finding) => {
      // Severity filter
      if (!selectedSeverities.has(finding.severity)) {
        return false;
      }

      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          finding.title.toLowerCase().includes(query) ||
          finding.description.toLowerCase().includes(query) ||
          finding.controlId.toLowerCase().includes(query) ||
          finding.controlName.toLowerCase().includes(query) ||
          finding.framework.toLowerCase().includes(query)
        );
      }

      return true;
    });

    // Sort
    result.sort((a, b) => {
      let comparison = 0;

      switch (sortField) {
        case 'severity':
          comparison = severityOrder[a.severity] - severityOrder[b.severity];
          break;
        case 'confidence':
          comparison = b.confidenceScore - a.confidenceScore;
          break;
        case 'date':
          comparison = new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
          break;
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [findings, selectedSeverities, searchQuery, sortField, sortOrder]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className="h-6 w-16 bg-muted rounded" />
                <div className="flex-1 space-y-2">
                  <div className="h-5 bg-muted rounded w-3/4" />
                  <div className="h-4 bg-muted rounded w-1/2" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters and Search */}
      <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
        {/* Severity Filters */}
        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground mr-1">Severity:</span>
          {severityFilters.map((severity) => (
            <button
              key={severity}
              onClick={() => toggleSeverity(severity)}
              className={`transition-opacity ${
                selectedSeverities.has(severity) ? 'opacity-100' : 'opacity-40'
              }`}
            >
              <SeverityBadge severity={severity} size="sm" />
            </button>
          ))}
          <div className="flex gap-1 ml-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={selectAllSeverities}
              className="text-xs h-7 px-2"
            >
              All
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearAllSeverities}
              className="text-xs h-7 px-2"
            >
              None
            </Button>
          </div>
        </div>

        {/* Search and Sort */}
        <div className="flex items-center gap-2 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search findings..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Sort buttons */}
          <div className="flex border rounded-md">
            <Button
              variant={sortField === 'severity' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => toggleSort('severity')}
              className="rounded-r-none text-xs"
            >
              Severity
              {sortField === 'severity' &&
                (sortOrder === 'asc' ? (
                  <SortAsc className="h-3 w-3 ml-1" />
                ) : (
                  <SortDesc className="h-3 w-3 ml-1" />
                ))}
            </Button>
            <Button
              variant={sortField === 'confidence' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => toggleSort('confidence')}
              className="rounded-none border-l text-xs"
            >
              Confidence
              {sortField === 'confidence' &&
                (sortOrder === 'asc' ? (
                  <SortAsc className="h-3 w-3 ml-1" />
                ) : (
                  <SortDesc className="h-3 w-3 ml-1" />
                ))}
            </Button>
            <Button
              variant={sortField === 'date' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => toggleSort('date')}
              className="rounded-l-none border-l text-xs"
            >
              Date
              {sortField === 'date' &&
                (sortOrder === 'asc' ? (
                  <SortAsc className="h-3 w-3 ml-1" />
                ) : (
                  <SortDesc className="h-3 w-3 ml-1" />
                ))}
            </Button>
          </div>
        </div>
      </div>

      {/* Results count */}
      <div className="text-sm text-muted-foreground">
        Showing {filteredAndSortedFindings.length} of {findings.length} findings
      </div>

      {/* Findings List */}
      {filteredAndSortedFindings.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Search className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No findings match your filters</h3>
            <p className="text-muted-foreground text-center">
              Try adjusting your severity filters or search query.
            </p>
            <Button variant="outline" className="mt-4" onClick={selectAllSeverities}>
              Reset Filters
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {filteredAndSortedFindings.map((finding) => (
            <FindingCard key={finding.id} finding={finding} />
          ))}
        </div>
      )}
    </div>
  );
}
