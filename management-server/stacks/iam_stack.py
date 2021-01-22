##############################################################
#
# iam_stack.py
#
# Resources:
#  Imaging EC2 Instance Role
#   - 1 managed policy   
#
# Exports:
#  imaging_ec2_role (IRole)
#
##############################################################

from aws_cdk import (
  aws_iam as iam,
  core
)

class IAMStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, env, vars, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # Create the imaging EC2 Role
    self._imaging_ec2_role=iam.Role(self,"Imaging EC2 Role",
      role_name=vars['imaging_role'],
      assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
      managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore')
      ]
    )

  # Exports
  @property
  def imaging_ec2_role(self) -> iam.IRole:
    return self._imaging_ec2_role
