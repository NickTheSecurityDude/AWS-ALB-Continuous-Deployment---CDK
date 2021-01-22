#!/usr/bin/env python3

##################################################################
#
# app.py - STACKS
# 
# 1. SSM
# 2. Config
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

sys.path.append("..")
import vars

#if region != 'us-east-1':
#  print("This app may only be run from us-east-1")
#  sys.exit()

account_id = client.get_caller_identity()["Account"]

my_env = {'region': region, 'account': account_id}

from stacks.ssm_stack import SSMStack
from stacks.config_stack import ConfigStack

# Get sub project name from vars file
proj_name=vars.project_vars['config_stack_name']

app = core.App()

ssm_stack=SSMStack(app, proj_name+"-ssm",env=my_env,vars=vars.project_vars)
config_stack=ConfigStack(app,proj_name+"-config",vars=vars.project_vars)

# Tag all resources
for stack in [ssm_stack,config_stack]:
  core.Tags.of(stack).add("Project", proj_name)
  core.Tags.of(stack).add("ProjectGroup", vars.project_vars['group_proj_name'])

app.synth()
