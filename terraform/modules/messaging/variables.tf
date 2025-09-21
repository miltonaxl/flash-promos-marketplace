variable "queue_name" {
  description = "Name of the SQS queue"
  type        = string
  default     = "flash-promo-notifications"
}

variable "topic_name" {
  description = "Name of the SNS topic"
  type        = string
  default     = "flash-promo-topic"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
