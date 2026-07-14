import boto3
import json
import csv
import io
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
ses_client = boto3.client('ses', region_name='ap-south-1')
sns_client = boto3.client('sns', region_name='ap-south-1')

SENDER_EMAIL = "harikaneela988@gmail.com"   # Must be verified in AWS SES
SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:YOUR_ACCOUNT_ID:EmailNotifications"  # Replace with your SNS ARN


def lambda_handler(event, context):
    """
    Triggered by an S3 PUT event when a CSV file of recipients is uploaded.
    Reads the CSV, sends emails via SES, and publishes a summary to SNS.
    """
    logger.info("Lambda triggered by S3 event")

    # --- Step 1: Get the uploaded file from S3 ---
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    logger.info(f"Processing file: s3://{bucket_name}/{file_key}")

    s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    file_content = s3_response['Body'].read().decode('utf-8')

    # --- Step 2: Read email list from CSV ---
    # Expected CSV format: name,email,subject,message
    recipients = []
    reader = csv.DictReader(io.StringIO(file_content))
    for row in reader:
        recipients.append(row)

    logger.info(f"Total recipients found: {len(recipients)}")

    # --- Step 3: Send emails via SES ---
    success_count = 0
    failed_count = 0
    failed_emails = []

    for recipient in recipients:
        try:
            name    = recipient.get('name', 'User')
            email   = recipient.get('email', '').strip()
            subject = recipient.get('subject', 'Hello from Harika!')
            message = recipient.get('message', f"Hi {name}, this is a test email.")

            if not email:
                logger.warning(f"Skipping row with missing email: {recipient}")
                failed_count += 1
                continue

            ses_client.send_email(
                Source=SENDER_EMAIL,
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Text': {
                            'Data': message,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': f"""
                            <html>
                              <body style="font-family: Arial, sans-serif; padding: 20px;">
                                <h2 style="color: #1A5276;">{subject}</h2>
                                <p>{message}</p>
                                <hr/>
                                <small style="color: gray;">Sent by Mass Email System | AWS Lambda + SES</small>
                              </body>
                            </html>
                            """,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            success_count += 1
            logger.info(f"Email sent to {email}")

        except Exception as e:
            logger.error(f"Failed to send to {recipient.get('email')}: {str(e)}")
            failed_count += 1
            failed_emails.append(recipient.get('email', 'unknown'))

    # --- Step 4: Publish summary notification to SNS ---
    summary_message = (
        f"Mass Email Job Completed\n"
        f"File: {file_key}\n"
        f"Total Recipients: {len(recipients)}\n"
        f"Successfully Sent: {success_count}\n"
        f"Failed: {failed_count}\n"
    )
    if failed_emails:
        summary_message += f"Failed Emails: {', '.join(failed_emails)}"

    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="Mass Email Job Summary",
        Message=summary_message
    )
    logger.info("SNS notification published")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Mass email job completed',
            'total': len(recipients),
            'success': success_count,
            'failed': failed_count
        })
    }
