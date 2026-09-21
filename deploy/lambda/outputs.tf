output "ecr_repository_url" {
  description = "Push the Lambda container image here."
  value       = aws_ecr_repository.this.repository_url
}

output "function_name" {
  description = "Deployed Lambda function name (empty until image_uri is set)."
  value       = try(aws_lambda_function.this[0].function_name, "")
}

output "function_url" {
  description = "Public/IAM Function URL for the Wayfinder API (empty until image_uri is set)."
  value       = try(aws_lambda_function_url.this[0].function_url, "")
}

output "lambda_role_arn" {
  description = "IAM role assumed by the Lambda."
  value       = aws_iam_role.lambda.arn
}
