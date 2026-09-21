# AWS FinOps Guardrails

Cost is a first-class engineering concern. These guardrails keep AWS spend
predictable and attributable.

## Accountability & tagging

- **Mandatory cost allocation tags** on every resource: `owner`, `service`,
  `env`, `cost-center`. Untagged resources are flagged daily and may be stopped.
- Activate these as **cost allocation tags** in the billing console so they show
  up in Cost Explorer and the Cost and Usage Report (CUR).
- Each service has a monthly budget owned by its team.

## Budgets & alerts

- **AWS Budgets** per account and per `service` tag. Alert thresholds at
  **50% / 80% / 100%** of the monthly budget, plus a **forecasted-to-exceed**
  alert. Notifications go to the owning team and `#cloud-costs`.
- **Cost Anomaly Detection** enabled org-wide with alerts on unexpected spikes.

## Preventive guardrails (SCPs & policy)

- SCPs restrict usage to **approved regions** to avoid data-egress surprises.
- Deny launching disallowed/expensive instance families in non-prod (e.g. no
  GPU or `*.metal` in sandbox without an exception).
- Require `env=sandbox|staging|prod` tag on compute at creation via policy.

## Compute cost controls

- Right-size continuously using Compute Optimizer recommendations.
- Prefer **Fargate/Lambda** for spiky workloads; use **Spot** for fault-tolerant
  and batch workloads.
- Purchase **Savings Plans / Reserved Instances** for steady-state baseline
  after 30 days of stable usage. Coverage target: 70-80% of baseline.
- **Auto-stop non-prod** compute nightly and on weekends (scheduler/Lambda).

## Storage & data controls

- S3 lifecycle policies: transition to IA/Glacier and expire per data class.
- Delete unattached EBS volumes and old snapshots; enable EBS `gp3` over `gp2`.
- Set RDS/Aurora to stop in non-prod outside business hours where feasible.
- Watch **NAT Gateway** and cross-AZ/egress traffic; use VPC endpoints.

## Visibility & reviews

- Weekly cost review of top movers in `#cloud-costs`.
- Monthly FinOps review per team against budget; unit-cost metrics (e.g. cost
  per request / per tenant) tracked over time.
- Orphaned resource sweep (unattached IPs, idle load balancers, empty clusters).

## Quick checklist for a new service

1. Tags applied (`owner`, `service`, `env`, `cost-center`).
2. Budget + alerts created for the `service` tag.
3. Non-prod auto-stop schedule configured.
4. Storage lifecycle rules set.
5. Spot/Savings Plan strategy documented.
