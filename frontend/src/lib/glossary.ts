/**
 * Glossary of security and compliance terms for non-technical users.
 * Used for tooltips and inline explanations throughout the UI.
 */

export const glossary: Record<string, string> = {
  // Compliance Frameworks
  'SOC 2': 'Service Organization Control 2 - An auditing standard that verifies a company has controls for security, availability, and privacy.',
  'SOC 2 Type II': 'SOC 2 Type II includes testing of controls over a period (6-12 months), not just a point-in-time snapshot.',
  'ISO 27001': 'International standard for information security management systems (ISMS). Shows a company has systematic security processes.',
  'NIST 800-53': 'National Institute of Standards and Technology security controls catalog, used extensively by US federal agencies.',
  'NIST CSF': 'NIST Cybersecurity Framework - A voluntary framework for managing cybersecurity risk, organized around Identify, Protect, Detect, Respond, Recover.',
  'CIS Controls': 'Center for Internet Security Critical Security Controls - A prioritized set of 18 actions to protect against common cyber attacks.',
  'PCI-DSS': 'Payment Card Industry Data Security Standard - Required for any organization that handles credit card data.',
  'HIPAA': 'Health Insurance Portability and Accountability Act - US law protecting health information privacy and security.',
  'CAIQ': 'Consensus Assessments Initiative Questionnaire - Cloud Security Alliance\'s standardized questionnaire for cloud vendor assessments.',
  'SIG': 'Standardized Information Gathering - A questionnaire used to assess third-party vendor security practices.',
  'HECVAT': 'Higher Education Community Vendor Assessment Toolkit - Used by universities to assess cloud service providers.',
  'NIST AI RMF': 'NIST AI Risk Management Framework - Guidelines for trustworthy AI development with focus on governance, mapping, measurement, and management.',

  // Security Terms
  'MFA': 'Multi-Factor Authentication - Requires two or more verification methods (password + phone code) to access accounts.',
  'SSO': 'Single Sign-On - Log in once to access multiple related applications without re-authenticating.',
  'RBAC': 'Role-Based Access Control - Permissions assigned based on job role (admin, analyst, viewer) rather than individuals.',
  'Encryption at Rest': 'Data is encrypted when stored on disk, so if storage is stolen, data remains protected.',
  'Encryption in Transit': 'Data is encrypted when moving over networks (HTTPS/TLS), preventing interception.',
  'Zero Trust': 'Security model that requires verification for every access request, never assuming trust based on network location.',
  'Penetration Test': 'Authorized simulated cyber attack to find vulnerabilities before real attackers do.',
  'Vulnerability': 'A weakness in software or systems that could be exploited by attackers.',

  // Risk Terms
  'Critical Severity': 'Immediate action required - vulnerability could lead to full system compromise or major data breach.',
  'High Severity': 'Address urgently - significant risk that should be fixed within days.',
  'Medium Severity': 'Plan remediation - moderate risk that should be addressed within weeks.',
  'Low Severity': 'Monitor and schedule - minor issue with limited impact, fix when convenient.',
  'SLA': 'Service Level Agreement - Contractual commitment for response times and remediation deadlines.',
  'TPRM': 'Third-Party Risk Management - The process of identifying and mitigating risks from vendors and partners.',
  'Residual Risk': 'Risk that remains after security controls are applied.',
  'Risk Acceptance': 'Formal decision to accept a known risk without additional mitigation.',

  // AI Risk Terms
  'Model Poisoning': 'Attack where malicious data is injected into AI training to cause incorrect predictions.',
  'Data Provenance': 'Documentation of where training data came from, how it was collected, and if it\'s properly licensed.',
  'Bias Detection': 'Testing AI systems to identify unfair treatment of different demographic groups.',
  'Explainability': 'Ability to understand and explain why an AI system made a particular decision.',
  'Adversarial Robustness': 'AI system\'s resistance to inputs specifically crafted to cause misclassification.',

  // Document Types
  'Type I Report': 'Point-in-time assessment - describes controls as of a specific date.',
  'Type II Report': 'Period assessment - tests controls over time (typically 6-12 months).',
  'Bridge Letter': 'Temporary document covering the gap between old and new audit reports.',
  'Gap Analysis': 'Comparison of current state vs. desired state to identify what\'s missing.',

  // Platform Features
  'RAG': 'Retrieval-Augmented Generation - AI technique that retrieves relevant documents before generating responses, improving accuracy.',
  'Confidence Score': 'Percentage indicating how certain the AI is about a finding, based on available evidence.',
  'Citation': 'Reference to specific page and section in source document where evidence was found.',
};

/**
 * Get tooltip content for a term.
 */
export function getTermDefinition(term: string): string | undefined {
  return glossary[term];
}

/**
 * Get all terms starting with a specific letter (for glossary pages).
 */
export function getTermsByLetter(letter: string): Array<{ term: string; definition: string }> {
  return Object.entries(glossary)
    .filter(([term]) => term.toUpperCase().startsWith(letter.toUpperCase()))
    .map(([term, definition]) => ({ term, definition }))
    .sort((a, b) => a.term.localeCompare(b.term));
}

/**
 * Search glossary for terms matching a query.
 */
export function searchGlossary(query: string): Array<{ term: string; definition: string }> {
  const lowerQuery = query.toLowerCase();
  return Object.entries(glossary)
    .filter(
      ([term, definition]) =>
        term.toLowerCase().includes(lowerQuery) || definition.toLowerCase().includes(lowerQuery)
    )
    .map(([term, definition]) => ({ term, definition }));
}
