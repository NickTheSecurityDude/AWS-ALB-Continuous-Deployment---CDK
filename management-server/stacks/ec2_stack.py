##############################################################
#
# ec2_stack.py
#
# Resources:
#  - Elastic IP
#  - EC2 Instance
#
##############################################################

from aws_cdk import (
  aws_ec2 as ec2,
  aws_iam as iam,
  core
)

class EC2Stack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, imaging_sg: ec2.ISecurityGroup, imaging_ec2_role: iam.IRole, vars, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # elastic ip
    eip=ec2.CfnEIP(self,"Imaging Server IP")

    # Name Tag for EIP
    core.Tags.of(eip).add(key="Name",value="Imaging Server EIP")

    # Parameters for EC2 Instance
    itype=ec2.InstanceType("t3.nano")
    iami=ec2.MachineImage.from_ssm_parameter(vars['ami_param'],os=ec2.OperatingSystemType.LINUX)
    default_vpc=ec2.Vpc.from_lookup(self, "DefaultVpc", is_default=True)

    # Create EC2 Instance
    imaging_ec2=ec2.Instance(self, "ec2-instance",
      instance_type = itype,
      machine_image = iami,
      vpc = default_vpc,
      security_group=imaging_sg,
      role=imaging_ec2_role,
      key_name=vars['ec2_key_pair']
    )

    # add tags to EC2 Instance
    core.Tags.of(imaging_ec2).add(key="Name",value=vars['ec2_mng_name'])
    core.Tags.of(imaging_ec2).add(key="ami_id_parameter",value=vars['ami_param'])
    core.Tags.of(imaging_ec2).add(key="OS",value="linux")
    core.Tags.of(imaging_ec2).add(key="ServerGroup",value="production")
    core.Tags.of(imaging_ec2).add(key="Type",value="imaging_server")

    # attach eip
    ec2.CfnEIPAssociation(self,"EIP Attachment",eip=eip.ref,instance_id=imaging_ec2.instance_id)
