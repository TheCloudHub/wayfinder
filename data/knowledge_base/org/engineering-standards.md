# Engineering Standards

## Git & code review

- Trunk-based development; branch names `feature/<ticket>-<short-desc>`.
- All changes go through a pull request with at least **1 approving review**
  (2 for changes to `infra/` or `security/`).
- Keep PRs under ~400 lines of diff where possible.
- CI must be green before merge. Squash-merge to keep history linear.
- Conventional Commits format: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.

## Testing

- Unit tests required for new logic; target 80% coverage on changed lines.
- Integration tests run in the sandbox environment on every PR.
- No merging with skipped or flaky tests without a linked follow-up ticket.

## Languages & tooling

- **Backend:** Python (3.11+, FastAPI) and Go. Format with `ruff`/`gofmt`.
- **Frontend:** TypeScript + React.
- **IaC:** Terraform is the standard for all three clouds. Bicep allowed for
  Azure-only teams by exception.
- Pin dependencies; use lockfiles (`requirements.txt`/`poetry.lock`, `go.sum`).

## Definition of Done

- Code reviewed and merged, tests passing.
- Observability added (metrics, structured logs, tracing spans).
- Runbook/docs updated in Confluence.
- Feature flags default off in prod until validated.
