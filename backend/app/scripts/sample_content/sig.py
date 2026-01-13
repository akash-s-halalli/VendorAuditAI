"""SIG (Standardized Information Gathering) questionnaire sample content."""

SIG_CONTENT = [
    # Page 1 - Introduction
    {
        "section_header": "SIG Questionnaire Response - Introduction",
        "page_number": 1,
        "content": """STANDARDIZED INFORMATION GATHERING (SIG) QUESTIONNAIRE
Version: SIG Core 2024
Respondent: {VENDOR}
Date Completed: October 15, 2024

Company Information:
- Company Name: {VENDOR}
- Industry: Technology / Cloud Services
- Number of Employees: 500-1000
- Annual Revenue: $50M - $100M
- Geographic Locations: United States, European Union, Asia Pacific
- Primary Services: Cloud-based software platform and data processing services

Contact Information:
- Security Contact: Chief Information Security Officer
- Privacy Contact: Data Protection Officer
- Compliance Contact: VP of Compliance

Certifications and Attestations:
- SOC 2 Type II (Current)
- ISO 27001:2022 (Current)
- ISO 27017 (Current)
- ISO 27018 (Current)
- PCI DSS Level 1 (Current)
- CSA STAR Level 2 (Current)

This questionnaire response covers {VENDOR}'s standard cloud service offerings and associated security, privacy, and compliance controls.""",
    },
    # Page 2 - A. Enterprise Risk Management
    {
        "section_header": "A. Enterprise Risk Management",
        "page_number": 2,
        "content": """A.1 Risk Management Program

A.1.1 Does your organization have a formal risk management program?
Response: YES

{VENDOR} maintains a comprehensive Enterprise Risk Management (ERM) program aligned with ISO 31000 and COSO frameworks. The program includes:
- Board-level risk oversight committee
- Dedicated risk management function
- Formal risk assessment methodology
- Risk appetite and tolerance statements
- Regular risk reporting to leadership

A.1.2 How frequently are risk assessments performed?
Response: Quarterly comprehensive assessments, continuous monitoring

Risk assessment activities include:
- Annual enterprise-wide risk assessment
- Quarterly business unit risk reviews
- Monthly security risk reviews
- Continuous automated vulnerability assessments
- Ad-hoc assessments for significant changes

A.1.3 Are risk assessment results documented and tracked?
Response: YES

All risk assessments are documented in our GRC platform with:
- Risk identification and categorization
- Likelihood and impact ratings
- Risk treatment decisions
- Control mapping
- Remediation tracking
- Risk owner assignment

A.1.4 How does your organization prioritize risk treatment?
Response: Risk scoring methodology based on business impact

Risks are prioritized using a quantitative scoring model considering:
- Financial impact potential
- Operational disruption severity
- Regulatory compliance implications
- Reputational damage potential
- Customer impact assessment""",
    },
    # Page 3 - B. Security Policy
    {
        "section_header": "B. Security Policy",
        "page_number": 3,
        "content": """B.1 Information Security Policies

B.1.1 Does your organization have documented information security policies?
Response: YES

{VENDOR} maintains a comprehensive policy framework including:
- Information Security Policy (Board approved)
- Acceptable Use Policy
- Access Control Policy
- Data Classification Policy
- Encryption Policy
- Incident Response Policy
- Business Continuity Policy
- Third-Party Risk Management Policy
- Privacy Policy

B.1.2 How often are security policies reviewed and updated?
Response: Annually, or more frequently as needed

Policy review process:
- Annual scheduled review of all policies
- Triggered reviews for regulatory changes
- Updates following significant incidents
- Stakeholder input collection
- Legal and compliance review
- Executive approval process

B.1.3 How are policies communicated to employees?
Response: Multiple channels with acknowledgment tracking

Policy communication methods:
- New hire orientation training
- Policy management portal (intranet)
- Annual policy acknowledgment campaign
- Regular security awareness communications
- Manager cascade communications
- Policy change notifications

B.1.4 What are the consequences for policy violations?
Response: Progressive discipline up to termination

Enforcement measures include:
- Documented verbal warning
- Written warning with corrective action plan
- Suspension pending investigation
- Termination for serious violations
- Legal action for criminal activity""",
    },
    # Page 4 - C. Organizational Security
    {
        "section_header": "C. Organizational Security",
        "page_number": 4,
        "content": """C.1 Security Organization

C.1.1 Does your organization have a dedicated security function?
Response: YES

{VENDOR}'s security organization includes:
- Chief Information Security Officer (CISO) reporting to CEO
- Security Operations team (24/7 SOC)
- Security Engineering team
- GRC and Compliance team
- Security Architecture team
- Application Security team

C.1.2 What is the security team headcount?
Response: 25+ dedicated security professionals

Team breakdown:
- Security Leadership: 3
- Security Operations: 8
- Security Engineering: 6
- GRC/Compliance: 4
- Application Security: 4
- Security Architecture: 2

C.2 Human Resources Security

C.2.1 Are background checks performed on employees?
Response: YES - All employees and contractors

Background verification includes:
- Criminal history check (7 years)
- Employment verification
- Education verification
- Professional reference checks
- Credit check for financial roles
- Enhanced checks for privileged access roles

C.2.2 Is security awareness training mandatory?
Response: YES - Annual with role-based modules

Training program includes:
- New hire security orientation (within 30 days)
- Annual security awareness refresher
- Phishing simulation exercises (monthly)
- Role-specific training (developers, admins, executives)
- Compliance-specific modules (HIPAA, PCI, GDPR)
- Training completion tracking (99.2% completion rate)""",
    },
    # Page 5 - D. Asset and Data Management
    {
        "section_header": "D. Asset and Data Management",
        "page_number": 5,
        "content": """D.1 Asset Management

D.1.1 Does your organization maintain an inventory of information assets?
Response: YES

Asset inventory includes:
- Hardware assets (servers, workstations, network devices)
- Software assets (applications, licenses)
- Data assets (databases, file stores)
- Cloud assets (virtual machines, containers, services)
- Third-party services and integrations

D.1.2 How is the asset inventory maintained?
Response: Automated discovery with manual validation

Asset management processes:
- Automated discovery scanning (weekly)
- Configuration Management Database (CMDB)
- Change management integration
- Annual physical inventory verification
- Asset lifecycle tracking
- Decommissioning procedures

D.2 Data Classification

D.2.1 Does your organization have a data classification scheme?
Response: YES

Classification levels:
- PUBLIC: Information approved for public disclosure
- INTERNAL: Internal business information
- CONFIDENTIAL: Sensitive business or customer data
- RESTRICTED: Highly sensitive data requiring special handling

D.2.2 How is customer data classified and handled?
Response: CONFIDENTIAL by default, RESTRICTED for sensitive data

Customer data handling:
- Classified as CONFIDENTIAL minimum
- Encryption required at rest and in transit
- Access restricted to authorized personnel
- Audit logging of all access
- Retention per contract and regulation
- Secure deletion upon termination""",
    },
    # Page 6 - E. Access Control
    {
        "section_header": "E. Access Control",
        "page_number": 6,
        "content": """E.1 Identity and Access Management

E.1.1 How is user access provisioned and managed?
Response: Automated IAM system with approval workflows

Access provisioning process:
- Request submitted through ticketing system
- Manager approval required
- Security review for privileged access
- Automated provisioning based on role templates
- Just-in-time access for elevated privileges
- Access granted per least privilege principle

E.1.2 What authentication mechanisms are used?
Response: Multi-factor authentication required

Authentication controls:
- Username and password (14+ character minimum)
- Multi-factor authentication (mandatory for all users)
- SSO integration via SAML 2.0/OIDC
- Passwordless authentication options available
- Certificate-based authentication for systems
- Hardware tokens for high-privilege accounts

E.1.3 How frequently are access reviews performed?
Response: Quarterly for all users

Access review process:
- Automated access certification campaigns
- Manager review of direct reports
- Application owner review of access
- Privileged access review (monthly)
- SOD (Segregation of Duties) violation review
- Exception documentation and approval

E.1.4 What is the process for access termination?
Response: Automated within 24 hours of termination

Termination process:
- HR triggers termination in identity system
- Automated account disable within 4 hours
- Access review within 24 hours
- Equipment recovery initiated
- Access fully revoked within 24 hours
- Audit trail maintained""",
    },
    # Page 7 - F. Cryptography
    {
        "section_header": "F. Cryptography",
        "page_number": 7,
        "content": """F.1 Encryption Standards

F.1.1 How is data encrypted at rest?
Response: AES-256 encryption with HSM key management

Data at rest encryption:
- Database encryption: TDE with AES-256
- File storage encryption: AES-256
- Backup encryption: AES-256
- Key management: HSM-backed key management service
- Key rotation: Annual automatic rotation
- Customer-managed keys: BYOK option available

F.1.2 How is data encrypted in transit?
Response: TLS 1.2 minimum, TLS 1.3 preferred

Data in transit encryption:
- External communications: TLS 1.3 preferred, TLS 1.2 minimum
- Internal communications: mTLS between services
- API communications: TLS 1.2+
- Database connections: Encrypted connections required
- VPN: AES-256 with IKEv2
- Certificate management: Automated with 90-day renewal

F.1.3 What cryptographic algorithms are prohibited?
Response: Weak/deprecated algorithms explicitly prohibited

Prohibited algorithms:
- MD5, SHA-1 for security purposes
- DES, 3DES, RC4
- TLS 1.0, TLS 1.1, SSL
- RSA < 2048 bits
- ECC < 256 bits

F.1.4 How are encryption keys managed?
Response: Centralized KMS with HSM backing

Key management:
- Hardware Security Modules (HSM) for master keys
- Centralized key management service
- Automated key rotation
- Key backup and recovery procedures
- Separation of key administrators
- Audit logging of key operations""",
    },
    # Page 8 - G. Operations Security
    {
        "section_header": "G. Operations Security",
        "page_number": 8,
        "content": """G.1 Change Management

G.1.1 Does your organization have a formal change management process?
Response: YES

Change management process:
- Change request documentation
- Impact and risk assessment
- Testing requirements
- Approval workflow (CAB for significant changes)
- Deployment procedures
- Rollback planning
- Post-implementation review

G.1.2 What types of changes require approval?
Response: All production changes require approval

Change categories:
- Standard: Pre-approved, low risk
- Normal: CAB approval required
- Emergency: Expedited approval with post-review
- All changes logged and auditable

G.2 Vulnerability Management

G.2.1 How often are vulnerability assessments performed?
Response: Continuous scanning with periodic comprehensive assessments

Vulnerability assessment schedule:
- Automated scanning: Continuous
- Network vulnerability scans: Weekly
- Web application scans: Weekly
- Penetration testing: Annual external, semi-annual internal
- Code scanning: Every build
- Container image scanning: Every deployment

G.2.2 What are the remediation SLAs for vulnerabilities?
Response: Based on severity and exploitability

Remediation timeframes:
- Critical: 24 hours (immediate if actively exploited)
- High: 7 days
- Medium: 30 days
- Low: 90 days
- Exceptions require documented risk acceptance""",
    },
    # Page 9 - H. Incident Response
    {
        "section_header": "H. Incident Response",
        "page_number": 9,
        "content": """H.1 Incident Management

H.1.1 Does your organization have a documented incident response plan?
Response: YES

Incident response program includes:
- Incident Response Policy and Procedures
- Incident classification criteria
- Communication templates and escalation paths
- Evidence preservation guidelines
- Forensic investigation procedures
- Customer notification procedures
- Post-incident review process

H.1.2 How are incidents detected?
Response: Multiple detection mechanisms

Detection capabilities:
- 24/7 Security Operations Center (SOC)
- SIEM with correlation rules
- Endpoint Detection and Response (EDR)
- Network intrusion detection (IDS/IPS)
- Cloud security monitoring
- User behavior analytics
- Threat intelligence integration
- Automated alerting with defined thresholds

H.1.3 What are the incident response timeframes?
Response: Defined by severity classification

Response timeframes:
- Critical: Response within 15 minutes, containment within 1 hour
- High: Response within 1 hour, containment within 4 hours
- Medium: Response within 4 hours, containment within 24 hours
- Low: Response within 24 hours, resolution within 5 days

H.1.4 How and when are customers notified of security incidents?
Response: Within 72 hours for incidents affecting customer data

Notification process:
- Impact assessment completed
- Legal and compliance review
- Customer notification within 72 hours
- Regular status updates until resolution
- Final incident report provided
- Regulatory notifications as required""",
    },
    # Page 10 - I. Business Continuity
    {
        "section_header": "I. Business Continuity",
        "page_number": 10,
        "content": """I.1 Business Continuity Management

I.1.1 Does your organization have a business continuity program?
Response: YES

Business continuity program includes:
- Business Impact Analysis (BIA)
- Business Continuity Plans (BCP)
- Disaster Recovery Plans (DRP)
- Crisis Communication Plan
- Emergency Response Procedures
- Testing and exercise program

I.1.2 What are the Recovery Time Objectives (RTO)?
Response: Tiered by service criticality

RTOs by tier:
- Tier 1 (Critical): 4 hours
- Tier 2 (High): 8 hours
- Tier 3 (Medium): 24 hours
- Tier 4 (Low): 72 hours

I.1.3 What are the Recovery Point Objectives (RPO)?
Response: Tiered by service criticality

RPOs by tier:
- Tier 1 (Critical): 1 hour
- Tier 2 (High): 4 hours
- Tier 3 (Medium): 24 hours
- Tier 4 (Low): 72 hours

I.1.4 How often is business continuity tested?
Response: Minimum annually, critical systems quarterly

Testing program:
- Tabletop exercises: Quarterly
- Technical recovery tests: Semi-annually
- Full DR failover test: Annually
- Communication plan test: Quarterly
- Third-party participation in annual test
- Test results documented and reviewed
- Improvement actions tracked to completion""",
    },
    # Page 11 - J. Third-Party Management
    {
        "section_header": "J. Third-Party Risk Management",
        "page_number": 11,
        "content": """J.1 Vendor Management

J.1.1 Does your organization have a third-party risk management program?
Response: YES

Third-party risk management includes:
- Vendor risk assessment framework
- Due diligence procedures
- Contractual security requirements
- Ongoing monitoring program
- Vendor performance management
- Exit and transition planning

J.1.2 How are vendors risk assessed?
Response: Risk-based tiered assessment

Assessment approach:
- Critical vendors: Comprehensive assessment, on-site review option
- High-risk vendors: Detailed questionnaire, certification review
- Medium-risk vendors: Standard questionnaire
- Low-risk vendors: Basic assessment

Assessment criteria:
- Data access and handling
- System integration level
- Business criticality
- Financial stability
- Geographic considerations
- Regulatory implications

J.1.3 What security requirements are included in contracts?
Response: Standard security addendum for all data-handling vendors

Contractual requirements:
- Data protection and confidentiality
- Security control requirements
- Incident notification obligations
- Audit and assessment rights
- Subcontractor management
- Insurance requirements
- Termination and data return

J.1.4 How often are vendors reassessed?
Response: Risk-based frequency

Reassessment schedule:
- Critical vendors: Annually + continuous monitoring
- High-risk vendors: Annually
- Medium-risk vendors: Every 2 years
- Low-risk vendors: Every 3 years
- Triggered reassessment for material changes or incidents""",
    },
    # Page 12 - K. Compliance
    {
        "section_header": "K. Compliance and Privacy",
        "page_number": 12,
        "content": """K.1 Regulatory Compliance

K.1.1 What regulations does your organization comply with?
Response: Multiple frameworks based on customer requirements

Compliance frameworks:
- SOC 2 Type II (Trust Services Criteria)
- ISO 27001:2022 (Information Security)
- ISO 27017 (Cloud Security)
- ISO 27018 (PII in Public Clouds)
- PCI DSS (Payment Card Industry)
- HIPAA (Healthcare - BAA available)
- GDPR (EU Data Protection)
- CCPA (California Privacy)
- Various data localization requirements

K.1.2 How does your organization monitor regulatory changes?
Response: Dedicated compliance monitoring program

Monitoring process:
- Regulatory intelligence service subscription
- Legal team monitoring
- Industry association participation
- Regular compliance reviews
- Impact assessments for new requirements
- Implementation tracking

K.2 Privacy

K.2.1 Does your organization have a privacy program?
Response: YES

Privacy program includes:
- Data Protection Officer appointed
- Privacy policies and procedures
- Privacy impact assessments
- Data subject rights procedures
- Privacy by design principles
- Records of processing activities
- Data breach notification procedures

K.2.2 How are data subject requests handled?
Response: Documented process with defined SLAs

DSR process:
- Request intake and verification
- Response within 30 days (GDPR/CCPA)
- Automated tools for data retrieval
- Secure delivery mechanisms
- Request logging and reporting
- Customer notification for their data subjects""",
    },
    # Page 13 - L. Additional Information
    {
        "section_header": "L. Additional Information",
        "page_number": 13,
        "content": """L.1 Recent Security Improvements

Recent enhancements to {VENDOR}'s security program:

Q4 2024:
- Implemented Zero Trust Network Architecture
- Deployed Extended Detection and Response (XDR)
- Enhanced privileged access management
- Expanded security awareness program

Q3 2024:
- Achieved ISO 27001:2022 recertification
- Implemented container security scanning
- Enhanced API security controls
- Deployed AI-powered threat detection

Q2 2024:
- Completed SOC 2 Type II audit
- Implemented data loss prevention (DLP)
- Enhanced backup encryption
- Expanded vendor assessment program

L.2 Security Incidents (Last 12 Months)

{VENDOR} has had no material security incidents affecting customer data in the past 12 months.

Minor incidents (no customer impact):
- 3 phishing attempts detected and blocked
- 2 vulnerability exploitation attempts blocked by WAF
- 1 insider policy violation (addressed through training)

L.3 Planned Improvements

Roadmap items:
- SASE (Secure Access Service Edge) implementation
- AI/ML security operations enhancement
- Privacy-enhancing technologies adoption
- Quantum-safe cryptography evaluation
- Extended supply chain security program

L.4 Contact Information

For additional security inquiries:
- Security Team: security@{VENDOR}.com
- Trust Center: trust.{VENDOR}.com
- Status Page: status.{VENDOR}.com""",
    },
]
