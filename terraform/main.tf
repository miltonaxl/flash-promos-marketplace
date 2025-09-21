module "messaging" {
  source      = "./modules/messaging"
  queue_name  = "flash-promo-notifications"
  topic_name  = "flash-promo-topic"
  environment = var.environment
  tags = {
    Environment = var.environment
    Project     = "flash-promo"
  }
}
