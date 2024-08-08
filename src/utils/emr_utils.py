import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from a .env file
load_dotenv()

# Configure environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'fakemykeyid')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'fakemysecretaccesskey')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', 'fakemysessiontoken')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Initialize the EMR client
emr_client = boto3.client(
    'emr',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

def handle_client_error(error, action, resource_name):
    print(f"Error while {action} {resource_name}: {error.response['Error']['Message']}")

def create_emr_cluster(name, release_label, instance_type, instance_count, log_uri):
    try:
        response = emr_client.run_job_flow(
            Name=name,
            LogUri=log_uri,
            ReleaseLabel=release_label,
            Instances={
                'InstanceGroups': [
                    {
                        'Name': 'Master nodes',
                        'InstanceRole': 'MASTER',
                        'InstanceType': instance_type,
                        'InstanceCount': 1,
                    },
                    {
                        'Name': 'Core nodes',
                        'InstanceRole': 'CORE',
                        'InstanceType': instance_type,
                        'InstanceCount': instance_count - 1,
                    }
                ],
                'Ec2KeyName': 'your-ec2-key-name',  # Replace with your actual EC2 key name
                'KeepJobFlowAliveWhenNoSteps': True,
                'TerminationProtected': False,
            },
            Applications=[{'Name': 'Hadoop'}, {'Name': 'Spark'}],
            JobFlowRole='EMR_EC2_DefaultRole',
            ServiceRole='EMR_DefaultRole'
        )
        return response['JobFlowId']
    except ClientError as e:
        handle_client_error(e, "create EMR cluster", name)
        return None

def terminate_emr_cluster(cluster_id):
    try:
        response = emr_client.terminate_job_flows(JobFlowIds=[cluster_id])
        return response
    except ClientError as e:
        handle_client_error(e, "terminate EMR cluster", cluster_id)
        return None

def list_emr_clusters():
    try:
        response = emr_client.list_clusters(ClusterStates=['STARTING', 'BOOTSTRAPPING', 'RUNNING', 'WAITING'])
        return response['Clusters']
    except ClientError as e:
        handle_client_error(e, "list EMR clusters", "")
        return []

def describe_emr_cluster(cluster_id):
    try:
        response = emr_client.describe_cluster(ClusterId=cluster_id)
        return response['Cluster']
    except ClientError as e:
        handle_client_error(e, "describe EMR cluster", cluster_id)
        return None

def add_step_to_emr_cluster(cluster_id, name, action_on_failure, hadoop_jar_step):
    try:
        response = emr_client.add_job_flow_steps(
            JobFlowId=cluster_id,
            Steps=[
                {
                    'Name': name,
                    'ActionOnFailure': action_on_failure,
                    'HadoopJarStep': hadoop_jar_step
                }
            ]
        )
        return response['StepIds']
    except ClientError as e:
        handle_client_error(e, "add step to EMR cluster", cluster_id)
        return None

def describe_emr_steps(cluster_id, step_ids):
    try:
        response = emr_client.describe_step(JobFlowId=cluster_id, StepId=step_ids)
        return response['Step']
    except ClientError as e:
        handle_client_error(e, "describe EMR step", step_ids)
        return None

def list_emr_steps(cluster_id):
    try:
        response = emr_client.list_steps(ClusterId=cluster_id)
        return response['Steps']
    except ClientError as e:
        handle_client_error(e, "list steps of EMR cluster", cluster_id)
        return []

def main():
    # Create an EMR cluster
    cluster_id = create_emr_cluster("TestCluster", "emr-6.2.0", "m5.xlarge", 3, "s3://your-log-uri/")
    if cluster_id:
        print(f"EMR Cluster created with ID: {cluster_id}")
        
        # List EMR clusters
        clusters = list_emr_clusters()
        print(f"Active EMR Clusters: {clusters}")

        # Describe the created cluster
        cluster_description = describe_emr_cluster(cluster_id)
        print(f"Cluster Description: {cluster_description}")

        # Add a step to the cluster
        step_ids = add_step_to_emr_cluster(cluster_id, "SampleStep", "TERMINATE_CLUSTER", {
            'Jar': 'command-runner.jar',
            'Args': ['spark-submit', '--deploy-mode', 'cluster', 's3://your-script-location/your-script.py']
        })
        if step_ids:
            print(f"Added steps: {step_ids}")

            # Describe the added steps
            step_description = describe_emr_steps(cluster_id, step_ids[0])
            print(f"Step Description: {step_description}")

            # List steps of the cluster
            steps = list_emr_steps(cluster_id)
            print(f"Steps in Cluster {cluster_id}: {steps}")

        # Terminate the cluster
        terminate_response = terminate_emr_cluster(cluster_id)
        if terminate_response:
            print(f"Terminated EMR Cluster with ID: {cluster_id}")

if __name__ == "__main__":
    main()
