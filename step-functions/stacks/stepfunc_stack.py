##############################################################
#
# step_func_stack.py
#
# Defines the function steps and definition
#
# Notes:
#  Role is created automagically
#
##############################################################

from aws_cdk import (
  aws_stepfunctions as sfn,
  aws_stepfunctions_tasks as sfn_tasks,
  aws_lambda as _lambda,
  aws_iam as iam,
  core
)

class StepFuncStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str,  
      update_asg_ami_func: _lambda.IFunction, 
      env, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)
 
    yum_update_task=sfn_tasks.LambdaInvoke(
      self, 'YumUpdate',
      lambda_function=update_asg_ami_func,
      #payload=sfn.TaskInput.from_data_at('$'),
      #result_path='$.taskresult'
    )

    wait_for_yum=sfn.Wait(self,"Wait For Yum",time=sfn.WaitTime.duration(core.Duration.seconds(60)))

    check_yum=sfn_tasks.LambdaInvoke(
      self, 'CheckYum',
      lambda_function=update_asg_ami_func,
      #payload=sfn.TaskInput.from_data_at('$'),
      #result_path='$.taskresult'
    )

    create_ami_task=sfn_tasks.LambdaInvoke(
      self, 'CreateAMI',
      lambda_function=update_asg_ami_func,
      #payload=sfn.TaskInput.from_data_at('$'),
      #result_path='$.taskresult'
    )

    wait_for_ami=sfn.Wait(self,"Wait For AMI",time=sfn.WaitTime.duration(core.Duration.seconds(60)))

    check_ami_task=sfn_tasks.LambdaInvoke(
      self, 'CheckAMI',
      lambda_function=update_asg_ami_func,
      payload=sfn.TaskInput.from_data_at('$'),
      #result_path='$.taskresult'
    )

    update_ami_task=sfn_tasks.LambdaInvoke(
      self, 'UpdateAMI',
      lambda_function=update_asg_ami_func,
      #payload=sfn.TaskInput.from_data_at('$'),
      #result_path='$.taskresult'
    )

    finish=sfn.Pass(self,"Finish")

    check_yum_status_choice=sfn.Choice(
      self, 'CheckYumStatus'
    )

    check_status_choice=sfn.Choice(
      self, 'CheckStatus'
    )

    sf_definition=yum_update_task.next(
      wait_for_yum.next(
        check_yum.next(
          check_yum_status_choice.when(
            sfn.Condition.string_equals(
              '$.Payload.status', 'Worked'
            ),
            create_ami_task.next(
              wait_for_ami.next(
                check_ami_task.next(
                  check_status_choice.when(
                    sfn.Condition.string_equals(
                      '$.Payload.status', 'Worked'
                    ),
                    update_ami_task.next(finish)
                    ).otherwise(
                      wait_for_ami
                    )
                   )
                )
              )
            ).otherwise(
            wait_for_yum
          )
        )
      )
    )
            

    sfn.StateMachine(self,"Update AMI Step Function",
      definition=sf_definition,
      #role=step_func_iam_role
    )
