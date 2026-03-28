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

# ECR Repository
infra_stack = AlminaInfraStack(app, "AlminaInfraStack", env=env)

# Fargate Service (requires ECR repo URI)
fargate_stack = AlminaFargateStack(
    app,
    "AlminaFargateStack",
    repo_uri=infra_stack.repo_uri,
    env=env,
)
fargate_stack.add_dependency(infra_stack)

app.synth()
