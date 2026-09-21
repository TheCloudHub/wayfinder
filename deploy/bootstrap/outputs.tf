output "deploy_role_arn" {
  description = "Set repo variable AWS_DEPLOY_ROLE_ARN to this."
  value       = aws_iam_role.deploy.arn
}

output "tf_state_bucket" {
  description = "Set repo variable TF_STATE_BUCKET to this. Created by the Deploy workflow on first run."
  value       = local.state_bucket
}

output "tf_lock_table" {
  description = "Set repo variable TF_LOCK_TABLE to this. Created by the Deploy workflow on first run."
  value       = local.lock_table
}

output "oidc_provider_arn" {
  description = "GitHub Actions OIDC provider ARN."
  value       = aws_iam_openid_connect_provider.github.arn
}
