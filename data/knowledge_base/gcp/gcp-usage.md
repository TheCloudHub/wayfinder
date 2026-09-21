# GCP Cloud Usage

## Access

- Access granted through Google Groups mapped to IAM roles, time-bound.
- Prefer predefined roles scoped to a project; avoid `roles/owner` for people.
- Authenticate: `gcloud auth login` and `gcloud config set project <id>`.
- Applications use **Workload Identity Federation** / service accounts with no
  downloaded JSON keys.

## Project structure

- Organization -> folders per domain -> one project per service per environment:
  `svc-<name>-<env>`.
- Enforce labels: `owner`, `service`, `env`, `cost-center`, `data-class`.

## Common services & standards

- **Compute:** Cloud Run for stateless services; GKE Autopilot for complex
  workloads; Cloud Functions for events.
- **Data:** Cloud SQL (Postgres), BigQuery for analytics, GCS for objects.
- **Secrets:** Secret Manager; mount at runtime via the service account.
- **Networking:** VPC Service Controls + Private Google Access; no public IPs on
  data services.

## Useful CLI

```bash
gcloud auth login
gcloud config set project svc-myservice-dev
gcloud run deploy myservice --source . --region us-central1
gcloud secrets create db-pass --replication-policy=automatic
```

## Guardrails

- Organization Policies restrict regions, block public IPs, and require OS Login.
- Budgets with alerts configured per project; anomalies routed to `#cloud-costs`.
