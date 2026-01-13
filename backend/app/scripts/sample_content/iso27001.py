"""ISO 27001 certification sample content."""

ISO27001_CONTENT = [
    # Page 1 - Certificate
    {
        "section_header": "ISO 27001:2022 Certificate",
        "page_number": 1,
        "content": """CERTIFICATE OF REGISTRATION

This is to certify that the Information Security Management System of:

{VENDOR}

has been assessed and found to conform to the requirements of:

ISO/IEC 27001:2022
Information Security, Cybersecurity and Privacy Protection - Information Security Management Systems - Requirements

Scope of Registration:
The provision and management of cloud-based software services, including data processing, storage, and transmission services, along with associated infrastructure and support operations.

Certificate Number: IS-2024-{VENDOR}-001
Original Registration Date: March 15, 2022
Current Certificate Valid From: March 15, 2024
Current Certificate Valid Until: March 14, 2027

This certificate remains valid subject to satisfactory surveillance audits and is subject to the satisfactory completion of periodic surveillance activities.""",
    },
    # Page 2 - Scope Statement
    {
        "section_header": "Scope of the ISMS",
        "page_number": 2,
        "content": """{VENDOR}'s Information Security Management System (ISMS) covers the following scope:

Organizational Scope:
The ISMS applies to all departments, business units, and personnel involved in the delivery of cloud-based services to customers. This includes Engineering, Operations, Customer Support, Security, and Corporate functions located at headquarters and remote offices.

Technical Scope:
- Cloud infrastructure and platform services
- Customer data processing and storage systems
- Internal corporate systems and networks
- Development and staging environments
- Third-party service integrations

Geographic Scope:
- Primary data centers in North America and Europe
- Corporate offices in San Francisco, New York, London, and Singapore
- Remote employee locations worldwide

Exclusions:
The following are excluded from the ISMS scope:
- Marketing and sales support systems not processing customer data
- Physical security of customer premises
- Customer-managed application code and configurations""",
    },
    # Page 3 - Context of the Organization
    {
        "section_header": "Context of the Organization",
        "page_number": 3,
        "content": """{VENDOR} operates in a highly competitive cloud services market where information security is a critical differentiator and customer requirement. The organization has identified the following interested parties and their security requirements:

Customers:
- Require secure processing and storage of business-critical data
- Need compliance with industry regulations (GDPR, HIPAA, PCI-DSS)
- Expect transparency through audit reports and certifications

Regulators:
- Data protection authorities require lawful processing
- Industry regulators mandate specific security controls
- Government agencies require certain data handling practices

Employees:
- Need secure access to work systems
- Require protection of personal information
- Expect secure working environment

Partners and Suppliers:
- Require secure integration interfaces
- Need assurance of data protection in shared processes
- Expect mutual security commitments

External Factors:
- Evolving cyber threat landscape
- Regulatory changes across jurisdictions
- Technological advancements in security controls
- Industry best practice developments""",
    },
    # Page 4 - Leadership and Commitment
    {
        "section_header": "Leadership and Commitment",
        "page_number": 4,
        "content": """{VENDOR}'s leadership demonstrates commitment to information security through the following:

Information Security Policy:
The CEO has approved an Information Security Policy that establishes the organization's commitment to protecting information assets and complying with applicable requirements. The policy is reviewed annually and updated as needed.

ISMS Objectives:
Leadership has established measurable security objectives including:
- Achieve and maintain industry certifications (SOC 2, ISO 27001, PCI-DSS)
- Maintain zero material security breaches affecting customer data
- Complete security awareness training for 100% of employees
- Resolve critical vulnerabilities within 24 hours
- Maintain 99.99% availability for security systems

Resource Allocation:
Adequate resources are allocated to the ISMS including:
- Dedicated security team with appropriate expertise
- Budget for security tools and technologies
- Investment in employee training and awareness
- External expertise for specialized assessments

Integration with Business Processes:
Information security requirements are integrated into:
- Product development lifecycle
- Vendor selection and management
- Employee onboarding and offboarding
- Incident management and response
- Business continuity planning""",
    },
    # Page 5 - Risk Assessment
    {
        "section_header": "Risk Assessment and Treatment",
        "page_number": 5,
        "content": """{VENDOR} maintains a formal information security risk management process aligned with ISO 27005:

Risk Assessment Methodology:
Risks are identified through analysis of:
- Asset inventory and classification
- Threat intelligence and vulnerability data
- Business impact analysis
- Compliance requirements
- Incident history and trends

Risk Analysis:
Each identified risk is analyzed based on:
- Likelihood of occurrence (1-5 scale)
- Potential impact (1-5 scale)
- Risk score = Likelihood x Impact
- Risk classification: Low (1-6), Medium (7-14), High (15-25)

Risk Treatment Options:
- Modify: Implement controls to reduce risk
- Accept: Accept risk when within tolerance
- Avoid: Eliminate the risk source
- Share: Transfer risk through insurance or contracts

Current Risk Register Summary:
- Total risks identified: 156
- High risks: 8 (all with treatment plans)
- Medium risks: 47 (62% treated, 38% accepted)
- Low risks: 101 (accepted with monitoring)

Key Risks Requiring Attention:
1. Advanced persistent threat (APT) attacks on cloud infrastructure
2. Supply chain compromise through third-party vendors
3. Insider threat from privileged users
4. Ransomware attacks on backup systems
5. Data exfiltration through authorized channels""",
    },
    # Page 6 - Statement of Applicability
    {
        "section_header": "Statement of Applicability",
        "page_number": 6,
        "content": """Statement of Applicability (SoA) Summary

{VENDOR} has assessed all 93 controls from ISO 27001:2022 Annex A:

Controls Implemented: 89 (95.7%)
Controls Not Applicable: 4 (4.3%)

Organizational Controls (Clause A.5): 37/37 implemented
- Information security policies and procedures
- Mobile device and teleworking policies
- Asset management and classification

People Controls (Clause A.6): 8/8 implemented
- Screening and terms of employment
- Security awareness and training
- Disciplinary process

Physical Controls (Clause A.7): 12/14 implemented
- Secure areas and equipment
- Clear desk and screen policies
- Not applicable: visitor management (cloud-only operations)
- Not applicable: physical entry controls to third-party premises

Technological Controls (Clause A.8): 32/34 implemented
- User access management
- Cryptographic controls
- Network security
- Not applicable: equipment siting (co-location provider responsible)
- Not applicable: power cables separation (co-location provider responsible)

Implementation Status:
All applicable controls have been implemented and are operating effectively. The SoA is reviewed annually and updated when controls are added or modified.""",
    },
    # Page 7 - Security Controls Implementation
    {
        "section_header": "Security Controls Implementation",
        "page_number": 7,
        "content": """Key Security Controls Implemented by {VENDOR}:

Access Control (A.5.15-A.5.18):
- Identity and access management system with MFA
- Role-based access control (RBAC)
- Privileged access management (PAM)
- Quarterly access reviews
- Automated provisioning/deprovisioning

Cryptography (A.8.24):
- AES-256 encryption for data at rest
- TLS 1.3 for data in transit
- Hardware Security Modules (HSM) for key management
- Encryption key rotation every 12 months
- Customer-managed encryption keys (BYOK) option

Network Security (A.8.20-A.8.22):
- Network segmentation with VLANs
- Next-generation firewalls with IPS
- Web Application Firewall (WAF)
- DDoS protection services
- Zero Trust Network Access (ZTNA)

Endpoint Security:
- Endpoint Detection and Response (EDR)
- Mobile Device Management (MDM)
- Patch management automation
- Application whitelisting on servers

Vulnerability Management (A.8.8):
- Weekly automated vulnerability scans
- Annual penetration testing
- Continuous dependency scanning
- Vulnerability SLAs: Critical 24hrs, High 7 days, Medium 30 days""",
    },
    # Page 8 - Operations Security
    {
        "section_header": "Operations Security",
        "page_number": 8,
        "content": """{VENDOR} implements operational security controls to ensure secure and reliable service delivery:

Change Management (A.8.32):
All changes to production systems follow a formal change management process:
- Change request with business justification
- Risk assessment and rollback plan
- Approval by Change Advisory Board
- Testing in non-production environment
- Scheduled deployment with monitoring
- Post-implementation review

Capacity Management (A.8.6):
System capacity is monitored and planned to ensure adequate resources:
- Real-time capacity monitoring
- Automated scaling based on demand
- Monthly capacity reviews
- Annual capacity planning

Separation of Development, Test, and Production (A.8.31):
Environments are strictly separated:
- Separate infrastructure for each environment
- No customer data in non-production environments
- Access controls specific to each environment
- Automated deployment pipelines

Malware Protection (A.8.7):
Multiple layers of malware protection:
- Endpoint antivirus with real-time scanning
- Email filtering and sandboxing
- Web proxy with content inspection
- Container image scanning

Logging and Monitoring (A.8.15-A.8.17):
Comprehensive logging and monitoring:
- Centralized log management (SIEM)
- 24/7 Security Operations Center
- Automated alert correlation
- 12-month log retention""",
    },
    # Page 9 - Incident Management
    {
        "section_header": "Information Security Incident Management",
        "page_number": 9,
        "content": """{VENDOR} maintains a comprehensive incident management program aligned with A.5.24-A.5.27:

Incident Response Plan:
The incident response plan defines:
- Incident classification criteria
- Roles and responsibilities
- Communication procedures
- Evidence preservation requirements
- Reporting obligations

Incident Classification:
- Critical: Confirmed breach of customer data, major service outage
- High: Attempted breach, significant security event, partial outage
- Medium: Security policy violation, minor vulnerability exploitation
- Low: Failed attack attempt, policy warning

Response Procedures:
1. Detection and initial assessment
2. Containment and evidence preservation
3. Investigation and root cause analysis
4. Eradication and recovery
5. Post-incident review and lessons learned

Incident Metrics (Last 12 Months):
- Total incidents: 127
- Critical: 0
- High: 3 (all resolved, no customer impact)
- Medium: 24
- Low: 100
- Average time to detect: 15 minutes
- Average time to contain: 45 minutes
- Average time to resolve: 4.2 hours

Reporting:
Security incidents affecting customers are reported within 72 hours as required by GDPR and contractual obligations. Regulatory authorities are notified as required by applicable laws.""",
    },
    # Page 10 - Business Continuity
    {
        "section_header": "Business Continuity",
        "page_number": 10,
        "content": """{VENDOR}'s business continuity management system ensures service availability during disruptions:

Business Impact Analysis:
Critical business processes have been identified and recovery requirements established:
- Customer-facing services: RTO 4 hours, RPO 1 hour
- Internal operations: RTO 24 hours, RPO 4 hours
- Administrative systems: RTO 72 hours, RPO 24 hours

Business Continuity Plans:
Plans address various scenarios:
- Data center failure (automatic failover to secondary region)
- Network disruption (redundant connectivity paths)
- Cyber attack (isolation and recovery procedures)
- Natural disaster (geographic distribution)
- Pandemic (remote work capability)

Disaster Recovery:
Technical recovery capabilities include:
- Active-active deployment across availability zones
- Automated failover for critical services
- Daily backups with geographic replication
- Tested recovery procedures

Testing Program:
- Quarterly tabletop exercises
- Semi-annual technical failover tests
- Annual full DR test with customer notification
- Documented test results and improvement actions

Recent Test Results:
- Q3 2024 DR test: All critical services recovered within RTO
- Identified improvement: Database recovery script optimization needed
- Action taken: Scripts updated and re-tested successfully""",
    },
    # Page 11 - Supplier Management
    {
        "section_header": "Supplier and Third-Party Management",
        "page_number": 11,
        "content": """{VENDOR} manages information security in supplier relationships per A.5.19-A.5.23:

Supplier Security Policy:
All suppliers with access to information assets must:
- Complete security questionnaire
- Provide relevant certifications (SOC 2, ISO 27001)
- Accept contractual security requirements
- Submit to periodic security assessments

Supplier Risk Assessment:
Suppliers are classified by risk:
- Critical: Process customer data or have system access
- High: Access internal data or networks
- Medium: Support services without data access
- Low: No access to systems or data

Supplier Assessment Schedule:
- Critical suppliers: Annual assessment, quarterly review
- High suppliers: Annual assessment
- Medium/Low suppliers: Assessment at onboarding, periodic questionnaire

Current Supplier Status:
- Total suppliers in scope: 47
- Critical suppliers: 8 (all with current SOC 2/ISO 27001)
- High suppliers: 15 (13 with current certifications)
- Suppliers requiring updated documentation: 2

Contractual Requirements:
Standard supplier agreements include:
- Data protection and confidentiality
- Security incident notification
- Audit and assessment rights
- Subcontractor approval requirements
- Termination and data return provisions""",
    },
    # Page 12 - Compliance
    {
        "section_header": "Compliance and Regulatory Requirements",
        "page_number": 12,
        "content": """{VENDOR} identifies and complies with applicable legal, regulatory, and contractual requirements:

Regulatory Framework:
The following regulations apply to {VENDOR}'s operations:
- General Data Protection Regulation (GDPR) - EU data processing
- California Consumer Privacy Act (CCPA) - California residents
- Health Insurance Portability and Accountability Act (HIPAA) - Healthcare customers
- Payment Card Industry Data Security Standard (PCI-DSS) - Payment processing
- Various data localization requirements

Compliance Controls:
- Privacy impact assessments for new processing activities
- Data processing agreements with customers
- Sub-processor management and disclosure
- Data subject rights request procedures
- Records of processing activities

Certifications and Attestations:
- ISO 27001:2022 - Information Security Management
- ISO 27017:2015 - Cloud Security
- ISO 27018:2019 - PII Protection in Public Clouds
- SOC 2 Type II - Security, Availability, Confidentiality
- PCI DSS Level 1 Service Provider

Compliance Monitoring:
- Regulatory change monitoring service
- Quarterly compliance reviews
- Annual compliance assessments
- External audit support

Findings and Improvements:
- No material compliance gaps identified
- Minor improvement: Documentation updates for GDPR Article 30
- Ongoing: Preparation for anticipated AI regulation requirements""",
    },
    # Page 13 - Performance Evaluation
    {
        "section_header": "Performance Evaluation and Improvement",
        "page_number": 13,
        "content": """{VENDOR} monitors, measures, analyzes, and evaluates ISMS performance per Clause 9:

Key Performance Indicators:
Security metrics are tracked and reported:
- Vulnerability remediation time (Target: Critical <24hrs, achieved 98%)
- Security awareness training completion (Target: 100%, achieved 99.2%)
- Access review completion rate (Target: 100%, achieved 100%)
- Incident response time (Target: <1hr, achieved 45min average)
- Patch compliance (Target: 95%, achieved 97%)

Internal Audit Program:
- Annual audit of all ISMS processes
- Qualified internal audit team
- Findings tracked to resolution
- Last audit: 8 findings, all resolved

Management Review:
Quarterly management reviews address:
- Audit and assessment results
- Security metrics and trends
- Risk register changes
- Resource adequacy
- Improvement opportunities

Continual Improvement:
ISMS improvements implemented in 2024:
- Enhanced threat intelligence integration
- Automated compliance monitoring
- Improved incident response playbooks
- Extended security awareness program
- Zero Trust architecture advancement

Improvement Pipeline:
- AI-powered threat detection enhancement
- Extended detection and response (XDR) implementation
- Supply chain security automation
- Privacy-enhancing technologies adoption""",
    },
    # Page 14 - Audit Findings
    {
        "section_header": "Certification Audit Findings",
        "page_number": 14,
        "content": """Summary of findings from the most recent certification audit:

Stage 1 Audit (Documentation Review):
- Conducted: January 2024
- Findings: 0 Major, 2 Minor, 3 Opportunities for Improvement
- Minor 1: Risk assessment procedure documentation needs update (Resolved)
- Minor 2: Supplier assessment template incomplete (Resolved)
- OFI 1: Consider expanding threat intelligence sources (Implemented)
- OFI 2: Enhance security metrics dashboard (In progress)
- OFI 3: Develop additional incident response playbooks (Completed)

Stage 2 Audit (Implementation):
- Conducted: February 2024
- Findings: 0 Major, 1 Minor, 5 Opportunities for Improvement
- Minor 1: Evidence of security awareness training for 3 new hires not available (Resolved - training completed)
- OFI 1: Implement automated compliance monitoring (In progress)
- OFI 2: Enhance backup testing procedures (Implemented)
- OFI 3: Consider additional network segmentation (Under evaluation)
- OFI 4: Improve change management metrics (Implemented)
- OFI 5: Enhance supplier assessment frequency (Implemented)

Overall Assessment:
The ISMS is effectively implemented and maintained. No major non-conformities were identified. Minor findings were promptly addressed. {VENDOR} demonstrates commitment to continual improvement of its information security management system.

Recommendation:
Certificate renewal recommended subject to continued conformity to ISO 27001:2022 requirements.""",
    },
]
