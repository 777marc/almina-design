#!/usr/bin/env python3
import os

import aws_cdk as cdk

from lightsail_cdk.lightsail_django_stack import LightsailDjangoStack


app = cdk.App()

LightsailDjangoStack(
    app,
    app.node.try_get_context("stackName") or "AlminaDesignLightsailStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
    ),
)

app.synth()
