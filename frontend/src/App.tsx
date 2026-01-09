import { Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout, AuthLayout } from '@/components/layout';
import { Login, Register, Dashboard, Vendors, Documents, Query } from '@/pages';
import { useAuthStore } from '@/stores/authStore';

/**
 * Protected Route wrapper - redirects to login if not authenticated
 */
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

/**
 * Public Route wrapper - redirects to dashboard if already authenticated
 */
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <div className="min-h-screen bg-background font-sans antialiased">
      <Routes>
        {/* Public routes (auth) */}
        <Route
          element={
            <PublicRoute>
              <AuthLayout />
            </PublicRoute>
          }
        >
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>

        {/* Protected routes (app) */}
        <Route
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/vendors" element={<Vendors />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/query" element={<Query />} />
          <Route path="/analysis" element={<Dashboard />} />
          <Route path="/search" element={<Dashboard />} />
          <Route path="/settings" element={<Dashboard />} />
        </Route>

        {/* Landing page */}
        <Route
          path="/"
          element={
            <main className="flex min-h-screen flex-col items-center justify-center p-24">
              <div className="text-center">
                <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-6xl">
                  VendorAuditAI
                </h1>
                <p className="mt-6 text-lg leading-8 text-muted-foreground">
                  AI-Powered Vendor Security Report Analyzer
                </p>
                <p className="mt-2 text-sm text-muted-foreground">
                  Transform SOC 2, SIG, HECVAT reviews from hours to minutes
                </p>
                <div className="mt-10 flex items-center justify-center gap-x-6">
                  <a
                    href="/login"
                    className="rounded-md bg-primary px-3.5 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
                  >
                    Get Started
                  </a>
                  <a
                    href="/register"
                    className="text-sm font-semibold leading-6 text-foreground"
                  >
                    Create Account <span aria-hidden="true">-&gt;</span>
                  </a>
                </div>
              </div>
            </main>
          }
        />

        {/* Catch all - redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;
