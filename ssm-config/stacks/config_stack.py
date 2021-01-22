##############################################################
#
# config_stack.py
#
# Resources:
#  "APPROVED_AMIS_BY_ID" config rule
#
##############################################################

from aws_cdk import (
  aws_config as config,
  core
)

import boto3

class ConfigStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, vars, **kwargs) -> None:
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

    # Create managed config rule to check that instances are running an approved AMI
    # The scope is set by the "ami_param" path in the vars.py file
    config.ManagedRule(self,"Config AMI Rule",
      identifier="APPROVED_AMIS_BY_ID",
      config_rule_name=vars['config_rule_name'],
      input_parameters={'amiIds':ami_id},
      rule_scope=config.RuleScope.from_tag(
        key='ami_id_parameter',
        value=vars['ami_param']
      )

    )
    
