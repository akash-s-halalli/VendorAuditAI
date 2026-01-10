import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from './Dashboard';

// Mock the api module
vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(),
  },
  apiClient: {
    get: vi.fn(),
  },
  getApiErrorMessage: vi.fn((error) => {
    if (error instanceof Error) return error.message;
    return 'An error occurred';
  }),
}));

// Import the mocked module
import apiClient from '@/lib/api';

const mockApiClient = apiClient as { get: ReturnType<typeof vi.fn> };

// Helper to create a fresh QueryClient for each test
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
    },
  });
}

// Wrapper component with QueryClientProvider
function renderWithQueryClient(ui: React.ReactElement) {
  const testQueryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={testQueryClient}>{ui}</QueryClientProvider>
  );
}

const mockDashboardStats = {
  totalVendors: 15,
  totalDocuments: 42,
  pendingAnalysis: 5,
  completedAnalysis: 37,
  criticalFindings: 3,
  highFindings: 8,
  mediumFindings: 12,
  lowFindings: 25,
};

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the dashboard title and description', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: mockDashboardStats });

    renderWithQueryClient(<Dashboard />);

    expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
    expect(screen.getByText(/overview of your vendor security posture/i)).toBeInTheDocument();
  });

  it('shows loading skeleton while fetching data', () => {
    // Return a promise that never resolves to keep loading state
    mockApiClient.get.mockReturnValueOnce(new Promise(() => {}));

    renderWithQueryClient(<Dashboard />);

    // Should show loading skeleton (multiple animated cards)
    const cards = document.querySelectorAll('.animate-pulse');
    expect(cards.length).toBeGreaterThan(0);
  });

  it('displays stats cards with correct data when loaded', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: mockDashboardStats });

    renderWithQueryClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Total Vendors')).toBeInTheDocument();
    });

    // Check stat values
    expect(screen.getByText('15')).toBeInTheDocument(); // totalVendors
    expect(screen.getByText('42')).toBeInTheDocument(); // totalDocuments
    expect(screen.getByText('5')).toBeInTheDocument(); // pendingAnalysis
    expect(screen.getByText('37')).toBeInTheDocument(); // completedAnalysis
  });

  it('displays stat card descriptions', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: mockDashboardStats });

    renderWithQueryClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Active vendors being monitored')).toBeInTheDocument();
    });

    expect(screen.getByText('Security reports uploaded')).toBeInTheDocument();
    expect(screen.getByText('Documents awaiting review')).toBeInTheDocument();
    expect(screen.getByText('Analyses completed')).toBeInTheDocument();
  });

  it('displays findings by severity section', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: mockDashboardStats });

    renderWithQueryClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Open Findings by Severity')).toBeInTheDocument();
    });

    // Check severity badges
    expect(screen.getByText('Critical')).toBeInTheDocument();
    expect(screen.getByText('High')).toBeInTheDocument();
    expect(screen.getByText('Medium')).toBeInTheDocument();
    expect(screen.getByText('Low')).toBeInTheDocument();
  });

  it('displays recent activity section', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: mockDashboardStats });

    renderWithQueryClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Recent Activity')).toBeInTheDocument();
    });

    expect(screen.getByText('Analysis completed')).toBeInTheDocument();
    expect(screen.getByText('Document uploaded')).toBeInTheDocument();
    expect(screen.getByText('Critical finding detected')).toBeInTheDocument();
  });

  it('displays quick actions section', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: mockDashboardStats });

    renderWithQueryClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    });

    expect(screen.getByText('Upload Document')).toBeInTheDocument();
    expect(screen.getByText('Add Vendor')).toBeInTheDocument();
    expect(screen.getByText('Ask a Question')).toBeInTheDocument();
  });

  it('shows error state when API call fails', async () => {
    const errorMessage = 'Network error';
    mockApiClient.get.mockRejectedValueOnce(new Error(errorMessage));

    renderWithQueryClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load dashboard')).toBeInTheDocument();
    });
  });

  it('calls the correct API endpoint', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: mockDashboardStats });

    renderWithQueryClient(<Dashboard />);

    await waitFor(() => {
      expect(mockApiClient.get).toHaveBeenCalledWith('/dashboard/stats');
    });
  });

  it('handles empty stats gracefully', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        totalVendors: 0,
        totalDocuments: 0,
        pendingAnalysis: 0,
        completedAnalysis: 0,
        criticalFindings: 0,
        highFindings: 0,
        mediumFindings: 0,
        lowFindings: 0,
      },
    });

    renderWithQueryClient(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Total Vendors')).toBeInTheDocument();
    });

    // All values should show 0
    const zeros = screen.getAllByText('0');
    expect(zeros.length).toBeGreaterThan(0);
  });
});
