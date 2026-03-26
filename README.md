# Set Up and Monitor a WordPress Instance on AWS

## Project Overview

This project deploys and monitors two WordPress environments on AWS using CloudFormation:

- **Live Environment** — Always running, used for publishing blogs to the public
- **Dev Environment** — Runs only during business hours (9 AM – 6 PM CST), used for development and testing

---

## Architecture Diagram

```
                        AWS Cloud
                           |
              +------------+------------+
              |                         |
        [Live Stack]               [Dev Stack]
              |                         |
         EC2 Instance              EC2 Instance
         (Always ON)               (9AM-6PM only)
              |                         |
        Elastic IP                Elastic IP
              |                         |
      CloudWatch Alarms         CloudWatch Alarms
              |                         |
          SNS Alerts               SNS Alerts
                                        |
                              +--------------------+
                              |                    |
                        Lambda (Start)      Lambda (Stop)
                              |                    |
                        EventBridge           EventBridge
                        (9 AM CST)            (6 PM CST)
```

---

## AWS Services Used

| Service | Purpose |
|---|---|
| **CloudFormation** | Infrastructure as Code — provisions all AWS resources |
| **EC2** | Virtual servers that run WordPress |
| **S3** | Stores the CloudFormation template |
| **Lambda** | Python functions to start/stop the Dev instance |
| **EventBridge** | Schedules Lambda to trigger at 9 AM and 6 PM |
| **CloudWatch** | Monitors CPU usage and instance health |
| **SNS** | Sends email alerts when alarms trigger |
| **IAM** | Manages permissions for EC2 and Lambda |
| **Elastic IP** | Provides a fixed public IP address for each instance |

---

## Project Structure

```
wordpress-aws-project/
├── cloudformation/
│   └── wordpress-stack.yaml   # Main CloudFormation template
├── scripts/
│   ├── start-instance.py      # Lambda function to start Dev instance
│   └── stop-instance.py       # Lambda function to stop Dev instance
└── README.md                  # Project documentation
```

---

## Prerequisites

- AWS account
- EC2 Key Pair created in your region
- S3 bucket to store the CloudFormation template

---

## Deployment Steps

### Step 1: Upload Template to S3
1. Create an S3 bucket
2. Upload `cloudformation/wordpress-stack.yaml` to the bucket
3. Copy the Object URL of the uploaded file

### Step 2: Deploy Live Stack
1. Go to AWS CloudFormation Console
2. Click **"Create stack"** → **"With new resources"**
3. Select **"Amazon S3 URL"** and paste the Object URL
4. Set the following parameters:
   - Stack name: `wordpress-live-stack`
   - EnvironmentType: `live`
   - KeyPairName: your key pair name
   - InstanceType: `t2.micro`
   - DBPassword: your chosen password
5. Acknowledge IAM capabilities and click **"Submit"**
6. Wait for **CREATE_COMPLETE**

### Step 3: Deploy Dev Stack
Repeat Step 2 with these changes:
- Stack name: `wordpress-dev-stack`
- EnvironmentType: `dev`

### Step 4: Set Up Lambda Functions
1. Create a Lambda function named `wordpress-dev-start` using Python 3.12
2. Paste the contents of `scripts/start-instance.py`
3. Replace the Instance ID with your Dev EC2 Instance ID from CloudFormation Outputs
4. Attach `AmazonEC2FullAccess` policy to the Lambda role
5. Repeat for `wordpress-dev-stop` using `scripts/stop-instance.py`

### Step 5: Schedule with EventBridge
From each Lambda function, add an EventBridge trigger:

| Function | Schedule Expression | Time (CST) |
|---|---|---|
| `wordpress-dev-start` | `cron(0 14 * * ? *)` | 9:00 AM |
| `wordpress-dev-stop` | `cron(0 23 * * ? *)` | 6:00 PM |

---

## How the Scheduling Works

AWS EventBridge uses UTC time. Houston (CST) is UTC-5 during daylight saving:

| Houston Time | UTC Time | Action |
|---|---|---|
| 9:00 AM CST | 14:00 UTC | Dev instance starts |
| 6:00 PM CST | 23:00 UTC | Dev instance stops |

When the Dev instance is stopped, the WordPress site is completely inaccessible — anyone trying to visit the URL will see a connection error until 9 AM the next day.

---

## Monitoring

CloudWatch alarms are automatically configured by the CloudFormation template:

| Alarm | Threshold | Action |
|---|---|---|
| CPU Utilization | > 80% for 10 mins | SNS email alert |
| Status Check Failed | >= 1 failure | SNS email alert |

To receive alerts, confirm the subscription email sent by AWS SNS to your inbox.

---

## Live vs Dev Environment

| Feature | Live | Dev |
|---|---|---|
| Always available | ✅ Yes | ❌ No |
| Business hours only | ❌ No | ✅ Yes (9AM-6PM) |
| Purpose | Public blog | Testing only |
| Auto start/stop | ❌ No | ✅ Yes |
| Cost | 24/7 | 9 hrs/day only |

---

## Real-World Scenario

This project simulates a real company setup where:
- The **Live** site serves as the public-facing blog that customers and readers can access anytime
- The **Dev** site is used by developers to test changes before pushing them to the live blog
- The Dev site is only available during business hours to save costs and improve security
- CloudWatch monitoring ensures the team is alerted immediately if anything goes wrong

---

## Author

Alex Moise 
Course-end project — AWS CloudFormation & WordPress Deployment
