/**
 * API type definitions for VendorAuditAI frontend.
 */

// Common types
export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';
export type VendorTier = 'critical' | 'high' | 'medium' | 'low';
export type VendorStatus = 'active' | 'inactive' | 'onboarding' | 'offboarding';
export type DocumentType =
  | 'soc2'
  | 'sig_lite'
  | 'sig_core'
  | 'hecvat'
  | 'iso27001'
  | 'pentest'
  | 'questionnaire'
  | 'other';
export type DocumentStatus = 'uploaded' | 'processing' | 'parsed' | 'analyzed' | 'failed';
export type FindingType = 'gap' | 'exception' | 'weakness' | 'observation' | 'strength';
export type UserRole = 'admin' | 'analyst' | 'viewer';

// Pagination
export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    pages: number;
  };
}

// User
export interface User {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  organizationId: string;
  isActive: boolean;
  createdAt: string;
}

// Organization
export interface Organization {
  id: string;
  name: string;
  slug: string;
  subscriptionTier: string;
  createdAt: string;
}

// Vendor
export interface Vendor {
  id: string;
  name: string;
  description?: string;
  website?: string;
  tier: VendorTier;
  status: VendorStatus;
  criticalityScore?: number;
  dataClassification?: string;
  lastAssessed?: string;
  nextAssessmentDue?: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface CreateVendorRequest {
  name: string;
  description?: string;
  website?: string;
  tier?: VendorTier;
  criticalityScore?: number;
  dataClassification?: string;
  tags?: string[];
}

export interface UpdateVendorRequest {
  name?: string;
  description?: string;
  website?: string;
  tier?: VendorTier;
  status?: VendorStatus;
  criticalityScore?: number;
  dataClassification?: string;
  tags?: string[];
}

// Document
export interface Document {
  id: string;
  vendorId?: string;
  filename: string;
  originalFilename: string;
  docType: DocumentType;
  mimeType: string;
  fileSize: number;
  status: DocumentStatus;
  pageCount?: number;
  reportPeriodStart?: string;
  reportPeriodEnd?: string;
  auditorName?: string;
  opinionType?: string;
  createdAt: string;
  processedAt?: string;
}

// Analysis
export interface AnalysisRun {
  id: string;
  documentId: string;
  frameworkIds: string[];
  analysisType: string;
  status: string;
  progress: number;
  startedAt?: string;
  completedAt?: string;
  summary?: AnalysisSummary;
  createdAt: string;
}

export interface AnalysisSummary {
  totalFindings: number;
  bySeverity: Record<Severity, number>;
  byType: Record<FindingType, number>;
  controlsCovered: number;
  controlsWithGaps: number;
}

// Finding
export interface Finding {
  id: string;
  runId: string;
  documentId: string;
  controlId: string;
  controlName: string;
  framework: string;
  findingType: FindingType;
  severity: Severity;
  title: string;
  description: string;
  evidence?: string;
  recommendation?: string;
  pageReferences: number[];
  citations: Citation[];
  confidenceScore: number;
  status: string;
  createdAt: string;
}

export interface Citation {
  page: number;
  paragraph?: number;
  text: string;
}

// Framework
export interface Framework {
  id: string;
  name: string;
  version: string;
  fullName: string;
  description: string;
  controlCount: number;
}

// Query
export interface QueryRequest {
  query: string;
  filters?: {
    vendorIds?: string[];
    documentIds?: string[];
    frameworks?: string[];
    dateRange?: {
      from?: string;
      to?: string;
    };
  };
}

export interface QueryResponse {
  answer: string;
  sources: QuerySource[];
  relatedFindings: Finding[];
}

export interface QuerySource {
  documentId: string;
  documentName: string;
  page: number;
  text: string;
  confidence: number;
}

// Dashboard
export interface DashboardSummary {
  totalVendors: number;
  vendorsByTier: Record<VendorTier, number>;
  pendingAssessments: number;
  openFindings: Record<Severity, number>;
  recentActivity: ActivityItem[];
}

export interface ActivityItem {
  id: string;
  type: 'document_uploaded' | 'analysis_completed' | 'finding_resolved' | 'vendor_added';
  description: string;
  timestamp: string;
  userId: string;
}
