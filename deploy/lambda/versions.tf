terraform {
  required_version = ">= 1.6.0"

  # Remote state so CD runs share state. Configure per-environment with:
  #   terraform init -backend-config=backend.hcl
  # (bucket/key/region/dynamodb_table). See deploy/bootstrap for provisioning.
  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
