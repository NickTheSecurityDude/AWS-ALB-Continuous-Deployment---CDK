#!/usr/bin/env python3

##################################################################
#
# app.py - STACKS
# 
# 1. IAM
# 2. Lambda
# 3. Step Functions
#
# Requires:
# ../vars.py
#
# Notes:
#  bootstrap one for project root
#  cdk bootstrap aws://<account-id>/<region>
#
###################################################################

from aws_cdk import core

import boto3
import sys

client = boto3.client('sts')

region=client.meta.region_name
account_id = client.get_caller_identity()["Account"]

# import common vars file
sys.path.append("..")
import vars

#if region != 'us-east-1':
#  print("This app may only be run from us-east-1")
#  sys.exit()

my_env = {'region': region, 'account': account_id}
 
from stacks.iam_stack import IAMStack
from stacks.lambda_stack import LambdaStack
from stacks.stepfunc_stack import StepFuncStack

# Get sub project name from vars file
proj_name=vars.project_vars['step_func_stack_name']

app = core.App()

iam_stack=IAMStack(app, proj_name+"-iam",proj=proj_name,env=my_env,vars=vars.project_vars)
lambda_stack=LambdaStack(app, proj_name+"-lambda",update_ami_lambda_role=iam_stack.update_ami_lambda_role)
stepfunc_stack=StepFuncStack(app, proj_name+"-stepfunc",
  update_asg_ami_func=lambda_stack.update_asg_ami_func,
  env=my_env
)

# Tag all resources
for stack in [iam_stack,lambda_stack,stepfunc_stack]:
  core.Tags.of(stack).add("Project", proj_name)
  core.Tags.of(stack).add("ProjectGroup", vars.project_vars['group_proj_name'])

app.synth()
