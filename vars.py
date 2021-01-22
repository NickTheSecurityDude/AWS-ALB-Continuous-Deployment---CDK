#
# Enter parameter name (full path) on line 15 in and the config rule name on line 16:
# step-functions/lambda/update_asg_ami.py
# and zip file, from lambda/ run:
# zip update_asg_ami.zip update_asg_ami.py
# ex. 
# /project/amiid/ami-auto-replace
# my-amiid-config-rule

group_proj_name="ami-auto-replace"

project_vars={
  "group_proj_name": group_proj_name,
  "ami_param": "/project/amiid/"+group_proj_name,
  "ec2_mng_name": "Linux-Prod-Imaging-Server",
  "ssm_initial_ami": "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2",
  "config_rule_name": "my-amiid-config-rule",
  "imaging_stack_name": "linprod-mngsrv",
  "alb_stack_name":"website1-alb",
  "config_stack_name": "ssm-config",
  "step_func_stack_name": "update-ami-sf",
  "alb_role": "ALBEC2Role",
  "imaging_role": "ImagingEC2Role",
  "ec2_key_pair": "alb-key",
  "config_rule_name": "my-amiid-config-rule"
}
