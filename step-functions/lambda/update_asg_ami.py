###############################################################################################################
#
# update_asg_ami.py
#
# Description:
#  This uses "case" logic to comminucate back and forth with the step function (stacks/stepfunc_stack.py)
#
# Steps:
#  - 1. Yum Upate   
#  - 2. Checker to determine if Yum has finished (and the instnace has stopped)
#  - 3. AMI Creation 
#  - 4. Checker to determine if AMI has finished creating
#  - 5. Update both the EC2 and ALB CloudFormation Stacks and
#       update the Config Rule with the AMI ID created in step 3 
#
# Returns:
#  event Json Object
#  (or an error on line 143 which will stop the step function)
# 
###############################################################################################################

import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
  #testing_flag
  skip_ami=0

  # declare boto3 clients
  ec2_client=boto3.client('ec2')
  ssm_client=boto3.client('ssm')
  config_client=boto3.client('config')

  # Store even Payload as "event"
  event=event['Payload']

  # *** change this to match vars.py, if needed ***
  ami_param_path="/project/amiid/ami-auto-replace"
  config_rule_name="my-amiid-config-rule"

  # create local variables from event
  print(event)
  step=event['step']
  img_name=event['img_project_name']
  alb_name=event['alb_project_name']

  #get instance id of imaging server (if the terminated one has not disappears remove the tags)
  response = ec2_client.describe_instances(Filters=[
        {'Name': 'tag:Project','Values':[img_name]},
        {'Name': 'tag:Type','Values':['imaging_server']}
      ])
  
  #print(response)
  instance_id=response['Reservations'][0]['Instances'][0]['InstanceId']
  print(instance_id)

  # Determine which section to run, based on position in Step Function
  if step==1:
    #run yum update
    print("Begin Step 1")
    #next step
    event['step']=2
    #event['status']="Worked"
    # update kernel

    date_str=datetime.now().strftime("%Y-%m-%d-%M")

    #run yum update using ssm commnad
    response = ssm_client.send_command(
      Targets=[
          {
            'Key': 'tag:OS',
            'Values': [
               "linux",
            ]
          },
          {
            'Key': 'tag:ServerGroup',
            'Values': [
               "production",
            ]
          },
        ],
      DocumentName='AWS-RunShellScript',
      DocumentVersion='1',
      TimeoutSeconds=600,
      Parameters={
        'workingDirectory': [
          "",
        ],
        'executionTimeout': [
          "3600",
        ],
        'commands': [
          "echo "+date_str+"\" yum update by systems manager\" >>/root/message.txt",
          "cat /root/message.txt",
          "yum -y update",
          "sleep 30",
          "shutdown -h +1;echo $?"
        ],
      },
      MaxErrors='0',
    )
    
    print(response)
    
  if step==2:
    #check that yum finished and instance is halted
    #keep next step at 2 until instance is confirmed stopped
    event['step']=2
    print("Begin Step 2")
    
    response = ec2_client.describe_instances(
      InstanceIds=[
        instance_id,
      ],
    )
      
    state=response['Reservations'][0]['Instances'][0]['State']['Name']

    # if not stopped step fuction will wait then retry this section
    if state!='stopped':
      print("yum still running")
      event['status']="Retry" 
    else:
      print("yum finished")
      event['step']=3
      event['status']="Worked"
      
  if step==3:
    # start AMI creation
    event['step']=4
    print("Begin Step 3")
    
    #make sure ami is not running already
    ami_is_running=ec2_client.describe_images(Filters=[{'Name': 'tag:Name','Values': [img_name]},{'Name': 'state','Values': ['pending']}],Owners=['self'])['Images']
    print(ami_is_running)
    print(len(ami_is_running))
    
    if ami_is_running:
      print("This AMI is still creating, do not restart the process")
      return "ERROR: script run twice before completion of first run"
    else:
      #create ami 
      date_str=datetime.now().strftime("%Y-%m-%d-%M")

      ami_name=img_name+"-"+date_str

      print(ami_name)
      print("Start AMI creation")

      if skip_ami==0:
        ami_id=response = ec2_client.create_image(
          InstanceId=instance_id,
          NoReboot=True,
          Name=ami_name
        )['ImageId']
        print(ami_id)

        event['ami_id']=ami_id
        
        #update ssm ami-id parameter
        response = ssm_client.put_parameter(
          Name=ami_param_path,
          Type='String',
          Value=ami_id,
          Overwrite=True,
          #DataType="aws:ec2:image"
        )
        print(response)

  if step==4:
    # check that ami creation finished before continuing
    # keep next step at 4 until ami is confirmed completed
    event['step']=4
    print("Begin Step 4")
    #check ami status
    ami_id=event['ami_id']
    ami_status=ec2_client.describe_images(ImageIds=[ami_id])['Images'][0]['State']
    
    if ami_status=='available':
      event['status']="Worked"
      #next step
      event['step']=5
    else:
      event['status']="Retry"
      
  if step==5:
    # update CloudFormation Stacks
    print("Begin Step 5")

    event['status']="Finished"
    
    #update ALB CF Stack with new AMI
    ami_id=event['ami_id']
    
    #stack_name=event['cf_stack_name']
    stack_name=alb_name+"-alb"
    cf_client = boto3.client('cloudformation')
    
    response = cf_client.update_stack(
      StackName=stack_name,
      UsePreviousTemplate=True,
      Capabilities=['CAPABILITY_NAMED_IAM']
    )
    print(response)
    
    # update imaging server CF Stack
    response = cf_client.update_stack(
      StackName=img_name+"-ec2",
      UsePreviousTemplate=True,
      Capabilities=['CAPABILITY_NAMED_IAM']
    )
    print(response)
    
    # update ami in config rule
    response = config_client.put_config_rule(
      ConfigRule={
        'ConfigRuleName': config_rule_name,
        'Scope': {
          'TagKey': 'ami_id_parameter',
          'TagValue': ami_param_path,
        },
        'Source': {
          'Owner': 'AWS',
          'SourceIdentifier': 'APPROVED_AMIS_BY_ID',
        },
        'InputParameters': '{"amiIds": \"'+ami_id+'\"}',
      }
    )
    print(response)
    
  return event
