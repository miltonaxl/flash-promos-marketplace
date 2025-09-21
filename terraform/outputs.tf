output "sqs_queue_url" {
  description = "SQS Queue URL"
  value       = module.messaging.sqs_queue_url
}

output "sns_topic_arn" {
  description = "SNS Topic ARN"
  value       = module.messaging.sns_topic_arn
}
