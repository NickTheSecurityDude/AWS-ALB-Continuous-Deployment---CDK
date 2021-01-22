##############################################################
#
# sg_stack.py
#
# Resources:
#   Security Group For Allowing HTTP and HTTPS traffic
#     - 2 Rules  
#     - Uses the default VPC
#
# Exports:
#  imaging_sg (ISecurityGroup)
#
##############################################################

from aws_cdk import (
  aws_ec2 as ec2,
  core
)

class SGStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # Create the Security Group
    imaging_sg=ec2.SecurityGroup(self,"Imaging SG",
      vpc=ec2.Vpc.from_lookup(self,"DefaultVPC",is_default=True)
    )

    #  Add web traffic security group rules
    imaging_sg.add_ingress_rule(ec2.Peer.any_ipv4(),ec2.Port.tcp(80),"web traffic")
    imaging_sg.add_ingress_rule(ec2.Peer.any_ipv4(),ec2.Port.tcp(443),"web traffic")

    self._imaging_sg=imaging_sg

  # Exports
  @property
  def imaging_sg(self) -> ec2.ISecurityGroup:
    return self._imaging_sg