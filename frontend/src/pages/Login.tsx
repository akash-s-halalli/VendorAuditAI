import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, ArrowRight } from 'lucide-react';
import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';

export function Login() {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  return (
    <>
      {/* Mobile logo */}
      <div className="flex items-center justify-center gap-2 mb-8 lg:hidden">
        <Shield className="h-8 w-8 text-primary" />
        <span className="text-2xl font-bold">VendorAuditAI</span>
      </div>

      <Card className="border-primary/20 bg-black/40 backdrop-blur-xl">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-2xl">Welcome Back</CardTitle>
          <CardDescription>Sign in to access your security dashboard</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            onClick={login}
            className="w-full h-12 text-lg font-medium neon-border group relative overflow-hidden"
          >
            <span className="relative z-10 flex items-center justify-center gap-2">
              Sign In with Netlify
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </span>
            <div className="absolute inset-0 bg-primary/20 blur-md group-hover:bg-primary/30 transition-all duration-300" />
          </Button>
        </CardContent>
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
