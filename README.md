# Install Guide

## Instructions
Enter variables in vars.py
(including SSH Keypair name)

Enter parameter name (path) on line 15 in and the config rule name on line 16:
step-functions/lambda/update_asg_ami.py
and zip file, from lambda/ run:
zip update_asg_ami.zip update_asg_ami.py

Setup Virtual Environment
```
python3 -m venv .venv  
source .venv/bin/activate   
python3 -m pip install -r requirements.txt  
cdk bootstrap aws://<account-id>/<region>  
```

Run in this order:
1. ssm-config
2. management-server (imaging server)
3. Alb-autoscale
4. step-functions

Run the step function with this payload, enter stack values used in vars.py file:
```
{
  "Payload": {
    "step": 1,
    "img_project_name": "PUT imaging_stack_name HERE",
    "alb_project_name": "PUT alb_stack_name HERE"
  }
}
```

### Note:
If you run the step function a second time before the first instance 
has been removed in "Terminating" state, then you need to remove the tags from
it, or wait for it to disappear from the console.

(c) Copyright 2020 - NickTheSecurityDude

#### Disclaimer:
For informational/educational purposes only. Bugs are likely and can be reported on github.
Using this will incur AWS charges.
