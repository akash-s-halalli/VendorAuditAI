import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Play, FileText, AlertTriangle, Loader2, RefreshCw } from 'lucide-react';
import { Button, Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { FindingsSummary, FindingsList } from '@/components/findings';
import apiClient, { getApiErrorMessage } from '@/lib/api';
import type { Document, Finding, AnalysisRun, Severity } from '@/types/api';

interface AnalysisResponse {
  run: AnalysisRun;
  findings: Finding[];
}

/**
 * Analysis Page - Document analysis dashboard with findings display.
 * Allows users to select a document, run analysis, and view findings.
 */
export function Analysis() {
  const queryClient = useQueryClient();
  const [selectedDocumentId, setSelectedDocumentId] = useState<string>('');
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  // Fetch documents for dropdown
  const { data: documentsResponse, isLoading: isLoadingDocuments } = useQuery({
    queryKey: ['documents-for-analysis'],
    queryFn: async () => {
      const response = await apiClient.get('/documents?limit=100&status=analyzed,parsed');
      return response.data;
    },
  });

  const documents: Document[] = documentsResponse?.data || [];

  // Fetch analysis results for selected document
  const {
    data: analysisData,
    isLoading: isLoadingAnalysis,
    refetch: refetchAnalysis,
  } = useQuery<AnalysisResponse>({
    queryKey: ['analysis', selectedDocumentId],
    queryFn: async () => {
      const response = await apiClient.get(`/analysis/documents/${selectedDocumentId}`);
      return response.data;
    },
    enabled: !!selectedDocumentId,
  });

  // Run analysis mutation
  const runAnalysisMutation = useMutation({
    mutationFn: async (documentId: string) => {
      const response = await apiClient.post(`/analysis/run`, {
        documentId,
        frameworkIds: [], // Use default frameworks
        analysisType: 'full',
      });
      return response.data;
    },
    onSuccess: () => {
      setAnalysisError(null);
      // Invalidate and refetch analysis data
      queryClient.invalidateQueries({ queryKey: ['analysis', selectedDocumentId] });
      queryClient.invalidateQueries({ queryKey: ['documents-for-analysis'] });
    },
    onError: (error) => {
      setAnalysisError(getApiErrorMessage(error));
    },
  });

  const handleRunAnalysis = () => {
    if (selectedDocumentId) {
      runAnalysisMutation.mutate(selectedDocumentId);
    }
  };

  const selectedDocument = documents.find((d) => d.id === selectedDocumentId);
  const findings = analysisData?.findings || [];
  const analysisRun = analysisData?.run;

  // Calculate severity counts
  const bySeverity: Record<Severity, number> = {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    info: 0,
  };

  findings.forEach((finding) => {
    if (finding.severity in bySeverity) {
      bySeverity[finding.severity]++;
    }
  });

  const isAnalyzing = runAnalysisMutation.isPending || analysisRun?.status === 'processing';

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Analysis Dashboard</h1>
        <p className="text-muted-foreground">
          Analyze security documents and review findings
        </p>
      </div>

      {/* Document Selection */}
      <Card className="mb-6">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Document Selection
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-end">
            <div className="flex-1 w-full md:w-auto">
              <label
                htmlFor="document-select"
                className="block text-sm font-medium text-muted-foreground mb-2"
              >
                Select a document to analyze
              </label>
              <select
                id="document-select"
                value={selectedDocumentId}
                onChange={(e) => setSelectedDocumentId(e.target.value)}
                className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                disabled={isLoadingDocuments}
              >
                <option value="">
                  {isLoadingDocuments ? 'Loading documents...' : 'Choose a document...'}
                </option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.originalFilename} ({doc.docType.toUpperCase()})
                    {doc.status === 'analyzed' ? ' - Analyzed' : ''}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleRunAnalysis}
                disabled={!selectedDocumentId || isAnalyzing}
                isLoading={isAnalyzing}
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Run Analysis
                  </>
                )}
              </Button>

              {selectedDocumentId && (
                <Button
                  variant="outline"
                  onClick={() => refetchAnalysis()}
                  disabled={isLoadingAnalysis}
                >
                  <RefreshCw className={`h-4 w-4 ${isLoadingAnalysis ? 'animate-spin' : ''}`} />
                </Button>
              )}
            </div>
          </div>

          {/* Selected document info */}
          {selectedDocument && (
            <div className="mt-4 p-3 bg-secondary/50 rounded-md">
              <div className="flex items-center gap-4 text-sm">
                <span>
                  <strong>Type:</strong> {selectedDocument.docType.toUpperCase()}
                </span>
                {selectedDocument.pageCount && (
                  <span>
                    <strong>Pages:</strong> {selectedDocument.pageCount}
                  </span>
                )}
                <span>
                  <strong>Status:</strong>{' '}
                  <span
                    className={`font-medium ${
                      selectedDocument.status === 'analyzed'
                        ? 'text-green-600'
                        : selectedDocument.status === 'failed'
                        ? 'text-red-600'
                        : 'text-yellow-600'
                    }`}
                  >
                    {selectedDocument.status.charAt(0).toUpperCase() +
                      selectedDocument.status.slice(1)}
                  </span>
                </span>
              </div>
            </div>
          )}

          {/* Error message */}
          {analysisError && (
            <div className="mt-4 flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-md text-sm">
              <AlertTriangle className="h-4 w-4" />
              {analysisError}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Analysis Progress */}
      {isAnalyzing && (
        <Card className="mb-6 border-primary">
          <CardContent className="py-8">
            <div className="flex flex-col items-center justify-center">
              <Loader2 className="h-12 w-12 text-primary animate-spin mb-4" />
              <h3 className="text-lg font-medium mb-2">Analysis in Progress</h3>
              <p className="text-muted-foreground text-center mb-4">
                Analyzing document against compliance frameworks...
              </p>
              {analysisRun && (
                <div className="w-full max-w-xs">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span>Progress</span>
                    <span>{analysisRun.progress}%</span>
                  </div>
                  <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all duration-300"
                      style={{ width: `${analysisRun.progress}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* No document selected state */}
      {!selectedDocumentId && !isLoadingDocuments && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <FileText className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">Select a Document</h3>
            <p className="text-muted-foreground text-center max-w-md">
              Choose a document from the dropdown above to view existing analysis results or run a
              new analysis.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Loading state for analysis */}
      {selectedDocumentId && isLoadingAnalysis && !isAnalyzing && (
        <div className="space-y-4">
          <Card className="animate-pulse">
            <CardHeader>
              <div className="h-6 bg-muted rounded w-48" />
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-20 bg-muted rounded" />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Analysis Results */}
      {selectedDocumentId && !isLoadingAnalysis && !isAnalyzing && (
        <>
          {findings.length > 0 ? (
            <div className="space-y-6">
              {/* Summary Statistics */}
              <FindingsSummary bySeverity={bySeverity} total={findings.length} />

              {/* Findings List with Filtering */}
              <div>
                <h2 className="text-xl font-semibold mb-4">Findings</h2>
                <FindingsList findings={findings} />
              </div>
            </div>
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16">
                <AlertTriangle className="h-16 w-16 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No Analysis Results</h3>
                <p className="text-muted-foreground text-center max-w-md mb-4">
                  This document hasn't been analyzed yet, or no findings were detected. Click "Run
                  Analysis" to analyze this document.
                </p>
                <Button onClick={handleRunAnalysis} disabled={isAnalyzing}>
                  <Play className="h-4 w-4 mr-2" />
                  Run Analysis
                </Button>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
