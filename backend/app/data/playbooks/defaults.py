"""Default AI Governance Playbook templates.

These playbooks are designed for non-technical users in marketing, HR, and finance
to safely adopt AI tools following DoorDash's AI governance requirements.
"""

TOOL_SELECTION_PLAYBOOK = {
    "name": "AI Tool Selection Playbook",
    "description": "Guide for evaluating and selecting AI tools for your department. Perfect for non-technical users who want to adopt AI tools safely.",
    "phase": "tool_selection",
    "target_audience": "non_technical",
    "department": "all",
    "estimated_duration_minutes": 120,
    "icon": "search",
    "color": "#0066FF",
    "steps": [
        {
            "step_number": 1,
            "title": "Define Business Requirements",
            "description": "Clearly document what problem the AI tool needs to solve",
            "instructions": """Before selecting any AI tool, you need to clearly define what you're trying to accomplish.

1. Write a clear problem statement (2-3 sentences describing the challenge)
2. List the specific tasks the tool needs to perform
3. Identify who will use the tool and how often
4. Define success metrics (how will you know it's working?)
5. Estimate the data the tool will need access to""",
            "checklist": [
                {"id": "req_1", "text": "Problem statement documented", "required": True, "help_text": "Describe the business challenge in 2-3 sentences"},
                {"id": "req_2", "text": "Use cases listed with examples", "required": True, "help_text": "List at least 3 specific tasks the tool should perform"},
                {"id": "req_3", "text": "User list identified", "required": True, "help_text": "Who will use this tool? How often?"},
                {"id": "req_4", "text": "Success metrics defined", "required": True, "help_text": "What measurable outcomes indicate success?"},
                {"id": "req_5", "text": "Data requirements documented", "required": True, "help_text": "What data will the tool need to access?"}
            ],
            "estimated_time_minutes": 30,
            "tips": "Be specific about what you need. Vague requirements lead to wrong tool selections.",
            "resources": [
                {"title": "Requirements Template", "url": "/templates/ai-requirements", "type": "template"},
                {"title": "AI Tool Evaluation Guide", "url": "/docs/ai-evaluation", "type": "document"}
            ]
        },
        {
            "step_number": 2,
            "title": "Check Approved Vendor List",
            "description": "See if an approved tool already meets your needs",
            "instructions": """Before requesting a new tool, check if we already have an approved solution.

1. Review the Approved AI Vendor Registry in VendorAuditAI
2. Filter by your use case category
3. Compare features against your requirements from Step 1
4. If a match exists, you can skip to Step 5 (Final Approval)
5. If no match, proceed to Step 3 for new vendor evaluation""",
            "checklist": [
                {"id": "check_1", "text": "Reviewed approved vendor list", "required": True, "help_text": "Check the Approved AI Vendors page"},
                {"id": "check_2", "text": "Compared features to requirements", "required": True, "help_text": "Does an existing tool meet your needs?"},
                {"id": "check_3", "text": "Documented why approved tools don't meet needs (if applicable)", "required": False, "help_text": "If proceeding to new vendor, explain the gap"}
            ],
            "estimated_time_minutes": 15,
            "tips": "Using an already-approved tool is faster and safer. Only request new tools when necessary."
        },
        {
            "step_number": 3,
            "title": "Complete Data Classification",
            "description": "Identify what data the tool will access",
            "instructions": """Security needs to understand what data this tool will touch.

Classify each data type the tool will access:
- **Public**: No restrictions (marketing materials, public docs)
- **Internal**: Company confidential (internal reports, non-sensitive business data)
- **Sensitive**: PII, financial data (customer names, email addresses, purchase history)
- **Critical**: Payment data, health records (credit cards, SSN, medical info)

Document:
1. List all data types the tool will access
2. Classify each data type using the levels above
3. Document where data will be stored/processed
4. Note any data residency requirements (EU data must stay in EU, etc.)""",
            "checklist": [
                {"id": "data_1", "text": "All data types listed", "required": True, "help_text": "List every type of data the tool will see"},
                {"id": "data_2", "text": "Classification assigned to each", "required": True, "help_text": "Public, Internal, Sensitive, or Critical?"},
                {"id": "data_3", "text": "Storage locations documented", "required": True, "help_text": "Where will data be stored?"},
                {"id": "data_4", "text": "Residency requirements noted", "required": True, "help_text": "Any geographic restrictions?"}
            ],
            "required_approvals": ["security_analyst"],
            "estimated_time_minutes": 45,
            "warning": "Incorrectly classifying data can lead to compliance violations. When in doubt, classify higher."
        },
        {
            "step_number": 4,
            "title": "Submit Security Review Request",
            "description": "Request formal security assessment of the vendor",
            "instructions": """Now submit the vendor for security review.

1. Complete the Vendor Intake Form with all information from previous steps
2. Attach any vendor documentation (SOC 2 report, security whitepaper, privacy policy)
3. Include your data classification from Step 3
4. Submit to security team for review
5. Wait for security assessment results (typically 5-10 business days)

The security team will evaluate:
- Does the vendor have SOC 2 Type 2?
- How do they handle data?
- What's their incident response process?
- Are there any red flags?""",
            "checklist": [
                {"id": "sec_1", "text": "Vendor Intake Form completed", "required": True, "help_text": "Fill out all required fields"},
                {"id": "sec_2", "text": "Vendor documentation attached", "required": True, "help_text": "SOC 2, security docs, privacy policy"},
                {"id": "sec_3", "text": "Data classification attached", "required": True, "help_text": "Include output from Step 3"},
                {"id": "sec_4", "text": "Request submitted to security team", "required": True, "help_text": "Submit via VendorAuditAI"}
            ],
            "required_approvals": ["security_team"],
            "estimated_time_minutes": 30,
            "tips": "The more documentation you provide upfront, the faster the review."
        },
        {
            "step_number": 5,
            "title": "Obtain Final Approval",
            "description": "Get sign-off from required stakeholders",
            "instructions": """Once security review passes, get final approvals.

1. Compile all documentation from previous steps
2. Prepare cost/benefit summary
3. Submit for manager approval
4. Submit for security final sign-off
5. Once all approvals are received, proceed to the Deployment Playbook

Required approvals:
- Your direct manager
- Security team lead (for Sensitive/Critical data tools)
- Legal (if vendor processes EU data or has unusual terms)""",
            "checklist": [
                {"id": "approve_1", "text": "Documentation compiled", "required": True, "help_text": "All outputs from Steps 1-4"},
                {"id": "approve_2", "text": "Cost/benefit documented", "required": True, "help_text": "What's the ROI?"},
                {"id": "approve_3", "text": "Manager approval received", "required": True, "help_text": "Your direct manager signed off"},
                {"id": "approve_4", "text": "Security sign-off received", "required": True, "help_text": "Security team approved"}
            ],
            "required_approvals": ["manager", "security_lead"],
            "estimated_time_minutes": 60,
            "tips": "Once approved, proceed to the Secure Deployment Playbook before using the tool."
        }
    ]
}

DEPLOYMENT_PLAYBOOK = {
    "name": "Secure AI Tool Deployment Playbook",
    "description": "Step-by-step guide for deploying AI tools securely. Ensures proper configuration and training before go-live.",
    "phase": "deployment",
    "target_audience": "non_technical",
    "department": "all",
    "estimated_duration_minutes": 180,
    "icon": "rocket",
    "color": "#00D4AA",
    "steps": [
        {
            "step_number": 1,
            "title": "Configure Authentication",
            "description": "Set up secure access to the tool",
            "instructions": """Before anyone uses the tool, set up secure authentication.

1. **SSO Integration** (preferred)
   - Request SSO integration from IT
   - This lets users log in with their company credentials
   - No separate password to remember

2. **If SSO not available**
   - Use strong, unique passwords (16+ characters)
   - Enable MFA (multi-factor authentication)
   - Use a password manager

3. **Role-based access**
   - Set up different permission levels
   - Not everyone needs admin access
   - Document who has what access level""",
            "checklist": [
                {"id": "auth_1", "text": "SSO configured OR strong passwords set", "required": True, "help_text": "SSO preferred, strong passwords as fallback"},
                {"id": "auth_2", "text": "MFA enabled for all users", "required": True, "help_text": "All users must have 2FA enabled"},
                {"id": "auth_3", "text": "Roles and permissions configured", "required": True, "help_text": "Set up appropriate access levels"},
                {"id": "auth_4", "text": "Access list documented", "required": True, "help_text": "Who has access and at what level?"}
            ],
            "estimated_time_minutes": 45,
            "warning": "Never share credentials. Each user should have their own account."
        },
        {
            "step_number": 2,
            "title": "Configure Data Settings",
            "description": "Ensure data is handled securely",
            "instructions": """Configure how the tool handles your data.

1. **Data retention**
   - How long does the tool keep your data?
   - Set retention to minimum needed
   - Enable auto-deletion if available

2. **Training opt-out** (CRITICAL for AI tools)
   - Many AI tools use your data to train their models
   - This can expose sensitive information
   - ALWAYS opt out of training programs

3. **Export restrictions**
   - Limit who can export data
   - Enable audit logging for exports

4. **Encryption**
   - Verify data is encrypted at rest and in transit
   - Check the vendor's security documentation""",
            "checklist": [
                {"id": "data_1", "text": "Data retention configured", "required": True, "help_text": "Set to minimum necessary period"},
                {"id": "data_2", "text": "Training on data disabled", "required": True, "help_text": "CRITICAL: Opt out of AI training"},
                {"id": "data_3", "text": "Export restrictions set", "required": True, "help_text": "Limit who can export data"},
                {"id": "data_4", "text": "Audit logging enabled", "required": True, "help_text": "Track who does what"}
            ],
            "estimated_time_minutes": 30,
            "warning": "If you cannot disable AI training on your data, escalate to security before proceeding."
        },
        {
            "step_number": 3,
            "title": "Create Usage Guidelines",
            "description": "Document what users can and cannot do",
            "instructions": """Create clear guidelines for your team.

1. **Approved use cases**
   - List exactly what the tool should be used for
   - Be specific with examples

2. **Prohibited uses**
   - What should NEVER go into the tool?
   - Examples: customer SSNs, passwords, health info

3. **Escalation path**
   - Who do users contact with questions?
   - What's the process for edge cases?

4. **Share with team**
   - Post guidelines where team can find them
   - Get acknowledgment from each user""",
            "checklist": [
                {"id": "guide_1", "text": "Approved use cases documented", "required": True, "help_text": "List specific approved activities"},
                {"id": "guide_2", "text": "Prohibited uses documented", "required": True, "help_text": "What should NEVER be done?"},
                {"id": "guide_3", "text": "Escalation path defined", "required": True, "help_text": "Who to contact for questions"},
                {"id": "guide_4", "text": "Guidelines shared with all users", "required": True, "help_text": "Everyone must have access"}
            ],
            "estimated_time_minutes": 30,
            "tips": "Keep guidelines simple. If they're too long, people won't read them."
        },
        {
            "step_number": 4,
            "title": "Train Users",
            "description": "Ensure users know how to use the tool safely",
            "instructions": """Before go-live, train all users.

1. **Schedule training session**
   - 30-60 minutes is usually sufficient
   - Include demo of approved use cases

2. **Cover security basics**
   - DO: Use for approved purposes only
   - DON'T: Put sensitive data in prompts
   - DO: Report anything suspicious
   - DON'T: Share your login credentials

3. **Walk through guidelines**
   - Review the usage guidelines from Step 3
   - Answer questions

4. **Document attendance**
   - Record who attended training
   - Follow up with those who missed""",
            "checklist": [
                {"id": "train_1", "text": "Training session scheduled", "required": True, "help_text": "Book time on calendars"},
                {"id": "train_2", "text": "Training delivered", "required": True, "help_text": "Session completed"},
                {"id": "train_3", "text": "Attendance documented", "required": True, "help_text": "Record who attended"},
                {"id": "train_4", "text": "All users trained", "required": True, "help_text": "No one starts without training"}
            ],
            "estimated_time_minutes": 60,
            "tips": "Record the training session so new team members can watch it later."
        },
        {
            "step_number": 5,
            "title": "Go Live Verification",
            "description": "Final checks before full deployment",
            "instructions": """Final verification before enabling for all users.

1. **Security verification**
   - Have security team verify configurations
   - Quick 15-minute review

2. **Pilot test**
   - Start with 2-3 users for 1 week
   - Monitor for issues
   - Gather feedback

3. **Address issues**
   - Fix any problems found in pilot
   - Update guidelines if needed

4. **Full rollout**
   - Enable for all approved users
   - Announce via appropriate channel
   - Share guidelines link again""",
            "checklist": [
                {"id": "live_1", "text": "Security verification complete", "required": True, "help_text": "Security team approved config"},
                {"id": "live_2", "text": "Pilot test successful", "required": True, "help_text": "No major issues in pilot"},
                {"id": "live_3", "text": "Issues addressed", "required": True, "help_text": "All pilot feedback addressed"},
                {"id": "live_4", "text": "Go-live approval received", "required": True, "help_text": "Final approval to launch"}
            ],
            "required_approvals": ["security_lead"],
            "estimated_time_minutes": 60,
            "tips": "After go-live, proceed to the Regression Protection Playbook for ongoing monitoring."
        }
    ]
}

REGRESSION_PROTECTION_PLAYBOOK = {
    "name": "AI Tool Regression Protection Playbook",
    "description": "Ongoing monitoring to prevent security drift. Ensures your AI tool stays secure over time.",
    "phase": "regression_protection",
    "target_audience": "all",
    "department": "all",
    "estimated_duration_minutes": 60,
    "icon": "shield",
    "color": "#FFB800",
    "steps": [
        {
            "step_number": 1,
            "title": "Set Up Monitoring",
            "description": "Configure ongoing security monitoring",
            "instructions": """Set up monitoring to catch security issues early.

1. **Usage monitoring**
   - Enable analytics/usage tracking in the tool
   - Know who's using it and how

2. **Alert configuration**
   - Set up alerts for unusual activity
   - Examples: after-hours access, bulk exports, failed logins

3. **Access reviews**
   - Schedule regular reviews of who has access
   - Remove access when people change roles

4. **Document baseline**
   - Record normal usage patterns
   - Easier to spot anomalies later""",
            "checklist": [
                {"id": "mon_1", "text": "Usage monitoring enabled", "required": True, "help_text": "Track tool usage"},
                {"id": "mon_2", "text": "Alerts configured", "required": True, "help_text": "Get notified of unusual activity"},
                {"id": "mon_3", "text": "Access review schedule set", "required": True, "help_text": "Monthly or quarterly reviews"},
                {"id": "mon_4", "text": "Baseline documented", "required": True, "help_text": "Record normal patterns"}
            ],
            "estimated_time_minutes": 30
        },
        {
            "step_number": 2,
            "title": "Schedule Periodic Reviews",
            "description": "Set up regular security checkpoints",
            "instructions": """Schedule regular reviews to prevent drift.

1. **Quarterly security review**
   - Review all configurations
   - Check for vendor security updates
   - Update settings if needed

2. **Monthly access review**
   - Who has access?
   - Does everyone still need it?
   - Remove unnecessary access

3. **Annual vendor reassessment**
   - Full security review of vendor
   - Check if SOC 2 is still current
   - Review any incidents

4. **Calendar reminders**
   - Add all reviews to calendar
   - Set reminders 1 week before""",
            "checklist": [
                {"id": "rev_1", "text": "Quarterly review scheduled", "required": True, "help_text": "Every 3 months"},
                {"id": "rev_2", "text": "Monthly access review scheduled", "required": True, "help_text": "First week of each month"},
                {"id": "rev_3", "text": "Annual reassessment scheduled", "required": True, "help_text": "Full vendor review yearly"},
                {"id": "rev_4", "text": "Calendar reminders set", "required": True, "help_text": "Don't miss review dates"}
            ],
            "estimated_time_minutes": 15
        },
        {
            "step_number": 3,
            "title": "Document Change Process",
            "description": "Define how changes will be managed",
            "instructions": """Document the process for making changes.

1. **Adding new users**
   - Who approves new users?
   - What training is required?
   - How is access granted?

2. **Removing users**
   - When should access be removed?
   - Who is responsible for removal?
   - How quickly must it happen?

3. **Configuration changes**
   - Who can make config changes?
   - What changes require approval?
   - How are changes documented?

4. **Approval authority**
   - Define who can approve what
   - Document escalation path""",
            "checklist": [
                {"id": "change_1", "text": "User addition process documented", "required": True, "help_text": "How to add new users"},
                {"id": "change_2", "text": "User removal process documented", "required": True, "help_text": "How to remove users"},
                {"id": "change_3", "text": "Config change process documented", "required": True, "help_text": "How to make changes"},
                {"id": "change_4", "text": "Approvers defined", "required": True, "help_text": "Who approves what"}
            ],
            "estimated_time_minutes": 30
        },
        {
            "step_number": 4,
            "title": "Create Incident Response Plan",
            "description": "Plan for security incidents",
            "instructions": """Be prepared if something goes wrong.

1. **Define incidents**
   - What constitutes a security incident?
   - Examples: data breach, unauthorized access, malware

2. **Escalation contacts**
   - Who to call first?
   - Security team contact
   - Vendor support contact
   - Legal contact (if needed)

3. **Containment steps**
   - How to quickly stop an incident?
   - Disable user access
   - Revoke API keys
   - Contact vendor

4. **Communication template**
   - Pre-write incident communications
   - Who needs to be notified?
   - What information to share?""",
            "checklist": [
                {"id": "ir_1", "text": "Incident definition documented", "required": True, "help_text": "What counts as an incident?"},
                {"id": "ir_2", "text": "Escalation contacts listed", "required": True, "help_text": "Who to call"},
                {"id": "ir_3", "text": "Containment steps documented", "required": True, "help_text": "How to stop an incident"},
                {"id": "ir_4", "text": "Communication template created", "required": True, "help_text": "Pre-written notifications"}
            ],
            "estimated_time_minutes": 45,
            "warning": "If an incident occurs, follow the containment steps immediately, then notify security."
        }
    ]
}

# All default playbooks
DEFAULT_PLAYBOOKS = [
    TOOL_SELECTION_PLAYBOOK,
    DEPLOYMENT_PLAYBOOK,
    REGRESSION_PROTECTION_PLAYBOOK,
]
