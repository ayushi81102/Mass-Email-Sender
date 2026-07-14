# Mass Email System — AWS Serverless
**Tech Stack:** AWS Lambda · S3 · SES · SNS · Python · HTML/CSS/JS

---

## Architecture
```
Frontend (index.html)
      │
      │ Upload CSV
      ▼
  AWS S3 Bucket  ──── S3 Event Trigger ────▶  AWS Lambda
                                                  │
                                    ┌─────────────┼─────────────┐
                                    ▼             ▼             ▼
                                Read CSV      Send Emails    Publish
                                from S3       via SES      Summary to SNS
```

---

## Project Structure
```
mass-email-project/
├── frontend/
│   └── index.html          # Upload UI (drag & drop CSV)
├── lambda/
│   └── lambda_function.py  # AWS Lambda handler
├── s3-trigger/
│   └── recipients.csv      # Sample CSV file
└── README.md
```

---

## Setup Instructions

### Step 1 — Verify Email in SES
1. Go to **AWS SES Console → Verified Identities**
2. Click **Create Identity → Email Address**
3. Enter `harikaneela988@gmail.com` and verify it

### Step 2 — Create S3 Bucket
1. Go to **AWS S3 Console → Create Bucket**
2. Name it e.g. `mass-email-bucket-harika`
3. Uncheck "Block all public access" if needed for testing
4. Go to **Properties → Event Notifications → Create Event Notification**
   - Event type: `s3:ObjectCreated:*`
   - Destination: **Lambda Function** → select your Lambda

### Step 3 — Create SNS Topic
1. Go to **AWS SNS Console → Topics → Create Topic**
2. Type: **Standard**, Name: `EmailNotifications`
3. Copy the ARN and paste it in `lambda_function.py` → `SNS_TOPIC_ARN`
4. Create a subscription (Email) with your email to receive job reports

### Step 4 — Deploy Lambda
1. Go to **AWS Lambda Console → Create Function**
2. Runtime: **Python 3.12**
3. Paste the code from `lambda/lambda_function.py`
4. Set timeout to **5 minutes** (for large lists)
5. Attach IAM role with these permissions:
   - `AmazonSESFullAccess`
   - `AmazonSNSFullAccess`
   - `AmazonS3ReadOnlyAccess`

### Step 5 — Test It
1. Open `frontend/index.html` in your browser
2. Upload `recipients.csv`
3. Enter your bucket name and region
4. Click **Upload & Trigger Email Pipeline**
5. Emails are sent via SES → SNS summary arrives in your inbox

---

## CSV Format
```csv
name,email,subject,message
Alice,alice@example.com,Hello!,Hi Alice welcome aboard.
Bob,bob@example.com,Hello!,Hi Bob welcome aboard.
```

---

## Built by Harika Neela
- [LinkedIn](https://www.linkedin.com/in/harika-neela-1452b5237/)
- B.Tech CSE | AWS Certified Cloud Practitioner
