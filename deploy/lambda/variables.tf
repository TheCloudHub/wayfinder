variable "aws_region" {
  type        = string
  description = "AWS region for all resources."
  default     = "us-east-1"
}

variable "name" {
  type        = string
  description = "Base name for the Wayfinder resources."
  default     = "wayfinder"
}

variable "image_uri" {
  type        = string
  description = "ECR image URI (with tag or digest) for the Lambda container. Leave blank on first apply to create the ECR repo only."
  default     = ""
}

variable "bedrock_llm_model_id" {
  type        = string
  description = "Bedrock generation model id (inference profile)."
  default     = "us.amazon.nova-2-lite-v1:0"
}

variable "bedrock_embed_model_id" {
  type        = string
  description = "Bedrock embeddings model id."
  default     = "amazon.titan-embed-text-v2:0"
}

variable "s3_vector_bucket" {
  type        = string
  description = "Amazon S3 Vectors bucket name."
  default     = "wayfinder-rag"
}

variable "s3_vector_index" {
  type        = string
  description = "Amazon S3 Vectors index name."
  default     = "knowledge-base"
}

variable "memory_size" {
  type        = number
  description = "Lambda memory (MB). vCPU scales with memory."
  default     = 1024
}

variable "timeout" {
  type        = number
  description = "Lambda timeout in seconds."
  default     = 60
}

variable "provisioned_concurrency" {
  type        = number
  description = "Warm instances kept initialized on the live alias. 0 disables (cheapest); set >0 to remove cold starts."
  default     = 0
}

variable "function_url_auth_type" {
  type        = string
  description = "Auth for the Function URL. AWS_IAM requires SigV4 signed requests; NONE makes the endpoint PUBLIC."
  default     = "AWS_IAM"

  validation {
    condition     = contains(["AWS_IAM", "NONE"], var.function_url_auth_type)
    error_message = "function_url_auth_type must be 'AWS_IAM' or 'NONE'."
  }
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days."
  default     = 14
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to all resources."
  default = {
    service     = "wayfinder"
    owner       = "platform"
    cost-center = "engineering"
  }
}
