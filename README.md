# Optimizing AWS Systems Manager Session Manager Logs

AWS Systems Manager Session Manager is a powerful tool for managing servers securely. However, its default logging behavior can result in large log files, leading to higher storage costs and reduced audit efficiency. This repository demonstrates how to optimize Session Manager logs using an AWS Lambda function.

## Problem Statement

Commands like `tail` or `less` generate excessive log output, causing:
- **Increased storage costs**: Large log file sizes.
- **Reduced auditability**: Logs cluttered with redundant output.

## Proposed Solution

A Lambda function is used to:
1. Identify outputs of commands like `tail` and `less`.
2. Truncate unnecessary lines and replace them with summaries.
3. Save optimized logs to a separate S3 directory.

## Architecture Overview

- **Trigger**: S3 event notification triggers the Lambda function when a log is uploaded.
- **Processing**: The Lambda function processes logs, removing unnecessary content.
- **Output**: Optimized logs are stored in an S3 bucket under `processed-ssm-logs/`.

## Implementation Steps

### 1. Set Up S3 Bucket
- Create a bucket (e.g., `my-ssm-logs-bucket`) with directories:
  - `ssm-logs/`: For original logs.
  - `processed-ssm-logs/`: For optimized logs.

### 2. Configure Systems Manager
- Enable session logging to the S3 bucket.
- Grant the required IAM role `s3:PutObject` permissions.

### 3. Create the Lambda Function
- Use the [Lambda function code](lambda_function.py) provided in this repository to process the logs.
- Attach an IAM role allowing `s3:GetObject` and `s3:PutObject`.

### 4. Test the Setup
- Start a session, run commands, and verify the optimized logs in `processed-ssm-logs`.

## Benefits
- **Cost Efficiency**: Reduced storage costs by minimizing log size.
- **Improved Auditability**: Streamlined logs for better insights.
