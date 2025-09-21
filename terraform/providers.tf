terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region                      = var.aws_region
  access_key                  = var.aws_access_key
  secret_key                  = var.aws_secret_key
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  s3_use_path_style           = true

  dynamic "endpoints" {
    for_each = var.use_localstack ? [1] : []
    content {
      sqs = var.sqs_endpoint
      sns = var.sns_endpoint
    }
  }
}
