import boto3
import json

aws_region = 'eu-north-1'


def get_instances(ec2_client):

    custom_filter = [{'Name':'tag:Name','Values': ['staging-yogobe-ec2-autoscaling-instance']},
                    {'Name': 'instance-state-name', 'Values': ['running']}]

    instances = []
    ec2_instance_response = ec2_client.describe_instances(Filters=custom_filter)
    for reservation in ec2_instance_response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])

    return instances

def submit_ssm_command(instances, document_name, ssm_client):
    try: 
        response = ssm_client.send_command(
            InstanceIds = instances,
            DocumentName = document_name,
            DocumentVersion = '$LATEST'
        )
        command_id = response['Command']['CommandId']
    except ClientError as e:
        print("Unexpected error when submitting SSM command: "+ e.response['Error']['Code'])
    
    return command_id

def quiet_workers(instances, ssm_client):
    return submit_ssm_command(instances, 'quiet_sidekiq', ssm_client)

def wake_workers(instances, ssm_client):
    return submit_ssm_command(instances, 'wake_sidekiq', ssm_client)


ec2_client = boto3.client('ec2', region_name=aws_region)
ssm_client = boto3.client('ssm', region_name=aws_region)

### Main Line ###

instances = get_instances(ec2_client)
print(quiet_workers(instances, ssm_client))

