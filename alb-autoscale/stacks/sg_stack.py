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
#  alb_sg (ISecurityGroup)
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
    alb_sg=ec2.SecurityGroup(self,"ALB SG",
      vpc=ec2.Vpc.from_lookup(self,"DefaultVPC",is_default=True)
    )

    #  Add web traffic security group rules
    alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(),ec2.Port.tcp(80),"web traffic")
    alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(),ec2.Port.tcp(443),"web traffic")

    self._alb_sg=alb_sg

  # Exports
  @property
  def alb_sg(self) -> ec2.ISecurityGroup:
    return self._alb_sg
