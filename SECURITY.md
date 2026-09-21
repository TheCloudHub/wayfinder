# Security Policy

## Reporting a vulnerability

Please report suspected security issues privately to the platform team via
GitHub Security Advisories ("Report a vulnerability" on this repository) or the
`#security` channel. Do not open public issues for vulnerabilities.

We aim to acknowledge reports within 2 business days.

## Secure-by-design measures in this repo

**Secrets & credentials**
- No long-lived AWS keys. Runtime uses the AWS credential chain (task/instance
  roles); CI/CD assumes an IAM role via GitHub OIDC (`id-token: write`).
- `.env`, `*.tfvars`, and the local vector store are gitignored.
- Secret scanning (gitleaks) runs in CI; enable GitHub secret scanning + push
  protection on the repository.

**Least privilege**
- Lambda IAM policy is scoped: Bedrock limited to Amazon foundation models and
  this account's inference profiles; S3 Vectors limited to the project bucket
  and its indexes.
- GitHub Actions use minimal `permissions:` blocks (default `contents: read`).

**Supply chain**
- Dependabot updates for pip, GitHub Actions, Terraform, and Docker.
- `harden-runner` audits runner egress. Pin actions to commit SHAs for stricter
  guarantees.
- SAST runs in CI without GitHub Advanced Security: `bandit` (Python) and
  `actionlint` (workflows). Enable CodeQL if GHAS is purchased for the org.

**Application**
- Answers are grounded strictly in retrieved context (no fabricated policy).
- CORS is off by default (same-origin UI); enable explicitly via
  `CORS_ALLOW_ORIGINS`.
- The Lambda Function URL defaults to `AWS_IAM` auth. Setting it to `NONE`
  makes the endpoint public — do so only behind additional controls.

## Hardening checklist before production

- [ ] Enable branch protection on `main` (required reviews + status checks).
- [ ] Enable GitHub secret scanning and push protection.
- [ ] Configure the `production` environment with required reviewers.
- [ ] Create the OIDC deploy role with a trust policy scoped to this repo/branch.
- [ ] Keep `function_url_auth_type = "AWS_IAM"` unless fronted by a gateway/CDN.
- [ ] Set `CORS_ALLOW_ORIGINS` to explicit origins if cross-origin is required.
