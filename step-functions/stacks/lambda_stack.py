##############################################################
#
# lambda_stack.py
#
# Resources:
#  1 lambda functions (code in /lambda folder (from_asset))
#
# Exports:
#  update_asg_ami_func (Lambda IFunction)
#
# Imports:
#  update_ami_lambda_role (IAM IRole)
#
##############################################################

from aws_cdk import (
  aws_iam as iam,
  aws_lambda as lambda_,
  core
)

class LambdaStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, update_ami_lambda_role: iam.IRole, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # create the Lambda function
    # create new zip file if changing related .py file
    self._update_asg_ami_func=lambda_.Function(self,"Update ASG AMI Lambda Func",
      code=lambda_.Code.from_asset("lambda/update_asg_ami.zip"),
      handler="update_asg_ami.lambda_handler",
      runtime=lambda_.Runtime.PYTHON_3_8,
      role=update_ami_lambda_role,
      timeout=core.Duration.seconds(60)     
    )

  # Exports
  @property
  def update_asg_ami_func(self) -> str:
    return self._update_asg_ami_func
