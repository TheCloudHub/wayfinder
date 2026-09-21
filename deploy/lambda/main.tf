data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name

  s3vectors_bucket_arn = "arn:aws:s3vectors:${local.region}:${local.account_id}:bucket/${var.s3_vector_bucket}"
}

# ── Container registry ───────────────────────────────────────────────────────
resource "aws_ecr_repository" "this" {
  name                 = var.name
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

# Allow the Lambda service to pull images from this repo (required for
# container-image functions).
resource "aws_ecr_repository_policy" "lambda_pull" {
  repository = aws_ecr_repository.this.name
  policy = jsonencode({
    Version = "2008-10-17"
    Statement = [{
      Sid       = "LambdaECRImageRetrievalPolicy"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"]
      Condition = {
        StringLike = {
          "aws:sourceArn" = "arn:aws:lambda:${local.region}:${local.account_id}:function:${var.name}*"
        }
      }
    }]
  })
}

# ── IAM role for the Lambda ──────────────────────────────────────────────────
data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.name}-lambda"
  assume_role_policy = data.aws_iam_policy_document.assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "app" {
  # Bedrock: only Amazon foundation models + this account's inference profiles.
  statement {
    sid     = "BedrockInvoke"
    actions = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
    resources = [
      "arn:aws:bedrock:*::foundation-model/amazon.*",
      "arn:aws:bedrock:*:${local.account_id}:inference-profile/*",
    ]
  }

  # S3 Vectors: scoped to this project's bucket and its indexes.
  statement {
    sid = "S3Vectors"
    actions = [
      "s3vectors:CreateVectorBucket",
      "s3vectors:GetVectorBucket",
      "s3vectors:CreateIndex",
      "s3vectors:GetIndex",
      "s3vectors:ListIndexes",
      "s3vectors:PutVectors",
      "s3vectors:QueryVectors",
      "s3vectors:GetVectors",
    ]
    resources = [
      local.s3vectors_bucket_arn,
      "${local.s3vectors_bucket_arn}/index/*",
    ]
  }
}

resource "aws_iam_role_policy" "app" {
  name   = "${var.name}-app"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.app.json
}

# ── Logs ─────────────────────────────────────────────────────────────────────
resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${var.name}"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

# ── Lambda (container image) ─────────────────────────────────────────────────
resource "aws_lambda_function" "this" {
  count = var.image_uri == "" ? 0 : 1

  function_name = var.name
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = var.image_uri
  memory_size   = var.memory_size
  timeout       = var.timeout
  publish       = true

  environment {
    variables = {
      VECTOR_BACKEND         = "s3vectors"
      BEDROCK_LLM_MODEL_ID   = var.bedrock_llm_model_id
      BEDROCK_EMBED_MODEL_ID = var.bedrock_embed_model_id
      S3_VECTOR_BUCKET       = var.s3_vector_bucket
      S3_VECTOR_INDEX        = var.s3_vector_index
    }
  }

  depends_on = [aws_cloudwatch_log_group.this, aws_ecr_repository_policy.lambda_pull]
  tags       = var.tags
}

resource "aws_lambda_alias" "live" {
  count            = var.image_uri == "" ? 0 : 1
  name             = "live"
  function_name    = aws_lambda_function.this[0].function_name
  function_version = aws_lambda_function.this[0].version
}

resource "aws_lambda_provisioned_concurrency_config" "warm" {
  count                             = var.image_uri != "" && var.provisioned_concurrency > 0 ? 1 : 0
  function_name                     = aws_lambda_function.this[0].function_name
  qualifier                         = aws_lambda_alias.live[0].name
  provisioned_concurrent_executions = var.provisioned_concurrency
}

resource "aws_lambda_function_url" "this" {
  count              = var.image_uri == "" ? 0 : 1
  function_name      = aws_lambda_function.this[0].function_name
  qualifier          = aws_lambda_alias.live[0].name
  authorization_type = var.function_url_auth_type

  cors {
    allow_origins = ["*"]
    allow_methods = ["*"]
    allow_headers = ["*"]
  }
}
