import { Outlet } from 'react-router-dom';
import { Shield } from 'lucide-react';

export function AuthLayout() {
  return (
    <div className="min-h-screen flex">
      {/* Left side - branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-primary items-center justify-center p-12">
        <div className="max-w-md text-primary-foreground">
          <div className="flex items-center gap-3 mb-8">
            <Shield className="h-12 w-12" />
            <span className="text-3xl font-bold">VendorAuditAI</span>
          </div>
          <h1 className="text-4xl font-bold mb-4">
            AI-Powered Vendor Security Analysis
          </h1>
          <p className="text-lg opacity-90">
            Transform SOC 2, SIG, and HECVAT reviews from hours to minutes with
            intelligent document analysis and compliance gap detection.
          </p>
          <div className="mt-8 grid grid-cols-2 gap-4">
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-3xl font-bold">97%</div>
              <div className="text-sm opacity-80">Time Savings</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4">
              <div className="text-3xl font-bold">12</div>
              <div className="text-sm opacity-80">Frameworks</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - auth forms */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
