import { useState, useRef, useEffect } from 'react';
import { Download, FileSpreadsheet, FileText, ChevronDown, Loader2 } from 'lucide-react';
import { apiClient, getApiErrorMessage } from '@/lib/api';
import { useToast } from '@/components/ui/toast';
import { cn } from '@/lib/utils';

type ExportType = 'vendors' | 'findings' | 'remediation';
type ExportFormat = 'csv' | 'xlsx' | 'pdf';

interface ExportMenuProps {
  type: ExportType;
  filters?: Record<string, string>;
  disabled?: boolean;
}

interface FormatOption {
  format: ExportFormat;
  label: string;
  icon: React.ElementType;
}

/**
 * Available export formats per type.
 * - vendors: CSV, Excel
 * - findings: CSV, Excel, PDF
 * - remediation: CSV, Excel
 */
const FORMAT_OPTIONS: Record<ExportType, FormatOption[]> = {
  vendors: [
    { format: 'csv', label: 'CSV', icon: FileText },
    { format: 'xlsx', label: 'Excel', icon: FileSpreadsheet },
  ],
  findings: [
    { format: 'csv', label: 'CSV', icon: FileText },
    { format: 'xlsx', label: 'Excel', icon: FileSpreadsheet },
    { format: 'pdf', label: 'PDF', icon: FileText },
  ],
  remediation: [
    { format: 'csv', label: 'CSV', icon: FileText },
    { format: 'xlsx', label: 'Excel', icon: FileSpreadsheet },
  ],
};

/**
 * API endpoint paths per export type.
 */
const EXPORT_ENDPOINTS: Record<ExportType, string> = {
  vendors: '/export/vendors',
  findings: '/export/findings',
  remediation: '/export/remediation',
};

/**
 * File extensions per format.
 */
const FILE_EXTENSIONS: Record<ExportFormat, string> = {
  csv: 'csv',
  xlsx: 'xlsx',
  pdf: 'pdf',
};

/**
 * MIME types per format for blob handling.
 */
const MIME_TYPES: Record<ExportFormat, string> = {
  csv: 'text/csv',
  xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  pdf: 'application/pdf',
};

/**
 * ExportMenu - Reusable dropdown button for exporting data in various formats.
 * Supports vendors, findings, and remediation exports with format options.
 */
export function ExportMenu({ type, filters, disabled = false }: ExportMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingFormat, setLoadingFormat] = useState<ExportFormat | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { addToast } = useToast();

  const options = FORMAT_OPTIONS[type];
  const endpoint = EXPORT_ENDPOINTS[type];

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Close dropdown on escape key
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen]);

  /**
   * Handle export request for the selected format.
   * Makes API call, handles blob response, and triggers browser download.
   */
  async function handleExport(format: ExportFormat) {
    setIsLoading(true);
    setLoadingFormat(format);
    setIsOpen(false);

    try {
      // Build query params
      const params = new URLSearchParams({ format });
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value) {
            params.append(key, value);
          }
        });
      }

      // Make API request with blob response type
      const response = await apiClient.get(`${endpoint}?${params.toString()}`, {
        responseType: 'blob',
      });

      // Extract filename from Content-Disposition header or generate default
      const contentDisposition = response.headers['content-disposition'];
      let filename = `${type}_export_${new Date().toISOString().split('T')[0]}.${FILE_EXTENSIONS[format]}`;

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }

      // Create blob with correct MIME type
      const blob = new Blob([response.data], { type: MIME_TYPES[format] });

      // Create download link and trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      // Cleanup
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);

      addToast({
        type: 'success',
        title: 'Export Complete',
        description: `${type.charAt(0).toUpperCase() + type.slice(1)} exported as ${format.toUpperCase()}`,
      });
    } catch (error) {
      const errorMessage = getApiErrorMessage(error);
      addToast({
        type: 'error',
        title: 'Export Failed',
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
      setLoadingFormat(null);
    }
  }

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      {/* Main Export Button */}
      <button
        type="button"
        onClick={() => !disabled && !isLoading && setIsOpen(!isOpen)}
        disabled={disabled || isLoading}
        className={cn(
          'inline-flex items-center gap-2 px-4 py-2 rounded-lg',
          'border border-white/10 bg-black/30 backdrop-blur-sm',
          'text-sm font-medium text-white/90',
          'transition-all duration-200',
          'hover:bg-white/10 hover:border-primary/50 hover:shadow-[0_0_15px_rgba(0,242,255,0.15)]',
          'focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2 focus:ring-offset-black',
          'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-black/30 disabled:hover:border-white/10 disabled:hover:shadow-none'
        )}
        aria-expanded={isOpen}
        aria-haspopup="menu"
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin text-primary" />
        ) : (
          <Download className="h-4 w-4 text-primary" />
        )}
        <span>Export</span>
        <ChevronDown
          className={cn(
            'h-4 w-4 text-white/60 transition-transform duration-200',
            isOpen && 'rotate-180'
          )}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          role="menu"
          className={cn(
            'absolute right-0 mt-2 w-44 z-50',
            'rounded-lg border border-white/10 bg-black/90 backdrop-blur-md',
            'shadow-lg shadow-black/50',
            'py-1',
            'animate-in fade-in-0 zoom-in-95 duration-150'
          )}
        >
          <div className="px-3 py-2 border-b border-white/10">
            <p className="text-xs font-medium text-white/50 uppercase tracking-wider">
              Export Format
            </p>
          </div>
          {options.map((option) => {
            const Icon = option.icon;
            const isOptionLoading = loadingFormat === option.format;

            return (
              <button
                key={option.format}
                type="button"
                role="menuitem"
                onClick={() => handleExport(option.format)}
                disabled={isLoading}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2 text-left',
                  'text-sm text-white/80',
                  'transition-colors duration-150',
                  'hover:bg-white/10 hover:text-white',
                  'focus:outline-none focus:bg-white/10',
                  'disabled:opacity-50 disabled:cursor-not-allowed'
                )}
              >
                {isOptionLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                ) : (
                  <Icon className="h-4 w-4 text-primary/70" />
                )}
                <span>{option.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
