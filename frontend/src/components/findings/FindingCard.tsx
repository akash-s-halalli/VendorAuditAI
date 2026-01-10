import { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, Shield, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui';
import { SeverityBadge } from './SeverityBadge';
import type { Finding } from '@/types/api';
import { getConfidenceLevel } from '@/lib/utils';

interface FindingCardProps {
  finding: Finding;
}

/**
 * FindingCard - Expandable card displaying a single finding with all details.
 * Shows title, severity, and framework control reference. Expands to show
 * description, evidence, citations, and confidence score.
 */
export function FindingCard({ finding }: FindingCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => setIsExpanded(!isExpanded);

  const confidenceLevel = getConfidenceLevel(finding.confidenceScore);
  const confidencePercent = Math.round(finding.confidenceScore * 100);

  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardHeader
        className="cursor-pointer p-4"
        onClick={toggleExpand}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <SeverityBadge severity={finding.severity} />
              <span className="text-xs text-muted-foreground bg-secondary px-2 py-0.5 rounded">
                {finding.findingType.charAt(0).toUpperCase() + finding.findingType.slice(1)}
              </span>
            </div>
            <h3 className="font-semibold text-base leading-tight">{finding.title}</h3>
            <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Shield className="h-3.5 w-3.5" />
                <span>{finding.framework}</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="font-medium">{finding.controlId}</span>
                {finding.controlName && (
                  <span className="truncate max-w-[200px]">- {finding.controlName}</span>
                )}
              </div>
            </div>
          </div>
          <button
            className="p-1 rounded-full hover:bg-accent flex-shrink-0"
            aria-label={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? (
              <ChevronUp className="h-5 w-5 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-5 w-5 text-muted-foreground" />
            )}
          </button>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0 px-4 pb-4 border-t">
          <div className="space-y-4 mt-4">
            {/* Description */}
            <div>
              <h4 className="text-sm font-medium text-muted-foreground mb-1">Description</h4>
              <p className="text-sm">{finding.description}</p>
            </div>

            {/* Evidence */}
            {finding.evidence && (
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-1">Evidence</h4>
                <p className="text-sm bg-secondary/50 p-3 rounded-md">{finding.evidence}</p>
              </div>
            )}

            {/* Recommendation */}
            {finding.recommendation && (
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-1 flex items-center gap-1">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  Recommendation
                </h4>
                <p className="text-sm">{finding.recommendation}</p>
              </div>
            )}

            {/* Citations */}
            {finding.citations && finding.citations.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-1">
                  <FileText className="h-3.5 w-3.5" />
                  Citations
                </h4>
                <div className="space-y-2">
                  {finding.citations.map((citation, index) => (
                    <div
                      key={index}
                      className="text-sm bg-muted/50 p-3 rounded-md border-l-2 border-primary"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium bg-primary/10 text-primary px-2 py-0.5 rounded">
                          Page {citation.page}
                          {citation.paragraph && `, Para ${citation.paragraph}`}
                        </span>
                      </div>
                      <p className="text-muted-foreground italic">"{citation.text}"</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Page References */}
            {finding.pageReferences && finding.pageReferences.length > 0 && (
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-medium text-muted-foreground">Page References:</h4>
                <div className="flex flex-wrap gap-1">
                  {finding.pageReferences.map((page) => (
                    <span
                      key={page}
                      className="text-xs bg-secondary px-2 py-0.5 rounded"
                    >
                      p.{page}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Confidence Score */}
            <div className="flex items-center justify-between pt-2 border-t">
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Confidence:</span>
                <span className={`text-sm font-medium ${
                  confidencePercent >= 75 ? 'text-green-600' :
                  confidencePercent >= 50 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {confidencePercent}% ({confidenceLevel})
                </span>
              </div>
              <div className="w-24 h-2 bg-secondary rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    confidencePercent >= 75 ? 'bg-green-500' :
                    confidencePercent >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${confidencePercent}%` }}
                />
              </div>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
