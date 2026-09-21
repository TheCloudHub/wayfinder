# Security & Access Policy

## Identity

- Single sign-on via Okta for all systems. MFA is mandatory.
- Human access to cloud is **just-in-time** and least-privilege through the
  access portal. No standing admin/owner roles for individuals.
- Workloads authenticate with managed identities / workload identity, never
  long-lived static keys.

## Secrets

- Store secrets only in Azure Key Vault, GCP Secret Manager, or AWS Secrets
  Manager. Reference them at runtime; never bake into images or commit to git.
- Rotate credentials at least every 90 days; automate rotation where possible.
- Pre-commit secret scanning (gitleaks) runs on every commit.

## Data handling

- Classify data as Public, Internal, Confidential, or Restricted.
- Encrypt data at rest (cloud-managed keys minimum) and in transit (TLS 1.2+).
- Customer/PII data must stay within approved regions.

## Incident response

- Report suspected incidents in `#security-incident` immediately.
- Sev1/Sev2 pages the on-call security engineer via PagerDuty.
- Post-incident review (blameless) within 5 business days.
