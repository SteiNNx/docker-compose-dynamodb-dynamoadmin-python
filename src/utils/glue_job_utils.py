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

# Initialize the Glue client
glue_client = boto3.client(
    'glue',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

def create_glue_job(job_name, role, script_location):
    """
    Create a Glue job.

    Parameters:
    - job_name (str): The name of the Glue job.
    - role (str): The IAM role used by the Glue job.
    - script_location (str): The S3 path to the Glue script.

    Returns:
    - dict: The response from the create job request or None if an error occurred.
    """
    try:
        response = glue_client.create_job(
            Name=job_name,
            Role=role,
            Command={
                'Name': 'glueetl',
                'ScriptLocation': script_location
            }
        )
        return response
    except ClientError as e:
        print(f"Error while creating Glue job {job_name}: {e.response['Error']['Message']}")
        return None

def start_glue_job(job_name, arguments={}):
    """
    Start a Glue job.

    Parameters:
    - job_name (str): The name of the Glue job to start.
    - arguments (dict): Additional arguments for the Glue job run.

    Returns:
    - str: The job run ID of the started job or None if an error occurred.
    """
    try:
        response = glue_client.start_job_run(JobName=job_name, Arguments=arguments)
        return response['JobRunId']
    except ClientError as e:
        print(f"Error while starting Glue job {job_name}: {e.response['Error']['Message']}")
        return None

def get_job_run_status(job_name, job_run_id):
    """
    Get the status of a Glue job run.

    Parameters:
    - job_name (str): The name of the Glue job.
    - job_run_id (str): The ID of the job run to check the status.

    Returns:
    - str: The state of the job run or None if an error occurred.
    """
    try:
        response = glue_client.get_job_run(JobName=job_name, RunId=job_run_id)
        return response['JobRun']['JobRunState']
    except ClientError as e:
        print(f"Error while getting the status of Glue job {job_name} (RunId: {job_run_id}): {e.response['Error']['Message']}")
        return None

def describe_glue_job(job_name):
    """
    Describe a Glue job.

    Parameters:
    - job_name (str): The name of the Glue job to describe.

    Returns:
    - dict: The job description or None if an error occurred.
    """
    try:
        response = glue_client.get_job(JobName=job_name)
        return response['Job']
    except ClientError as e:
        print(f"Error while describing Glue job {job_name}: {e.response['Error']['Message']}")
        return None

def list_glue_jobs():
    """
    List all Glue jobs.

    Returns:
    - list: A list of Glue job names or an empty list if an error occurred.
    """
    try:
        response = glue_client.list_jobs()
        return response['JobNames']
    except ClientError as e:
        print(f"Error while listing Glue jobs: {e.response['Error']['Message']}")
        return []

def stop_glue_job_run(job_name, job_run_id):
    """
    Stop a running Glue job.

    Parameters:
    - job_name (str): The name of the Glue job.
    - job_run_id (str): The ID of the job run to stop.

    Returns:
    - dict: The response from the stop request or None if an error occurred.
    """
    try:
        response = glue_client.batch_stop_job_run(
            JobName=job_name,
            JobRunIds=[job_run_id]
        )
        return response
    except ClientError as e:
        print(f"Error while stopping Glue job {job_name} (RunId: {job_run_id}): {e.response['Error']['Message']}")
        return None

def list_glue_job_runs(job_name):
    """
    List the runs of a Glue job.

    Parameters:
    - job_name (str): The name of the Glue job.

    Returns:
    - list: A list of job run details or an empty list if an error occurred.
    """
    try:
        response = glue_client.get_job_runs(JobName=job_name)
        return response['JobRuns']
    except ClientError as e:
        print(f"Error while listing runs of Glue job {job_name}: {e.response['Error']['Message']}")
        return []

def main():
    # Define job parameters
    job_name = "example-glue-job"
    role = "arn:aws:iam::123456789012:role/GlueRole"  # Replace with your IAM role
    script_location = "s3://your-bucket/scripts/glue_script.py"  # Replace with your S3 script location

    # Create a Glue job
    print("Creating Glue job...")
    create_response = create_glue_job(job_name, role, script_location)
    print(f"Create job response: {create_response}")

    # List Glue jobs
    print("Listing Glue jobs...")
    jobs = list_glue_jobs()
    print(f"Glue jobs: {jobs}")

    # Start the Glue job
    print("Starting Glue job...")
    job_run_id = start_glue_job(job_name)
    print(f"Started job run ID: {job_run_id}")

    # Get job run status
    print("Checking job run status...")
    if job_run_id:
        status = get_job_run_status(job_name, job_run_id)
        print(f"Job run status: {status}")

    # Describe the Glue job
    print("Describing Glue job...")
    job_description = describe_glue_job(job_name)
    print(f"Job description: {job_description}")

    # List job runs
    print("Listing job runs...")
    job_runs = list_glue_job_runs(job_name)
    print(f"Job runs: {job_runs}")

    # Stop the job run
    print("Stopping job run...")
    stop_response = stop_glue_job_run(job_name, job_run_id)
    print(f"Stop job run response: {stop_response}")

if __name__ == "__main__":
    main()
