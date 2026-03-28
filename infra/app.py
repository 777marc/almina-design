#!/usr/bin/env python3
import os

import aws_cdk as cdk

from almina_infra.almina_infra_stack import AlminaInfraStack
from almina_infra.fargate_stack import AlminaFargateStack


app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION"),
)

# ECR repository stack
infra_stack = AlminaInfraStack(app, "AlminaInfraStack", env=env)

# Fargate service stack
fargate_stack = AlminaFargateStack(
    app,
    "AlminaFargateStack",
    repository=infra_stack.repo,
    env=env,
)
fargate_stack.add_dependency(infra_stack)

app.synth()
