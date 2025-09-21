variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_access_key" {
  description = "AWS access key"
  type        = string
  default     = "test"
}

variable "aws_secret_key" {
  description = "AWS secret key"
  type        = string
  default     = "test"
}

variable "use_localstack" {
  description = "Whether to use LocalStack endpoints"
  type        = bool
  default     = true
}

variable "sqs_endpoint" {
  description = "SQS endpoint URL"
  type        = string
  default     = "http://localhost:4566"
}

variable "sns_endpoint" {
  description = "SNS endpoint URL"
  type        = string
  default     = "http://localhost:4566"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}
