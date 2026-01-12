import { useState, useCallback, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Upload, Search, FileText, MoreVertical, CheckCircle, Clock, AlertCircle, Loader2, Download, Trash2 } from 'lucide-react';
import {
  Button,
  Input,
  Card,
  CardContent,
  Badge,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui';
import apiClient, { getApiErrorMessage } from '@/lib/api';
import type { DocumentStatus, DocumentType } from '@/types/api';

// Backend returns snake_case, so define the actual response type
interface BackendDocument {
  id: string;
  filename: string;
  file_size: number;
  mime_type: string;
  document_type: DocumentType;
  status: DocumentStatus;
  page_count?: number;
  created_at: string;
}

export function Documents() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<BackendDocument | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpenMenuId(null);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

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

      const response = await apiClient.post('/documents', formData);
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

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/documents/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setShowDeleteModal(false);
      setSelectedDocument(null);
    },
  });

  const documents: BackendDocument[] = documentsResponse?.data || [];

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
    // Validate by both MIME type and file extension for better security
    const validExtensions = ['.pdf', '.docx'];
    const validMimeTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const validFiles = files.filter((f) => {
      const ext = f.name.toLowerCase().slice(f.name.lastIndexOf('.'));
      return validMimeTypes.includes(f.type) && validExtensions.includes(ext);
    });

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

  const handleDownload = async (doc: BackendDocument) => {
    setOpenMenuId(null);
    try {
      const response = await apiClient.get(`/documents/${doc.id}/download`, {
        responseType: 'blob',
      });

      // Create download link
      const blob = new Blob([response.data], { type: doc.mime_type });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = doc.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      setUploadError(getApiErrorMessage(error));
    }
  };

  const openDeleteModal = (doc: BackendDocument) => {
    setSelectedDocument(doc);
    setShowDeleteModal(true);
    setOpenMenuId(null);
  };

  const handleDelete = () => {
    if (!selectedDocument) return;
    deleteMutation.mutate(selectedDocument.id);
  };

  const getStatusIcon = (status: DocumentStatus) => {
    switch (status) {
      case 'analyzed':
      case 'processed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'pending':
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
        <div>
          <input
            id="header-upload"
            type="file"
            className="hidden"
            accept=".pdf,.docx"
            multiple
            onChange={handleFileSelect}
          />
          <Button onClick={() => document.getElementById('header-upload')?.click()}>
            <Upload className="h-4 w-4 mr-2" />
            Upload Document
          </Button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <Dialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
        <DialogContent className="sm:max-w-[400px]">
          <DialogHeader>
            <DialogTitle>Delete Document</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete <strong>{selectedDocument?.filename}</strong>? This action cannot be undone and will remove all associated analysis data.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteModal(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>
              {deleteMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Delete Document
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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
        <div>
          <input
            id="dropzone-upload"
            type="file"
            className="hidden"
            accept=".pdf,.docx"
            multiple
            onChange={handleFileSelect}
          />
          <Button variant="outline" onClick={() => document.getElementById('dropzone-upload')?.click()}>
            Browse files
          </Button>
        </div>
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
            <Card key={doc.id} className="hover:shadow-sm transition-shadow">
              <CardContent className="p-4 flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded bg-primary/10">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium truncate">{doc.filename}</p>
                    {getStatusIcon(doc.status)}
                  </div>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <Badge variant="outline">{getDocTypeLabel(doc.document_type)}</Badge>
                    <span>{formatFileSize(doc.file_size)}</span>
                    {doc.page_count && <span>{doc.page_count} pages</span>}
                    <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="relative" ref={openMenuId === doc.id ? menuRef : null}>
                  <button
                    className="rounded-full p-2 hover:bg-accent"
                    onClick={(e) => {
                      e.stopPropagation();
                      setOpenMenuId(openMenuId === doc.id ? null : doc.id);
                    }}
                  >
                    <MoreVertical className="h-4 w-4" />
                  </button>
                  {openMenuId === doc.id && (
                    <div className="absolute right-0 top-full mt-1 w-40 rounded-md border bg-popover shadow-md z-50">
                      <button
                        className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-accent"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDownload(doc);
                        }}
                      >
                        <Download className="h-4 w-4" />
                        Download
                      </button>
                      <button
                        className="flex w-full items-center gap-2 px-3 py-2 text-sm text-destructive hover:bg-accent"
                        onClick={(e) => {
                          e.stopPropagation();
                          openDeleteModal(doc);
                        }}
                      >
                        <Trash2 className="h-4 w-4" />
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
