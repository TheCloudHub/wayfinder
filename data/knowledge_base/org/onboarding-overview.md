# Engineering Onboarding Overview

Welcome to the engineering org. This guide is the entry point for new developers.

## Your first week

1. **Day 1** – Accounts: SSO/Okta, email, Slack, GitHub org, Jira, Confluence.
2. **Day 2** – Dev environment: install the standard toolchain, clone the
   `platform` mono-repo, run the bootstrap script `./scripts/dev-setup.sh`.
3. **Day 3** – Cloud access: request least-privilege roles via the access portal
   (see the Azure, GCP and AWS access guides).
4. **Day 4** – Ship a "hello world" change through CI/CD to the sandbox
   environment to validate your setup.
5. **Day 5** – Read the security, on-call, and incident response docs.

## Core systems

- **Source control:** GitHub. Trunk-based development with short-lived branches.
- **CI/CD:** GitHub Actions -> environment promotion (sandbox -> staging -> prod).
- **Issue tracking:** Jira. Docs in Confluence.
- **Observability:** Datadog for metrics/logs/traces; PagerDuty for alerting.
- **Secrets:** Cloud-native secret managers only (Key Vault / Secret Manager /
  AWS Secrets Manager). Never commit secrets.

## Getting help

- `#eng-help` for general questions.
- `#platform` for CI/CD, infra, and tooling.
- `#cloud-costs` for FinOps and budget questions.
- File a ticket to the Platform team for access or environment issues.
