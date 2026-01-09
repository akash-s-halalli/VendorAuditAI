import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Upload, Search, FileText, MoreVertical, CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { Button, Input, Card, CardContent, Badge } from '@/components/ui';
import apiClient, { getApiErrorMessage } from '@/lib/api';
import type { Document, DocumentStatus, DocumentType } from '@/types/api';

export function Documents() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const { data: documentsResponse, isLoading } = useQuery({
    queryKey: ['documents', searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      params.append('limit', '50');

      const response = await apiClient.get(`/documents?${params}`);
      return response.data;
    },
  });

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setUploadError(null);
    },
    onError: (error) => {
      setUploadError(getApiErrorMessage(error));
    },
  });

  const documents: Document[] = documentsResponse?.data || [];

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    const validFiles = files.filter(
      (f) => f.type === 'application/pdf' || f.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    );

    validFiles.forEach((file) => {
      uploadMutation.mutate(file);
    });
  }, [uploadMutation]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    files.forEach((file) => {
      uploadMutation.mutate(file);
    });
    e.target.value = '';
  }, [uploadMutation]);

  const getStatusIcon = (status: DocumentStatus) => {
    switch (status) {
      case 'analyzed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'processing':
      case 'parsed':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'uploaded':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  const getDocTypeLabel = (docType: DocumentType) => {
    const labels: Record<DocumentType, string> = {
      soc2: 'SOC 2',
      sig_lite: 'SIG Lite',
      sig_core: 'SIG Core',
      hecvat: 'HECVAT',
      iso27001: 'ISO 27001',
      pentest: 'Pentest',
      questionnaire: 'Questionnaire',
      other: 'Other',
    };
    return labels[docType] || docType;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Documents</h1>
          <p className="text-muted-foreground">Upload and manage security reports</p>
        </div>
        <label>
          <input
            type="file"
            className="hidden"
            accept=".pdf,.docx"
            multiple
            onChange={handleFileSelect}
          />
          <Button as="span" className="cursor-pointer">
            <Upload className="h-4 w-4 mr-2" />
            Upload Document
          </Button>
        </label>
      </div>

      {/* Upload Zone */}
      <div
        className={`mb-6 border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging ? 'border-primary bg-primary/5' : 'border-border'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className={`h-10 w-10 mx-auto mb-4 ${isDragging ? 'text-primary' : 'text-muted-foreground'}`} />
        <p className="text-lg font-medium mb-1">
          {isDragging ? 'Drop files here' : 'Drag and drop files here'}
        </p>
        <p className="text-sm text-muted-foreground mb-4">
          Supports PDF and DOCX files (SOC 2, SIG, HECVAT, etc.)
        </p>
        <label>
          <input
            type="file"
            className="hidden"
            accept=".pdf,.docx"
            multiple
            onChange={handleFileSelect}
          />
          <Button variant="outline" as="span" className="cursor-pointer">
            Browse files
          </Button>
        </label>
      </div>

      {uploadError && (
        <div className="mb-6 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
          {uploadError}
        </div>
      )}

      {uploadMutation.isPending && (
        <div className="mb-6 flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Uploading...
        </div>
      )}

      {/* Search */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search documents..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Documents List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="h-10 w-10 bg-muted rounded"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-muted rounded w-1/3"></div>
                  <div className="h-3 bg-muted rounded w-1/4"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : documents.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No documents yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              Upload your first security report to get started.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {documents.map((doc) => (
            <Card key={doc.id} className="hover:shadow-sm transition-shadow cursor-pointer">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded bg-primary/10">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium truncate">{doc.originalFilename}</p>
                    {getStatusIcon(doc.status)}
                  </div>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <Badge variant="outline">{getDocTypeLabel(doc.docType)}</Badge>
                    <span>{formatFileSize(doc.fileSize)}</span>
                    {doc.pageCount && <span>{doc.pageCount} pages</span>}
                    <span>{new Date(doc.createdAt).toLocaleDateString()}</span>
                  </div>
                </div>
                <button className="rounded-full p-2 hover:bg-accent">
                  <MoreVertical className="h-4 w-4" />
                </button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
