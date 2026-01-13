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
  ChevronRight,
  Target,
  TrendingUp
} from 'lucide-react';
import { Button } from '@/components/ui';

const stats = [
  { value: '97%', label: 'Time Savings', description: '15 min vs 6-8 hours' },
  { value: '12', label: 'Frameworks', description: 'SOC 2, NIST, ISO, SIG, DORA' },
  { value: '25', label: 'Vendor Categories', description: 'DoorDash-style TPRM taxonomy' },
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
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-background/60 backdrop-blur-xl border-b border-white/5 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center gap-2 group cursor-pointer">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/20 blur-md rounded-full group-hover:bg-primary/40 transition-all duration-300" />
                <Shield className="relative h-8 w-8 text-primary" />
              </div>
              <span className="text-xl font-bold tracking-tight">VendorAuditAI</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#problem" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Problem</a>
              <a href="#solution" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Solution</a>
              <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Features</a>
              <Link to="/competition" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Market Analysis</Link>
              <a href="#demo" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Demo</a>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/login">
                <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">Sign In</Button>
              </Link>
              <Link to="/register">
                <Button size="sm" className="neon-border shadow-lg shadow-primary/20">Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-40 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Background Glow */}
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-primary/10 blur-[120px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-medium uppercase tracking-wider mb-8 animate-fade-in-up">
            <Zap className="h-3 w-3" />
            AI-Powered Third-Party Risk Management
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tighter text-white max-w-5xl mx-auto mb-8 animate-fade-in-up delay-100">
            Vendor Assessments in{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent relative inline-block">
              Minutes
              <svg className="absolute w-full h-3 -bottom-1 left-0 text-primary opacity-50" viewBox="0 0 100 10" preserveAspectRatio="none">
                <path d="M0 5 Q 50 10 100 5" stroke="currentColor" strokeWidth="2" fill="none" />
              </svg>
            </span>
            , Not Hours
          </h1>

          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-12 animate-fade-in-up delay-200">
            Transform SOC 2, SIG, HECVAT, and security report reviews from 6-8 hours to under 15 minutes.
            AI-powered analysis with <span className="text-white font-medium">auditor-grade accuracy</span>.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 animate-fade-in-up delay-300">
            <Link to="/register">
              <Button size="lg" className="h-14 px-10 text-lg neon-border shadow-[0_0_30px_rgba(0,242,255,0.2)] hover:shadow-[0_0_50px_rgba(0,242,255,0.4)] transition-all duration-300">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <a href="#demo">
              <Button variant="outline" size="lg" className="h-14 px-10 text-lg border-white/10 hover:bg-white/5 backdrop-blur-sm">
                Watch Demo
              </Button>
            </a>
          </div>

          {/* Stats */}
          <div className="mt-24 grid grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto animate-fade-in-up delay-300">
            {stats.map((stat) => (
              <div key={stat.label} className="glass-card p-6 rounded-2xl group hover:bg-white/5 transition-colors">
                <div className="text-4xl sm:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-white to-white/60 font-mono tracking-tight mb-2 group-hover:text-primary transition-colors">{stat.value}</div>
                <div className="text-sm font-semibold text-white/90 uppercase tracking-wide mb-1">{stat.label}</div>
                <div className="text-xs text-muted-foreground">{stat.description}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section id="problem" className="py-24 px-4 sm:px-6 lg:px-8 bg-black/40 border-y border-white/5 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
              The Third-Party Risk Crisis
            </h2>
            <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto">
              Security teams are overwhelmed. Legacy GRC tools cost <span className="text-white">$100K-$500K/year</span> and still require massive manual effort.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {problems.map((problem) => (
              <div key={problem.title} className="glass-card p-8 rounded-2xl hover:bg-white/5 transition-all duration-300 group">
                <div className="flex items-center justify-center h-14 w-14 rounded-xl bg-destructive/10 text-destructive mb-8 group-hover:scale-110 transition-transform duration-300">
                  <problem.icon className="h-7 w-7" />
                </div>
                <h3 className="text-xl font-bold text-white mb-4">{problem.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{problem.description}</p>
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
            <div className="glass-panel rounded-2xl p-8 lg:p-10">
              <h3 className="text-xl font-bold text-white mb-8 flex items-center gap-3">
                <BarChart3 className="h-5 w-5 text-primary" />
                Legacy GRC vs VendorAuditAI
              </h3>
              <div className="space-y-1">
                <div className="grid grid-cols-3 gap-4 pb-4 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  <div>Feature</div>
                  <div>Legacy Tools</div>
                  <div className="text-primary">VendorAuditAI</div>
                </div>
                {comparisonData.map((row) => (
                  <div key={row.feature} className="grid grid-cols-3 gap-4 py-4 px-4 rounded-lg hover:bg-white/5 transition-colors border-b border-white/5 last:border-0 items-center">
                    <div className="text-sm font-medium text-white">{row.feature}</div>
                    <div className="text-sm text-muted-foreground font-mono">{row.legacy}</div>
                    <div className="text-sm font-bold text-primary font-mono bg-primary/10 inline-block px-2 py-1 rounded w-fit">{row.vendorAudit}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Market Position CTA */}
            <div className="glass-panel rounded-2xl p-8 lg:p-10 bg-gradient-to-br from-primary/5 to-blue-500/5 border border-primary/20">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="h-10 w-10 rounded-xl bg-primary/20 flex items-center justify-center">
                      <Target className="h-5 w-5 text-primary" />
                    </div>
                    <h3 className="text-xl font-bold text-white">$8.6B Market Opportunity</h3>
                  </div>
                  <p className="text-muted-foreground mb-4">
                    See how VendorAuditAI compares against 24 competitors including Drata, Vanta, SecurityScorecard, and OneTrust.
                    Interactive charts, threat tier analysis, and strategic roadmap.
                  </p>
                  <div className="flex flex-wrap items-center gap-4 text-sm">
                    <div className="flex items-center gap-2 text-green-400">
                      <TrendingUp className="h-4 w-4" />
                      <span>15-17% CAGR</span>
                    </div>
                    <div className="flex items-center gap-2 text-yellow-400">
                      <Building2 className="h-4 w-4" />
                      <span>24 Competitors Analyzed</span>
                    </div>
                    <div className="flex items-center gap-2 text-primary">
                      <CheckCircle2 className="h-4 w-4" />
                      <span>91% Market Untapped</span>
                    </div>
                  </div>
                </div>
                <Link to="/competition">
                  <Button size="lg" className="neon-border whitespace-nowrap">
                    View Market Analysis
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
              Enterprise-Grade Capabilities
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Everything you need to manage third-party risk at scale
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => (
              <div key={feature.title} className="glass-card p-8 rounded-2xl hover:border-primary/30 transition-all duration-300 group h-full">
                <div className="flex items-center justify-center h-12 w-12 rounded-xl bg-primary/10 text-primary mb-6 group-hover:scale-110 transition-transform">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3 group-hover:text-primary transition-colors">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section id="demo" className="py-20 px-4 sm:px-6 lg:px-8 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
              See It In Action
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Try VendorAuditAI yourself with our live demo environment
            </p>
          </div>

          <div className="glass-panel rounded-2xl p-8 lg:p-12 relative overflow-hidden">
            {/* Ambient Background */}
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-secondary/10 blur-[100px] rounded-full pointer-events-none" />

            <div className="grid lg:grid-cols-2 gap-12 items-center relative z-10">
              <div>
                <h3 className="text-2xl font-bold text-foreground mb-4 flex items-center gap-2">
                  <Zap className="h-6 w-6 text-primary" />
                  Live Demo Access
                </h3>
                <p className="text-muted-foreground mb-8 text-lg">
                  Explore the full platform with sample vendor data. Upload your own documents,
                  run AI analysis, and query your portfolio.
                </p>

                <div className="bg-black/40 rounded-xl p-6 mb-8 border border-white/10 font-mono text-sm">
                  <div className="text-xs text-muted-foreground mb-4 uppercase tracking-wider">Demo Credentials</div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between group">
                      <span className="text-gray-400">Email:</span>
                      <code className="bg-primary/10 text-primary px-3 py-1 rounded border border-primary/20">newdemo@vendorauditai.com</code>
                    </div>
                    <div className="flex items-center justify-between group">
                      <span className="text-gray-400">Password:</span>
                      <code className="bg-primary/10 text-primary px-3 py-1 rounded border border-primary/20">Demo12345</code>
                    </div>
                  </div>
                </div>

                <Link to="/login">
                  <Button size="lg" className="w-full sm:w-auto neon-border">
                    Access Live Demo
                    <ChevronRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
              </div>

              <div className="space-y-4">
                <div className="glass-card hover:bg-white/5 rounded-xl p-6 group transition-colors">
                  <div className="flex items-center gap-4 mb-3">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center border border-primary/20 group-hover:border-primary/50 transition-colors">
                      <Building2 className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <div className="font-semibold text-white">Vendor Management</div>
                      <div className="text-xs text-primary/80 font-mono">Add and track vendors</div>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground pl-14">
                    Create vendor profiles, assign risk tiers, and monitor compliance status across your portfolio.
                  </div>
                </div>

                <div className="glass-card hover:bg-white/5 rounded-xl p-6 group transition-colors">
                  <div className="flex items-center gap-4 mb-3">
                    <div className="h-10 w-10 rounded-lg bg-secondary/10 flex items-center justify-center border border-secondary/20 group-hover:border-secondary/50 transition-colors">
                      <FileSearch className="h-5 w-5 text-secondary" />
                    </div>
                    <div>
                      <div className="font-semibold text-white">Document Analysis</div>
                      <div className="text-xs text-secondary/80 font-mono">AI-powered review</div>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground pl-14">
                    Upload SOC 2, SIG, HECVAT reports and get instant AI analysis with findings and recommendations.
                  </div>
                </div>

                <div className="glass-card hover:bg-white/5 rounded-xl p-6 group transition-colors">
                  <div className="flex items-center gap-4 mb-3">
                    <div className="h-10 w-10 rounded-lg bg-green-500/10 flex items-center justify-center border border-green-500/20 group-hover:border-green-500/50 transition-colors">
                      <BarChart3 className="h-5 w-5 text-green-500" />
                    </div>
                    <div>
                      <div className="font-semibold text-white">Risk Dashboard</div>
                      <div className="text-xs text-green-400/80 font-mono">Real-time visibility</div>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground pl-14">
                    Monitor vendor risk scores, track findings by severity, and prioritize remediation efforts.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-primary/5 z-0" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-[400px] bg-primary/20 blur-[100px] rounded-full pointer-events-none opacity-30" />

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-3xl sm:text-4xl font-bold text-white neon-text mb-6">
            Ready to Transform Your Vendor Risk Program?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-10">
            Join security teams who've cut vendor assessment time by 90% while improving coverage.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/register">
              <Button size="lg" className="text-base px-8 h-12 shadow-[0_0_20px_rgba(0,242,255,0.3)] hover:shadow-[0_0_30px_rgba(0,242,255,0.5)] transition-all duration-300">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <a href="mailto:contact@vendorauditai.com">
              <Button size="lg" variant="outline" className="text-base px-8 h-12 border-primary/30 text-primary hover:bg-primary/10">
                Contact Sales
              </Button>
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 border-t border-white/5 bg-black/20 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-primary" />
              <span className="text-lg font-bold tracking-tight text-white">VendorAuditAI</span>
            </div>
            <div className="flex items-center gap-8 text-sm font-medium text-muted-foreground">
              <a href="#" className="hover:text-primary transition-colors">Privacy</a>
              <a href="#" className="hover:text-primary transition-colors">Terms</a>
              <a href="#" className="hover:text-primary transition-colors">Security</a>
              <a href="mailto:contact@vendorauditai.com" className="hover:text-primary transition-colors">Contact</a>
            </div>
            <div className="text-sm text-muted-foreground opacity-60">
              © 2026 VendorAuditAI. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
