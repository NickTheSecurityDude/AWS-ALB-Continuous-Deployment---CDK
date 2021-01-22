##############################################################
#
# iam_stack.py
#
# Resources:
#   IAM Policy (this will be an inline policy)
#    - 1 policy document
#   Update AMI Lambda Role
#    - 2 inline policy, 1 managed policies   
#
# Exports:
#  update_ami_lambda_role (IRole)
#
##############################################################

from aws_cdk import (
  aws_iam as iam,
  core
)

import boto3

class IAMStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, proj, env, vars, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # Get config arn from boto3
    config_rule_name=vars['config_rule_name']

    config_client=boto3.client('config')

    response=config_client.describe_config_rules(
      ConfigRuleNames=[config_rule_name],
    )

    config_arn=response['ConfigRules'][0]['ConfigRuleArn']

    acct_id=env['account']
    region=env['region']

    # Create IAM Policy Document, granual IAM policy using least privilege
    self._iam_ami_lambda_policy_doc=iam.PolicyDocument(
      statements=[
        # SSM  Get/Put
        # arn resource
        iam.PolicyStatement(
          actions=[
            "ssm:GetParameter*",
            "ssm:PutParameter"
          ],
          effect=iam.Effect.ALLOW,
          resources=['arn:aws:ssm:'+region+':'+acct_id+':parameter'+vars['ami_param']]
        ),
        # SSM  Send Command
        # one statement for document, one statement for tag condition
        iam.PolicyStatement(
          actions=[
            "ssm:SendCommand"
          ],
          effect=iam.Effect.ALLOW,
          resources=['arn:aws:ec2:'+region+':'+acct_id+':instance/*'],
          conditions={
            "StringEquals": {"aws:ResourceTag/Name": vars['ec2_mng_name']}
          }
        ),
        iam.PolicyStatement(
          actions=[
            "ssm:SendCommand"
          ],
          effect=iam.Effect.ALLOW,
          resources=['arn:aws:ssm:*:*:document/AWS-RunShellScript']
        ),
        # EC2 Describe
        # describes do not allow resources, use *
        # use Describe* to help stay within policy char limit
        # elasticloadbalancingv2 is actually elasticloadbalancing (no v2)
        iam.PolicyStatement(
          actions=[
            "ec2:Describe*",
            "autoscaling:Describe*",
            "elasticloadbalancing:Describe*"
          ],
          effect=iam.Effect.ALLOW,
          resources=['*']
        ),   
        # EC2 Create Image / update ec2 stack
        # tag condition
        iam.PolicyStatement(
          actions=[
            "ec2:CreateImage",
            "ec2:associateAddress",
            "ec2:TerminateInstances"
          ],
          effect=iam.Effect.ALLOW,
          resources=['arn:aws:ec2:'+region+':'+acct_id+':instance/*'],
          conditions={
            "StringEquals": {"ec2:ResourceTag/Name": vars['ec2_mng_name']}
          }
        ), 
        # Create Image also needs permissions the ::image/* resource without a tag
        iam.PolicyStatement(
          actions=[
            "ec2:CreateImage"
          ],
          effect=iam.Effect.ALLOW,
          resources=['arn:aws:ec2:'+region+'::image/*']
        ),
        # CloudFormation "Runs" the instance before adding tags so restrict by instance profile
        iam.PolicyStatement(
          actions=[
            "ec2:RunInstances"
          ],
          effect=iam.Effect.ALLOW,
          resources=[
            'arn:aws:ec2:'+region+':'+acct_id+':instance/*',
            'arn:aws:ec2:'+region+':'+acct_id+':network-interface/*',
            'arn:aws:ec2:'+region+'::image/ami-*',
            'arn:aws:ec2:'+region+':'+acct_id+':key-pair/*',
            'arn:aws:ec2:'+region+':'+acct_id+':security-group/*',
            'arn:aws:ec2:'+region+':'+acct_id+':subnet/*',
            'arn:aws:ec2:'+region+':'+acct_id+':volume/*'
          ],
          conditions={
            "StringLikeIfExists": {
              "ec2:InstanceProfile": "arn:aws:iam::"+acct_id+":instance-profile/"+vars['imaging_stack_name']+"-ec2-ec2instanceInstanceProfile????????-?????????????"
            }
          }
        ),              
        # EC2 Create Tag, only allow on RunInstances
        iam.PolicyStatement(
          actions=[
            "ec2:CreateTags"
          ],
          effect=iam.Effect.ALLOW,
          resources=['arn:aws:ec2:'+region+':'+acct_id+':instance/*'],
          conditions={
            "StringEquals": {
              "ec2:CreateAction": "RunInstances"
            }
          }
        ),    
        # Auto-Scaling / Launch Config / update alb stack
        iam.PolicyStatement(
          actions=[
            "autoscaling:*"
          ],
          effect=iam.Effect.ALLOW,
          resources=[
                'arn:aws:autoscaling:'+region+':'+acct_id+':autoScalingGroup:*:autoScalingGroupName/'+vars['alb_stack_name']+'-alb-myASG*',
                'arn:aws:autoscaling:'+region+':'+acct_id+':launchConfiguration:*:launchConfigurationName/'+vars['alb_stack_name']+'-alb-myASGLaunchConfig*'
          ]
        ),  
        # Allow update to Config Rule
        # use arn
        iam.PolicyStatement(
          actions=[
            "config:PutConfigRule"
          ],
          effect=iam.Effect.ALLOW,
          resources=[config_arn]
        ),  
        # CloudFormation
        iam.PolicyStatement(
          actions=[
            "cloudformation:UpdateStack"
          ],
          effect=iam.Effect.ALLOW,
          resources=[
            'arn:aws:cloudformation:'+region+':'+acct_id+':stack/'+vars['alb_stack_name']+'-alb/*',
            'arn:aws:cloudformation:'+region+':'+acct_id+':stack/'+vars['imaging_stack_name']+'-ec2/*'
            ]
        ),
      ]
    )

    # Create a policy from the policy document
    self._iam_ami_lambda_policy=iam.Policy(self,"AMI Lambda IAM Policy",
      document=self._iam_ami_lambda_policy_doc
    )

    # Create the lambda IAM Role
    self._update_ami_lambda_role=iam.Role(self,"Update AMI Lambda Role",
      role_name=proj+"_lambda_role",
      assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
      inline_policies=[iam.PolicyDocument(
        statements=[iam.PolicyStatement(
          actions=["iam:PassRole"],
          effect=iam.Effect.ALLOW,
          resources=[
            "arn:aws:iam::"+acct_id+":role/"+vars['alb_role'],
            "arn:aws:iam::"+acct_id+":role/"+vars['imaging_role']
          ]
        )]
      )],
      managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')  
      ]
    )

    # add policy created above to role
    self._iam_ami_lambda_policy.attach_to_role(self._update_ami_lambda_role)

  # Exports
  @property
  def update_ami_lambda_role(self) -> iam.IRole:
    return self._update_ami_lambda_role


