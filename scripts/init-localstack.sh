#!/bin/bash

# Wait for LocalStack to be ready
until awslocal sqs list-queues; do
  echo "LocalStack is not ready yet. Retrying in 3 seconds..."
  sleep 3
done

# Create SQS queue
awslocal sqs create-queue --queue-name flash-promo-notifications

# Create SNS topic
awslocal sns create-topic --name flash-promo-topic

# Subscribe SQS to SNS
awslocal sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:000000000000:flash-promo-topic \
  --protocol sqs \
  --notification-endpoint arn:aws:sqs:us-east-1:000000000000:flash-promo-notifications

echo "LocalStack initialization complete"