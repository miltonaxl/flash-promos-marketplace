resource "aws_sqs_queue" "this" {
  name = "${var.queue_name}-${var.environment}"
  tags = var.tags
}

resource "aws_sns_topic" "this" {
  name = "${var.topic_name}-${var.environment}"
  tags = var.tags
}

resource "aws_sns_topic_subscription" "this" {
  topic_arn = aws_sns_topic.this.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.this.arn
}
