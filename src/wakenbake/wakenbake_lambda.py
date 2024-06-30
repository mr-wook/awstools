if True:
    import boto3
    import json

def lambda_handler(event, context):
    """
    Updates Route 53 host records for an EC2 instance based on information in an S3 file.

    Args:
        event (dict): Lambda event object
        context (object): Lambda context object

    Returns:
        dict: Dictionary containing a message about the update status.
    """

    # Get S3 bucket and key names from environment variables
    s3_bucket = os.environ['S3_BUCKET']
    s3_key = os.environ['S3_KEY']

    # Get boto3 clients
    s3_client = boto3.client('s3')
    route53_client = boto3.client('route53')

    # Download data from S3
    try:
        response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        data = response['Body'].read().decode('utf-8')
        instance_data = json.loads(data)
    except Exception as e:
        return { 'message': f"Error retrieving data from S3: {str(e)}" }

    # Extract instance ID and hostname from S3 data
    instance_id = instance_data.get('InstanceId')
    hostname = instance_data.get('Hostname')

    # Get public IP address of the instance
    try:
        ec2_client = boto3.client('ec2')
        public_ip = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]['PublicIpAddress']
    except Exception as e:
        return { 'message': f"Error getting instance public IP: {str(e)}" }

    # Update Route 53 record (replace with your actual hosted zone ID)
    hosted_zone_id = 'YOUR_HOSTED_ZONE_ID'
    try:
        route53_client.change_resource_record_sets(
          HostedZoneId=hosted_zone_id,
          ChangeBatch={
            'Changes': [
              {
                'Action': 'UPSERT',  # Update or create the record
                'ResourceRecordSet': {
                  'Name': hostname,
                  'Type': 'A',
                  'TTL': 300,
                  'ResourceRecords': [
                    {'Value': public_ip}
                  ]
                }
              }
            ]
          }
        )
      return { 'message': f"Route 53 record for {hostname} updated with IP {public_ip}" }
    except Exception as e:
      return { 'message': f"Error updating Route 53 record: {str(e)}" }

    # Set environment variables (update with your actual values)
    os.environ['S3_BUCKET'] = 'your-s3-bucket-name'
    os.environ['S3_KEY'] = 'your-s3-file-key'

"""
Explanation:
* Imports: Import boto3 for interacting with AWS services and json for working with JSON data.
* Lambda Handler: The lambda_handler function is the entry point for the Lambda.
* Environment Variables:
   * The Lambda should have environment variables set for:
     * S3_BUCKET: The name of the S3 bucket containing the data file.
     * S3_KEY: The key (filename) of the data file within the S3 bucket.
* Boto3 Clients: Create boto3 clients for interacting with S3 (s3_client) and Route 53 (route53_client).
* Download S3 Data:
   * Retrieve the data from the S3 file using get_object and decode it as UTF-8.
   * Handle potential exceptions during download.
* Extract Data:
   * Parse the downloaded JSON data to extract InstanceId and Hostname.
* Get Public IP:
   * Use the ec2_client to describe the EC2 instance and retrieve its public IP address.
   * Handle potential exceptions during retrieval.
* Update Route 53 Record:
   * Specify your Route 53 Hosted Zone ID (YOUR_HOSTED_ZONE_ID).
   * Use `

Two files on s3:
Instances.tbl:
    <instance-name>[/rectype:{A,AAAA,?CNAME?}] <public hostnames> [<private hostnames>]

Weirdos.tbl
    # User, Encrypted PW, list of hosts this user can wake-n-bake;
   <username> <encrypted-pw> host,host,host...
"""
