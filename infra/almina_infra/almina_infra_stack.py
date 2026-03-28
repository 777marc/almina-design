from aws_cdk import CfnOutput, RemovalPolicy, Stack, aws_ecr as ecr
from constructs import Construct


class AlminaInfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repo = ecr.Repository(
            self,
            "AlminaDesignRepository",
            repository_name="almina-design",
            image_scan_on_push=True,
            image_tag_mutability=ecr.TagMutability.MUTABLE,
            lifecycle_rules=[ecr.LifecycleRule(max_image_count=20)],
            removal_policy=RemovalPolicy.RETAIN,
        )

        self.repo_uri = repo.repository_uri

        CfnOutput(self, "RepositoryName", value=repo.repository_name)
        CfnOutput(self, "RepositoryUri", value=repo.repository_uri)
