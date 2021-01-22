#!/usr/bin/env python3

##################################################################
#
# app.py - STACKS
# 
# 1. IAM
# 2. SG
# 3. ALB
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

sys.path.append("..")
import vars
#print(vars.project_vars)

region=client.meta.region_name

#if region != 'us-east-1':
#  print("This app may only be run from us-east-1")
#  sys.exit()

account_id = client.get_caller_identity()["Account"]

my_env = {'region': region, 'account': account_id}

from stacks.iam_stack import IAMStack
from stacks.sg_stack import SGStack
from stacks.alb_stack import ALBStack

# Get sub project name from vars file
proj_name=vars.project_vars['alb_stack_name']

app = core.App()

iam_stack=IAMStack(app, proj_name+"-iam",env=my_env,vars=vars.project_vars)
sg_stack=SGStack(app, proj_name+"-sg",env=my_env)
alb_stack=ALBStack(app, proj_name+"-alb",
  alb_sg=sg_stack.alb_sg,
  alb_ec2_role=iam_stack.alb_ec2_role,
  vars=vars.project_vars,
  env=my_env
)

# Tag all resources
for stack in [iam_stack,sg_stack,alb_stack]:
  core.Tags.of(stack).add("Project", proj_name)
  core.Tags.of(stack).add("ProjectGroup", vars.project_vars['group_proj_name'])



app.synth()
