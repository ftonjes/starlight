from botocore.exceptions import BotoCoreError
from lib.core_utilities import parse_configuration, get_key
import boto3
import json


class Boto3STSService(object):

    def __init__(self, arn):

        # Get credentials so we can assume the role and query information for the ARN:
        sess = boto3.session.Session(
            aws_access_key_id=get_key('AWS_IPFABRIC_AKI'),
            aws_secret_access_key=get_key('AWS_IPFABRIC_SEC'))

        sts_connection = sess.client('sts')
        assume_role_object = sts_connection.assume_role(
            RoleArn=arn, RoleSessionName=get_key('AWS_IPFABRIC_USERNAME'),
            DurationSeconds=3600)

        self.credentials = assume_role_object['Credentials']


def get_boto3_session(credentials):

    # Set up Boto3 session to AWS:
    tmp_access_key = credentials['AccessKeyId']
    tmp_secret_key = credentials['SecretAccessKey']
    security_token = credentials['SessionToken']

    boto3_session = boto3.session.Session(
        aws_access_key_id=tmp_access_key,
        aws_secret_access_key=tmp_secret_key, aws_session_token=security_token
    )
    return boto3_session


def test_arn_access(arn_string):

    # Set up session:
    try:
        # Get credential info for session so we can assume role for ARN:
        creds = Boto3STSService(arn_string).credentials
        # Create AWS session:
        sess = get_boto3_session(creds)
    except (BotoCoreError, Exception) as err:
        return False, err

    # Set up session for EC2 information
    try:
        resource = sess.client('ec2')
    except (BotoCoreError, Exception) as err:
        return False, err

    # Get specific EC2-related info:
    result = resource.describe_vpcs()['Vpcs']

    return True, result
