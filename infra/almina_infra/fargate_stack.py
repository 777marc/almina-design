from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as logs,
)
from constructs import Construct


class AlminaFargateStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, repo_uri: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self,
            "AlminaVpc",
            max_azs=2,
            nat_gateways=1,
        )

        # ECS Cluster
        cluster = ecs.Cluster(self, "AlminaCluster", vpc=vpc)

        # CloudWatch Logs
        log_group = logs.LogGroup(
            self,
            "AlminaTaskLogGroup",
            log_group_name="/ecs/almina-design",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Fargate Service with ALB
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "AlminaFargateService",
            cluster=cluster,
            memory_limit_mib=512,
            cpu=256,
            desired_count=1,
            public_load_balancer=True,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry(repo_uri),
                container_port=8000,
                log_driver=ecs.LogDriver.aws_logs(
                    log_group=log_group,
                    stream_prefix="almina-design",
                ),
            ),
            load_balancer_name="almina-alb",
        )

        # Health check
        fargate_service.target_group.configure_health_check(
            path="/",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
            healthy_threshold_count=2,
            unhealthy_threshold_count=3,
        )

        # Outputs
        CfnOutput(
            self,
            "LoadBalancerDns",
            value=fargate_service.load_balancer.load_balancer_dns_name,
            description="Almina Design app URL",
        )

        CfnOutput(
            self,
            "ClusterName",
            value=cluster.cluster_name,
            description="ECS cluster name",
        )
