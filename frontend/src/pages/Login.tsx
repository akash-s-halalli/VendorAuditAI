import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, Input, Label } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { getApiErrorMessage } from '@/lib/api';

export function Login() {
  const navigate = useNavigate();
  const { login, validateMfa, isAuthenticated, isLoading, error, clearError } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    clearError();
  }, [clearError]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!email || !password) {
      setLocalError('Please enter your email and password');
      return;
    }

    try {
      const result = await login(email, password);
      if (result.mfaRequired && result.mfaToken) {
        setMfaToken(result.mfaToken);
      }
    } catch (err) {
      setLocalError(getApiErrorMessage(err));
    }
  };

  const handleMfaSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!mfaCode || mfaCode.length !== 6) {
      setLocalError('Please enter a valid 6-digit code');
      return;
    }

    try {
      await validateMfa(mfaToken!, mfaCode);
    } catch (err) {
      setLocalError(getApiErrorMessage(err));
    }
  };

  const displayError = localError || error;

  // MFA verification screen
  if (mfaToken) {
    return (
      <>
        <div className="flex items-center justify-center gap-2 mb-8 lg:hidden">
          <Shield className="h-8 w-8 text-primary" />
          <span className="text-2xl font-bold">VendorAuditAI</span>
        </div>

        <Card className="border-primary/20 bg-black/40 backdrop-blur-xl">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl">Two-Factor Authentication</CardTitle>
            <CardDescription>Enter the code from your authenticator app</CardDescription>
          </CardHeader>
          <form onSubmit={handleMfaSubmit}>
            <CardContent className="space-y-4">
              {displayError && (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
                  <AlertCircle className="h-4 w-4 flex-shrink-0" />
                  {displayError}
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="mfa-code">Verification Code</Label>
                <Input
                  id="mfa-code"
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  maxLength={6}
                  placeholder="000000"
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ''))}
                  className="text-center text-2xl tracking-widest"
                  autoFocus
                />
              </div>
              <Button
                type="submit"
                className="w-full h-12 text-lg font-medium"
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  'Verify'
                )}
              </Button>
            </CardContent>
          </form>
          <CardFooter className="flex flex-col gap-4">
            <button
              type="button"
              className="text-sm text-muted-foreground hover:text-primary"
              onClick={() => {
                setMfaToken(null);
                setMfaCode('');
                setLocalError(null);
              }}
            >
              Back to login
            </button>
          </CardFooter>
        </Card>
      </>
    );
  }

  // Login form
  return (
    <>
      <div className="flex items-center justify-center gap-2 mb-8 lg:hidden">
        <Shield className="h-8 w-8 text-primary" />
        <span className="text-2xl font-bold">VendorAuditAI</span>
      </div>

      <Card className="border-primary/20 bg-black/40 backdrop-blur-xl">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-2xl">Welcome Back</CardTitle>
          <CardDescription>Sign in to access your security dashboard</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {displayError && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-destructive/10 text-destructive text-sm">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                {displayError}
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                autoFocus
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>
            <Button
              type="submit"
              className="w-full h-12 text-lg font-medium neon-border group relative overflow-hidden"
              disabled={isLoading}
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <span className="relative z-10 flex items-center justify-center gap-2">
                  Sign In
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </span>
              )}
              <div className="absolute inset-0 bg-primary/20 blur-md group-hover:bg-primary/30 transition-all duration-300" />
            </Button>
          </CardContent>
        </form>
        <CardFooter className="flex flex-col gap-4">
          <p className="text-sm text-muted-foreground text-center">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary hover:underline font-medium">
              Create account
            </Link>
          </p>
        </CardFooter>
      </Card>
    </>
  );
}
