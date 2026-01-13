"""SOC 2 Type II report sample content."""

SOC2_CONTENT = [
    # Page 1 - Executive Summary
    {
        "section_header": "Executive Summary",
        "page_number": 1,
        "content": """This SOC 2 Type II report presents the results of our examination of {VENDOR}'s system and the suitability of the design and operating effectiveness of controls for the period from January 1, 2024 through December 31, 2024. The examination was conducted in accordance with attestation standards established by the American Institute of Certified Public Accountants (AICPA).

{VENDOR} provides cloud-based services to customers requiring high availability, security, and compliance with industry standards. This report covers the Security, Availability, and Confidentiality trust service categories as defined in the AICPA Trust Services Criteria.

Our examination revealed that {VENDOR} has implemented controls that are suitably designed and operating effectively to meet the applicable trust services criteria throughout the examination period. However, we identified certain areas where control enhancements could further strengthen the organization's security posture.""",
    },
    # Page 2 - Management Assertion
    {
        "section_header": "Management's Assertion",
        "page_number": 2,
        "content": """{VENDOR} management is responsible for designing, implementing, and maintaining effective controls over its cloud services platform. Management asserts that the controls described in this report were suitably designed and operating effectively throughout the examination period.

Management's assertion is based on the criteria set forth in the AICPA's Trust Services Criteria. The controls described in this report are designed to provide reasonable assurance regarding the security, availability, and confidentiality of the system.

Key management responsibilities include: (1) Establishing and maintaining an effective control environment; (2) Performing ongoing risk assessments; (3) Implementing and operating control activities; (4) Maintaining information and communication systems; and (5) Performing monitoring activities.""",
    },
    # Page 3 - System Description
    {
        "section_header": "Description of the System",
        "page_number": 3,
        "content": """The {VENDOR} platform is a cloud-based infrastructure service that provides customers with secure, scalable, and highly available computing resources. The system includes the following components:

Infrastructure: The platform operates across multiple geographically distributed data centers with redundant power, cooling, and network connectivity. All data centers maintain Tier III+ certification and employ physical security controls including biometric access, 24/7 surveillance, and security personnel.

Network Architecture: The network infrastructure employs defense-in-depth principles with multiple layers of firewalls, intrusion detection/prevention systems, and network segmentation. All external communications are encrypted using TLS 1.3.

Application Layer: Customer applications run in isolated containers with resource limits and network policies. The platform supports automated scaling, load balancing, and health monitoring.

Data Storage: Customer data is stored on encrypted volumes using AES-256 encryption. Backups are performed daily and replicated to geographically separate regions.""",
    },
    # Page 4 - Control Environment
    {
        "section_header": "Control Environment",
        "page_number": 4,
        "content": """{VENDOR} has established a strong control environment that sets the tone for the organization's approach to internal controls. The control environment includes:

Governance Structure: The Board of Directors provides oversight of risk management and internal controls. An Audit Committee meets quarterly to review security metrics, audit findings, and remediation progress.

Management Philosophy: {VENDOR} management demonstrates commitment to security through regular security reviews, adequate resource allocation, and promotion of security awareness throughout the organization.

Organizational Structure: Clear lines of responsibility are established for security functions. The Chief Information Security Officer (CISO) reports directly to the CEO and has authority over all security-related decisions.

Human Resources: Comprehensive background checks are performed on all employees. Security awareness training is mandatory and conducted annually. Employees sign confidentiality agreements upon hire.""",
    },
    # Page 5 - Risk Assessment
    {
        "section_header": "Risk Assessment Process",
        "page_number": 5,
        "content": """{VENDOR} maintains a formal risk assessment process that identifies, analyzes, and manages risks to the achievement of its objectives. The risk assessment process includes:

Risk Identification: Risks are identified through multiple channels including vulnerability assessments, penetration testing, threat intelligence feeds, and input from business units. An annual comprehensive risk assessment is performed by an independent third party.

Risk Analysis: Identified risks are evaluated based on likelihood and potential impact. A risk scoring methodology assigns numerical values to enable prioritization and tracking over time.

Risk Response: For each identified risk, management determines an appropriate response: accept, mitigate, transfer, or avoid. Mitigation strategies are documented in risk treatment plans with assigned owners and target completion dates.

Continuous Monitoring: Key risk indicators are monitored continuously. Material changes to the risk profile are escalated to the Audit Committee for review.

Identified Gaps: During the assessment period, the following risks were identified requiring enhanced controls: (1) Third-party vendor management processes need strengthening; (2) Privileged access monitoring requires additional automation; (3) Disaster recovery testing should be conducted more frequently.""",
    },
    # Page 6 - Access Controls
    {
        "section_header": "Logical Access Controls",
        "page_number": 6,
        "content": """Access to {VENDOR}'s systems and data is restricted to authorized personnel through comprehensive logical access controls:

Authentication: Multi-factor authentication (MFA) is required for all system access. Password policies enforce minimum length of 14 characters, complexity requirements, and 90-day rotation. SSO integration is available for enterprise customers.

Authorization: Role-based access control (RBAC) limits user permissions to the minimum necessary for job functions. Access requests require manager approval and are reviewed quarterly. Privileged access requires additional approval from the security team.

User Provisioning: New user accounts are created through an automated provisioning system tied to HR records. Account creation requires documented approval. Temporary access for contractors expires automatically after 90 days.

Access Termination: User access is revoked within 24 hours of employment termination. An automated process disables accounts when employees are marked as terminated in the HR system. Access reviews are performed quarterly to identify stale accounts.

Monitoring: All authentication attempts are logged and monitored. Failed login attempts trigger account lockout after 5 failures. Security alerts are generated for anomalous access patterns.""",
    },
    # Page 7 - Change Management
    {
        "section_header": "Change Management",
        "page_number": 7,
        "content": """{VENDOR} maintains formal change management procedures to ensure changes to the system are authorized, tested, and documented:

Change Request Process: All changes require a formal change request documenting the business justification, technical details, rollback plan, and risk assessment. Changes are categorized as standard, normal, or emergency based on risk and urgency.

Change Approval: Standard changes follow a pre-approved process. Normal changes require approval from the Change Advisory Board (CAB) which meets weekly. Emergency changes require immediate approval from the on-call manager with retrospective CAB review.

Testing Requirements: Changes must be tested in a non-production environment before deployment. Test cases document expected outcomes and actual results. User acceptance testing is required for changes affecting customer-facing functionality.

Deployment: Production deployments follow automated CI/CD pipelines with quality gates. Blue-green deployment strategy enables rapid rollback. Deployments are scheduled during maintenance windows when possible.

Post-Implementation Review: All changes are reviewed within 5 business days of implementation. Metrics tracked include deployment success rate, rollback frequency, and incidents attributed to changes.""",
    },
    # Page 8 - Incident Response
    {
        "section_header": "Security Incident Response",
        "page_number": 8,
        "content": """{VENDOR} maintains a security incident response program to detect, respond to, and recover from security incidents:

Incident Detection: Security events are collected from multiple sources including network devices, servers, applications, and cloud services. A Security Information and Event Management (SIEM) system correlates events and generates alerts based on predefined rules and machine learning models.

Incident Classification: Incidents are classified by severity: Critical (immediate threat to operations), High (significant security impact), Medium (limited impact), and Low (minimal impact). Classification determines response time and escalation requirements.

Response Procedures: The incident response team follows documented playbooks for common incident types. Critical and high-severity incidents require immediate response and executive notification. A dedicated war room is established for major incidents.

Communication: Affected customers are notified within 72 hours of confirmed security incidents as required by contractual and regulatory obligations. Status updates are provided regularly until resolution.

Post-Incident Analysis: Root cause analysis is performed for all high and critical severity incidents. Lessons learned are documented and incorporated into improved controls. Incident metrics are reported to the Audit Committee quarterly.""",
    },
    # Page 9 - Data Protection
    {
        "section_header": "Data Protection and Privacy",
        "page_number": 9,
        "content": """{VENDOR} implements comprehensive data protection controls to ensure the confidentiality and integrity of customer data:

Data Classification: Data is classified into categories: Public, Internal, Confidential, and Restricted. Classification determines handling requirements, access controls, and retention periods. Customer data is classified as Confidential by default.

Encryption: All customer data is encrypted at rest using AES-256 encryption with keys managed through a dedicated key management service. Data in transit is encrypted using TLS 1.3. Customers can optionally manage their own encryption keys (BYOK).

Data Residency: Customer data is stored in the region selected at account creation. Cross-region data transfer requires explicit customer consent. Data residency controls comply with GDPR, CCPA, and other applicable regulations.

Data Retention: Customer data is retained for the duration of the service agreement plus 30 days for backup purposes. Data deletion requests are processed within 30 days. Cryptographic erasure is used to ensure deleted data is unrecoverable.

Privacy Controls: Access to customer data requires specific business justification and is logged. Customer support personnel use anonymized data when possible. Privacy impact assessments are conducted for new features involving personal data.""",
    },
    # Page 10 - Business Continuity
    {
        "section_header": "Business Continuity and Disaster Recovery",
        "page_number": 10,
        "content": """{VENDOR} maintains business continuity and disaster recovery capabilities to ensure service availability:

Backup Strategy: Full backups are performed daily with incremental backups every 4 hours. Backups are encrypted and stored in geographically separate regions. Backup integrity is verified through automated restoration testing weekly.

Redundancy: All critical systems are deployed in an active-active configuration across multiple availability zones. Automated failover occurs within 30 seconds for most components. No single point of failure exists in the architecture.

Recovery Objectives: Recovery Time Objective (RTO) is 4 hours for critical systems and 24 hours for non-critical systems. Recovery Point Objective (RPO) is 1 hour for critical data and 24 hours for non-critical data.

Testing: Disaster recovery testing is conducted semi-annually. Tests include full failover to secondary region, restoration from backup, and communication plan activation. Test results are documented and reviewed by management.

Improvement Areas: Recent DR testing identified areas for improvement: (1) Documentation of certain recovery procedures needs updating; (2) Cross-training of recovery team members should be expanded; (3) Recovery time for database systems exceeded RTO target by 15 minutes.""",
    },
    # Page 11 - Vendor Management
    {
        "section_header": "Third-Party Vendor Management",
        "page_number": 11,
        "content": """{VENDOR} relies on third-party vendors for certain infrastructure and services. A formal vendor management program ensures these relationships do not introduce unacceptable risk:

Vendor Selection: New vendors undergo a risk assessment before engagement. Assessment criteria include financial stability, security certifications, regulatory compliance, and references. High-risk vendors require approval from the security team.

Due Diligence: SOC 2 reports or equivalent certifications are required for vendors processing customer data. Vendor questionnaires assess security controls, incident response capabilities, and business continuity plans. On-site assessments are performed for critical vendors.

Contractual Requirements: Vendor contracts include security requirements, audit rights, incident notification obligations, and data protection terms. Service level agreements define availability, performance, and support requirements.

Ongoing Monitoring: Vendor performance is reviewed quarterly. Annual reassessment is performed for all vendors with access to customer data. Vendor risk ratings are updated based on assessment findings.

Current Findings: The vendor management program has the following areas requiring attention: (1) Two vendors have outdated SOC 2 reports; (2) Quarterly reviews were delayed for three vendors due to resource constraints; (3) Contract renewal for one high-risk vendor lacks updated security terms.""",
    },
    # Page 12 - Monitoring and Logging
    {
        "section_header": "Monitoring and Logging",
        "page_number": 12,
        "content": """{VENDOR} maintains comprehensive monitoring and logging capabilities to detect security events and support forensic investigations:

Log Collection: Logs are collected from all systems including servers, network devices, applications, databases, and cloud services. Log sources include authentication events, system changes, data access, administrative actions, and security alerts.

Log Protection: Logs are transmitted securely to a centralized log management platform. Log integrity is protected through cryptographic hashing. Logs are retained for 12 months online and 7 years in archive storage.

Security Monitoring: The Security Operations Center (SOC) operates 24/7/365 to monitor security alerts. Alert triage follows documented procedures with defined response times. Correlation rules detect multi-stage attacks and lateral movement.

Performance Monitoring: System health metrics are collected and visualized in real-time dashboards. Automated alerts notify operations teams of performance degradation. Capacity planning reports are generated monthly.

Audit Trail: All administrative actions are logged with user identity, timestamp, action performed, and outcome. Audit logs support compliance requirements and incident investigations. Log access is restricted to authorized personnel.""",
    },
    # Page 13 - Compliance
    {
        "section_header": "Compliance and Certifications",
        "page_number": 13,
        "content": """{VENDOR} maintains multiple compliance certifications and undergoes regular audits to demonstrate adherence to industry standards:

Current Certifications:
- SOC 2 Type II (Security, Availability, Confidentiality)
- ISO 27001:2022 Information Security Management
- ISO 27017 Cloud Security
- ISO 27018 Protection of PII in Public Clouds
- PCI DSS Level 1 Service Provider
- HIPAA (Business Associate Agreement available)
- FedRAMP Moderate (In Progress)

Audit Schedule: External audits are conducted annually for SOC 2 and ISO certifications. PCI DSS assessment is performed quarterly for scanning and annually for full audit. Internal audits are conducted semi-annually.

Regulatory Compliance: {VENDOR} monitors regulatory changes affecting its operations. A regulatory compliance team tracks requirements from GDPR, CCPA, HIPAA, and industry-specific regulations. Compliance documentation is maintained for customer due diligence requests.

Customer Audits: {VENDOR} supports customer audit requests through completion of security questionnaires, provision of compliance documentation, and virtual audit sessions. On-site audits are available for enterprise customers.""",
    },
    # Page 14 - Test Results Summary
    {
        "section_header": "Test Results and Exceptions",
        "page_number": 14,
        "content": """This section summarizes the test results from our examination of {VENDOR}'s controls during the audit period:

Testing Methodology: We performed inquiry, observation, and inspection procedures to evaluate the design of controls. We tested the operating effectiveness of controls by examining documentary evidence, re-performing control activities, and analyzing system-generated reports.

Summary of Results:
- Total controls tested: 127
- Controls operating effectively: 121 (95.3%)
- Controls with exceptions: 6 (4.7%)

Exceptions Identified:

Exception 1 (CC6.1): Three user accounts remained active more than 24 hours after employee termination due to a system integration issue. The accounts did not access any systems during this period. Remediated.

Exception 2 (CC6.2): Quarterly access reviews for two departments were completed 15 days late due to resource constraints. No unauthorized access was identified. Process improvements implemented.

Exception 3 (CC7.2): One change was deployed without documented approval due to an emergency production issue. Post-implementation review confirmed the change was necessary and properly implemented.

Exception 4 (CC8.1): Disaster recovery test in Q2 did not meet RTO target by 15 minutes due to database restoration delays. Infrastructure improvements are in progress.

Exception 5 (A1.2): Two vendor SOC 2 reports were outdated by more than 3 months. Updated reports have since been obtained.

Exception 6 (C1.1): Data classification labels were missing from 12% of sampled documents. Training and automation improvements are being implemented.""",
    },
    # Page 15 - Auditor's Opinion
    {
        "section_header": "Independent Service Auditor's Report",
        "page_number": 15,
        "content": """We have examined {VENDOR}'s description of its cloud services system and the suitability of the design and operating effectiveness of controls relevant to security, availability, and confidentiality, based on the criteria in the AICPA Trust Services Criteria.

{VENDOR}'s management is responsible for its assertion that the controls were suitably designed and operating effectively. Our responsibility is to express an opinion based on our examination.

Our examination was conducted in accordance with attestation standards established by the AICPA. Those standards require that we plan and perform the examination to obtain reasonable assurance about whether the description is fairly presented and the controls were suitably designed and operating effectively.

In our opinion, in all material respects:
a) The description fairly presents the cloud services system that was designed and implemented throughout the period January 1, 2024 to December 31, 2024.
b) The controls stated in the description were suitably designed to provide reasonable assurance that the service commitments and system requirements would be achieved.
c) The controls tested, which were those necessary to provide reasonable assurance that the service commitments and system requirements were achieved, operated effectively throughout the period.

The exceptions noted in this report, while requiring management attention, do not affect our overall opinion on the effectiveness of {VENDOR}'s controls.""",
    },
]
