# AWS Cloud Usage

## Access

- Access via AWS IAM Identity Center (SSO). Use permission sets, not IAM users.
- Authenticate: `aws sso login --profile <profile>`; set `AWS_PROFILE`.
- Workloads use **IAM roles** (IRSA on EKS, task roles on ECS, instance
  profiles). No long-lived access keys for services.

## Account structure

- AWS Organizations with OUs per environment; one account per
  environment/domain boundary (sandbox/staging/prod).
- Service Control Policies (SCPs) enforce allowed regions and deny risky APIs.
- Tag every resource: `owner`, `service`, `env`, `cost-center`, `data-class`.

## Common services & standards

- **Compute:** ECS Fargate or EKS for services; Lambda for events.
- **Data:** RDS/Aurora Postgres; DynamoDB for key-value; S3 for objects.
- **Secrets:** AWS Secrets Manager / SSM Parameter Store (SecureString).
- **Networking:** private subnets by default; S3/ECR via VPC endpoints; block
  public S3 access at the account level.

## Useful CLI

```bash
aws sso login --profile dev
aws sts get-caller-identity
aws ecs deploy ...            # via CI/CD pipeline
aws secretsmanager create-secret --name db-pass --secret-string ...
aws s3 ls
```

## Guardrails

- S3 Block Public Access enforced org-wide.
- SCPs deny creation of IAM users and disabling of CloudTrail/GuardDuty.
- See `finops/aws-finops-guardrails.md` for cost controls.
