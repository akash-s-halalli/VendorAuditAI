import { Routes, Route } from 'react-router-dom';

function App() {
  return (
    <div className="min-h-screen bg-background font-sans antialiased">
      <Routes>
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
                    href="/dashboard"
                    className="rounded-md bg-primary px-3.5 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
                  >
                    Get Started
                  </a>
                  <a
                    href="/docs"
                    className="text-sm font-semibold leading-6 text-foreground"
                  >
                    Learn more <span aria-hidden="true">-&gt;</span>
                  </a>
                </div>
              </div>
            </main>
          }
        />
        <Route
          path="/dashboard"
          element={
            <div className="p-8">
              <h1 className="text-2xl font-bold">Dashboard</h1>
              <p className="text-muted-foreground">Coming soon...</p>
            </div>
          }
        />
      </Routes>
    </div>
  );
}

export default App;
