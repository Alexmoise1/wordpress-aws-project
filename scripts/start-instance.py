import boto3

# -------------------------------------------------------
# start-instance.py
# This script is used by AWS Lambda to START the dev
# WordPress instance at 9 AM every weekday.
# -------------------------------------------------------

# IMPORTANT: Replace this with your actual Dev Instance ID
# You can find it in the CloudFormation Outputs after deploying
INSTANCE_ID = "i-XXXXXXXXXXXXXXXXX"  # <-- Replace this
REGION = "us-east-1"                  # <-- Replace with your region

def lambda_handler(event, context):
    """
    Lambda function to start the WordPress dev EC2 instance.
    Triggered by EventBridge at 9 AM daily.
    """
    ec2 = boto3.client("ec2", region_name=REGION)

    try:
        # Start the instance
        response = ec2.start_instances(InstanceIds=[INSTANCE_ID])

        # Get the current state
        current_state = response["StartingInstances"][0]["CurrentState"]["Name"]
        previous_state = response["StartingInstances"][0]["PreviousState"]["Name"]

        print(f"Instance {INSTANCE_ID} state changed: {previous_state} -> {current_state}")

        return {
            "statusCode": 200,
            "body": f"Successfully started instance {INSTANCE_ID}. State: {current_state}"
        }

    except Exception as e:
        print(f"Error starting instance: {str(e)}")
        return {
            "statusCode": 500,
            "body": f"Error starting instance: {str(e)}"
        }
