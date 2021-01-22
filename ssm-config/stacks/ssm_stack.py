##############################################################
#
# ssm_stack.py
#
# Resources:
#   SSM Parameter for AMI Path (string)
#
##############################################################

from aws_cdk import (
  aws_ssm as ssm,
  core
)

import boto3

class SSMStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, env, vars, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    ssm_client = boto3.client('ssm')

    # Get *AWS created* parameter for the latest Amazon Linux 2 AMI ID
    # This parameter is NOT specific to your AWS account 
    # Or replace /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 in the vars file with your own parameter path
    ami_id_param=vars['ssm_initial_ami']
    response = ssm_client.get_parameter(
      Name=ami_id_param
    )
    ami_id=response['Parameter']['Value']

    # Create the string parameter for the project to use the Amazon Linux 2 AMI ID as the starting value
    ssm.StringParameter(self,"Linux Prod AMI ID",
      parameter_name=vars['ami_param'],
      string_value=ami_id
    )