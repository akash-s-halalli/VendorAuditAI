# Security Policy

## Supported Versions

VendorAuditAI is committed to maintaining security for the following versions:

| Version | Supported          | End of Support |
| ------- | ------------------ | -------------- |
| 1.x.x   | Yes                | Active         |
| < 1.0   | No                 | Deprecated     |

## Reporting a Vulnerability

We take security seriously at VendorAuditAI. If you discover a security vulnerability, please report it responsibly.

### For Critical Vulnerabilities

**DO NOT** open a public GitHub issue. Instead:

1. Email: **security@vendorauditai.com**
2. Subject: `[SECURITY] Brief description`
3. Include:
   - Detailed description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Any proof-of-concept code (if applicable)
   - Suggested remediation (if any)

### For Non-Critical Issues

For low-severity concerns, security best practices, or hardening suggestions, you may use our [Security Issue Template](https://github.com/MikeDominic92/VendorAuditAI/issues/new?template=security_vulnerability.yml).

## Response Timeline

| Phase | Timeline |
|-------|----------|
| Initial Acknowledgment | Within 48 hours |
| Preliminary Assessment | Within 5 business days |
| Status Update | Within 7 days |
| Critical Fix | Within 30 days |
| Non-Critical Fix | Within 90 days |

## Security Measures

VendorAuditAI implements enterprise-grade security controls:

### Authentication & Authorization
- JWT-based authentication with secure token handling
- SAML 2.0 SSO integration for enterprise identity providers
- Multi-Factor Authentication (MFA/TOTP) support
- Role-Based Access Control (RBAC)
- Session management with secure cookie attributes

### API Security
- Rate limiting on all API endpoints
- Request validation using Pydantic schemas
- CORS configuration with explicit origin allowlists
- API versioning for backwards compatibility

### Data Protection
- TLS 1.3 encryption for data in transit
- AES-256 encryption for sensitive data at rest
- Parameterized queries to prevent SQL injection
- Input sanitization and output encoding for XSS prevention
- Secure file upload validation

### Infrastructure
- Isolated container deployments
- Environment-based configuration management
- Secrets management (no hardcoded credentials)
- Comprehensive audit logging

### Compliance
- SOC 2 aligned security practices
- OWASP Top 10 vulnerability prevention
- Regular dependency updates and security patches

## Security Best Practices for Users

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Use `.env` files (gitignored) for sensitive configuration
3. **Access Control**: Follow principle of least privilege
4. **Updates**: Keep your deployment updated to the latest version
5. **Monitoring**: Enable audit logging and monitor for anomalies

## Bug Bounty

We do not currently operate a formal bug bounty program. However, we are grateful for responsible disclosure and will:

- Acknowledge security researchers who report valid vulnerabilities
- Provide recognition in our security acknowledgments (with permission)
- Work collaboratively on coordinated disclosure timelines

## Security Contacts

- Primary: security@vendorauditai.com
- GitHub Security Advisories: [Enable for this repository](https://github.com/MikeDominic92/VendorAuditAI/security/advisories)

## Acknowledgments

We thank the security research community for helping keep VendorAuditAI secure. Researchers who have contributed to our security will be acknowledged here (with their permission).

---

*Last Updated: January 2026*
