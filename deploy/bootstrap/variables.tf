variable "aws_region" {
  type        = string
  description = "AWS region."
  default     = "us-east-1"
}

variable "name" {
  type        = string
  description = "Base name for resources."
  default     = "wayfinder"
}

variable "github_org" {
  type        = string
  description = "GitHub org that owns the repo."
  default     = "TheCloudHub"
}

variable "github_repo" {
  type        = string
  description = "GitHub repository name."
  default     = "wayfinder"
}

variable "state_bucket_name" {
  type        = string
  description = "Globally-unique S3 bucket name for Terraform state."
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
