# Azure Cloud Usage

## Access

- Request roles through the access portal (PIM-backed, time-bound).
- Standard roles: `Reader` for browsing, `Contributor` scoped to a resource
  group for building. No subscription-level `Owner` for individuals.
- Authenticate the CLI with `az login`; use `az account set --subscription <id>`.

## Landing zone & structure

- Management groups -> subscriptions per environment (sandbox/staging/prod).
- One resource group per service per environment: `rg-<service>-<env>`.
- Tag every resource: `owner`, `service`, `env`, `cost-center`, `data-class`.

## Common services & standards

- **Compute:** Azure Container Apps or AKS for services; Functions for events.
- **Data:** Azure SQL / PostgreSQL Flexible Server; Storage for blobs.
- **Secrets:** Azure Key Vault + managed identities (no connection strings).
- **Networking:** private endpoints for PaaS; deny public access by default.

## Useful CLI

```bash
az login
az group create -n rg-myservice-dev -l eastus
az containerapp up -n myservice -g rg-myservice-dev --source .
az keyvault secret set --vault-name kv-myservice --name db-pass --value ...
```

## Guardrails

- Azure Policy enforces required tags, allowed regions, and denies public IPs.
- Budgets and cost alerts are set per subscription; see the FinOps guide for the
  AWS-specific cost guardrails and mirror the mindset here.
