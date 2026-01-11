import { Link } from 'react-router-dom';
import {
  Shield,
  FileSearch,
  BarChart3,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Building2,
  FileText,
  Zap,
  Lock,
  Globe,
  ArrowRight,
  ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui';

const stats = [
  { value: '97%', label: 'Accuracy Rate', description: 'Validated against auditors' },
  { value: '15min', label: 'Assessment Time', description: 'Down from 6-8 hours' },
  { value: '6+', label: 'Frameworks', description: 'NIST, ISO, SOC 2, CIS' },
  { value: '90%', label: 'Cost Reduction', description: 'vs. legacy GRC tools' },
];

const problems = [
  {
    icon: Clock,
    title: 'Manual Reviews Take Forever',
    description: 'Each vendor assessment takes 6-8 hours of analyst time. With 5,000+ vendors, security teams can never keep up.',
  },
  {
    icon: AlertTriangle,
    title: 'Third-Party Breaches',
    description: '60% of data breaches originate from third-party vendors. Poor visibility means undetected risks.',
  },
  {
    icon: FileText,
    title: 'Compliance Chaos',
    description: 'SOC 2, SIG, HECVAT, ISO 27001 - security teams drown in 500+ page reports with no way to compare.',
  },
];

const features = [
  {
    icon: FileSearch,
    title: 'AI Document Analysis',
    description: 'Upload any security report - SOC 2, SIG, HECVAT, penetration tests. Our AI extracts every control, policy, and attestation automatically.',
  },
  {
    icon: BarChart3,
    title: 'Multi-Framework Mapping',
    description: 'Automatically map findings to NIST 800-53, ISO 27001, SOC 2 TSC, CIS Controls, and more. No manual cross-referencing.',
  },
  {
    icon: Shield,
    title: 'Gap Detection',
    description: 'Identify missing controls, weak implementations, and compliance gaps with confidence scoring and page-specific citations.',
  },
  {
    icon: Zap,
    title: 'Natural Language Query',
    description: 'Ask questions in plain English: "Which vendors lack MFA?" or "Show all encryption findings." Search your entire portfolio instantly.',
  },
  {
    icon: Lock,
    title: 'Enterprise Security',
    description: 'Self-hosted deployment option, SSO/SAML, RBAC, encryption at rest and in transit. Your data never leaves your infrastructure.',
  },
  {
    icon: Globe,
    title: 'Portfolio Dashboard',
    description: 'Real-time visibility across all vendors. Track risk scores, monitor compliance status, and prioritize remediation.',
  },
];

const comparisonData = [
  { feature: 'Assessment Time', legacy: '6-8 hours', vendorAudit: '15 minutes' },
  { feature: 'Annual Cost', legacy: '$100K-$500K', vendorAudit: '90% less' },
  { feature: 'AI-Powered Analysis', legacy: 'Limited/None', vendorAudit: 'Native LLM + RAG' },
  { feature: 'Natural Language Query', legacy: 'No', vendorAudit: 'Yes' },
  { feature: 'Multi-Framework Mapping', legacy: 'Manual', vendorAudit: 'Automatic' },
  { feature: 'Confidence Scoring', legacy: 'No', vendorAudit: 'Yes, with citations' },
  { feature: 'Self-Hosted Option', legacy: 'Rare', vendorAudit: 'Full support' },
];

export function Landing() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Shield className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold">VendorAuditAI</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#problem" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Problem</a>
              <a href="#solution" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Solution</a>
              <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Features</a>
              <a href="#demo" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Demo</a>
            </div>
            <div className="flex items-center gap-3">
              <Link to="/login">
                <Button variant="ghost" size="sm">Sign In</Button>
              </Link>
              <Link to="/register">
                <Button size="sm">Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-8">
            <Zap className="h-4 w-4" />
            AI-Powered Third-Party Risk Management
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-foreground max-w-4xl mx-auto">
            Vendor Security Assessments in{' '}
            <span className="text-primary">Minutes, Not Hours</span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto">
            Transform SOC 2, SIG, HECVAT, and security report reviews from 6-8 hours to under 15 minutes.
            AI-powered analysis with auditor-grade accuracy.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register">
              <Button size="lg" className="text-base px-8">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <a href="#demo">
              <Button variant="outline" size="lg" className="text-base px-8">
                Watch Demo
              </Button>
            </a>
          </div>

          {/* Stats */}
          <div className="mt-20 grid grid-cols-2 lg:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-primary">{stat.value}</div>
                <div className="text-sm font-medium text-foreground mt-1">{stat.label}</div>
                <div className="text-xs text-muted-foreground">{stat.description}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section id="problem" className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
              The Third-Party Risk Crisis
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Security teams are overwhelmed. Legacy GRC tools cost $100K-$500K/year and still require massive manual effort.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {problems.map((problem) => (
              <div key={problem.title} className="bg-background rounded-xl p-8 shadow-sm border">
                <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-destructive/10 text-destructive mb-6">
                  <problem.icon className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">{problem.title}</h3>
                <p className="text-muted-foreground">{problem.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section id="solution" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
                AI That Thinks Like an Auditor
              </h2>
              <p className="mt-6 text-lg text-muted-foreground">
                VendorAuditAI uses advanced LLMs with Retrieval-Augmented Generation (RAG) to analyze security documents
                with the precision of a certified auditor - but in a fraction of the time.
              </p>

              <div className="mt-8 space-y-4">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <CheckCircle2 className="h-6 w-6 text-green-500" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">Upload Any Format</h4>
                    <p className="text-muted-foreground">PDF, DOCX, scanned documents - we handle them all</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <CheckCircle2 className="h-6 w-6 text-green-500" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">Automatic Framework Mapping</h4>
                    <p className="text-muted-foreground">Findings mapped to NIST, ISO, SOC 2, CIS Controls instantly</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <CheckCircle2 className="h-6 w-6 text-green-500" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">Auditor-Grade Citations</h4>
                    <p className="text-muted-foreground">Every finding includes page numbers and confidence scores</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <CheckCircle2 className="h-6 w-6 text-green-500" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">Query Your Portfolio</h4>
                    <p className="text-muted-foreground">Ask questions across all vendor documents in plain English</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Comparison Table */}
            <div className="bg-muted/30 rounded-2xl p-8 border">
              <h3 className="text-xl font-bold text-foreground mb-6">Legacy GRC vs VendorAuditAI</h3>
              <div className="space-y-4">
                {comparisonData.map((row) => (
                  <div key={row.feature} className="grid grid-cols-3 gap-4 py-3 border-b border-border last:border-0">
                    <div className="text-sm font-medium text-foreground">{row.feature}</div>
                    <div className="text-sm text-muted-foreground">{row.legacy}</div>
                    <div className="text-sm font-semibold text-primary">{row.vendorAudit}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
              Enterprise-Grade Capabilities
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Everything you need to manage third-party risk at scale
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => (
              <div key={feature.title} className="bg-background rounded-xl p-8 shadow-sm border hover:shadow-md transition-shadow">
                <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-primary/10 text-primary mb-6">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section id="demo" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
              See It In Action
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Try VendorAuditAI yourself with our live demo environment
            </p>
          </div>

          <div className="bg-gradient-to-br from-primary/5 to-primary/10 rounded-2xl p-8 lg:p-12 border">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <h3 className="text-2xl font-bold text-foreground mb-4">
                  Live Demo Access
                </h3>
                <p className="text-muted-foreground mb-6">
                  Explore the full platform with sample vendor data. Upload your own documents,
                  run AI analysis, and query your portfolio.
                </p>

                <div className="bg-background rounded-lg p-6 mb-6 border">
                  <div className="text-sm text-muted-foreground mb-2">Demo Credentials</div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Email:</span>
                      <code className="bg-muted px-2 py-1 rounded text-sm">demo@vendorauditai.com</code>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Password:</span>
                      <code className="bg-muted px-2 py-1 rounded text-sm">DemoPass123</code>
                    </div>
                  </div>
                </div>

                <Link to="/login">
                  <Button size="lg" className="w-full sm:w-auto">
                    Access Live Demo
                    <ChevronRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
              </div>

              <div className="space-y-4">
                <div className="bg-background rounded-lg p-6 border">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <Building2 className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <div className="font-semibold">Vendor Management</div>
                      <div className="text-sm text-muted-foreground">Add and track vendors</div>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Create vendor profiles, assign risk tiers, and monitor compliance status across your portfolio.
                  </div>
                </div>

                <div className="bg-background rounded-lg p-6 border">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <FileSearch className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <div className="font-semibold">Document Analysis</div>
                      <div className="text-sm text-muted-foreground">AI-powered review</div>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Upload SOC 2, SIG, HECVAT reports and get instant AI analysis with findings and recommendations.
                  </div>
                </div>

                <div className="bg-background rounded-lg p-6 border">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <BarChart3 className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <div className="font-semibold">Risk Dashboard</div>
                      <div className="text-sm text-muted-foreground">Real-time visibility</div>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Monitor vendor risk scores, track findings by severity, and prioritize remediation efforts.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold">
            Ready to Transform Your Vendor Risk Program?
          </h2>
          <p className="mt-6 text-lg opacity-90">
            Join security teams who've cut vendor assessment time by 90% while improving coverage.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register">
              <Button size="lg" variant="secondary" className="text-base px-8">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <a href="mailto:contact@vendorauditai.com">
              <Button size="lg" variant="outline" className="text-base px-8 border-primary-foreground/30 text-primary-foreground hover:bg-primary-foreground/10">
                Contact Sales
              </Button>
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 border-t">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-primary" />
              <span className="text-lg font-semibold">VendorAuditAI</span>
            </div>
            <div className="flex items-center gap-8 text-sm text-muted-foreground">
              <a href="#" className="hover:text-foreground transition-colors">Privacy</a>
              <a href="#" className="hover:text-foreground transition-colors">Terms</a>
              <a href="#" className="hover:text-foreground transition-colors">Security</a>
              <a href="mailto:contact@vendorauditai.com" className="hover:text-foreground transition-colors">Contact</a>
            </div>
            <div className="text-sm text-muted-foreground">
              2025 VendorAuditAI. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
