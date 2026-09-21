output "deploy_role_arn" {
  description = "Set repo variable AWS_DEPLOY_ROLE_ARN to this."
  value       = aws_iam_role.deploy.arn
}

output "tf_state_bucket" {
  description = "Set repo variable TF_STATE_BUCKET to this."
  value       = aws_s3_bucket.state.id
}

output "tf_lock_table" {
  description = "Set repo variable TF_LOCK_TABLE to this."
  value       = aws_dynamodb_table.lock.name
}

output "oidc_provider_arn" {
  description = "GitHub Actions OIDC provider ARN."
  value       = aws_iam_openid_connect_provider.github.arn
}
