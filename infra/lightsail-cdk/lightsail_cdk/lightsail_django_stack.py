from pathlib import Path

from aws_cdk import CfnOutput, Stack, aws_lightsail as lightsail
from constructs import Construct


class LightsailDjangoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_name = self.node.try_get_context("appName") or "almina-design"
        instance_name = self.node.try_get_context("instanceName") or "almina-design"
        availability_zone = self.node.try_get_context("availabilityZone") or "us-east-1a"
        blueprint_id = self.node.try_get_context("blueprintId") or "ubuntu_22_04"
        bundle_id = self.node.try_get_context("bundleId") or "micro_3_0"
        repo_url = self.node.try_get_context("repoUrl") or "https://github.com/your-user/almina-design.git"
        repo_branch = self.node.try_get_context("branch") or "main"
        domain_name = (self.node.try_get_context("domainName") or "").strip()
        certificate_email = (self.node.try_get_context("certificateEmail") or "").strip()
        key_pair_name = (self.node.try_get_context("keyPairName") or "").strip()

        project_root = Path(__file__).resolve().parents[3]
        bootstrap_template_path = project_root / "deploy" / "lightsail" / "bootstrap.sh.template"
        bootstrap_template = bootstrap_template_path.read_text(encoding="utf-8")

        host_name = domain_name or "localhost"
        site_url = f"https://{domain_name}" if domain_name else "http://localhost"
        server_name = domain_name or "_"
        allowed_hosts = ",".join(filter(None, [domain_name, "127.0.0.1", "localhost"]))
        csrf_origins = ",".join(filter(None, [site_url, "http://127.0.0.1:8000", "http://localhost:8000"]))

        user_data = (
            bootstrap_template
            .replace("__APP_NAME__", app_name)
            .replace("__INSTANCE_NAME__", instance_name)
            .replace("__REPO_URL__", repo_url)
            .replace("__REPO_BRANCH__", repo_branch)
            .replace("__SITE_URL__", site_url)
            .replace("__HOST_NAME__", host_name)
            .replace("__SERVER_NAME__", server_name)
            .replace("__ALLOWED_HOSTS__", allowed_hosts)
            .replace("__CSRF_TRUSTED_ORIGINS__", csrf_origins)
            .replace("__DOMAIN_NAME__", domain_name)
            .replace("__CERTIFICATE_EMAIL__", certificate_email)
        )

        instance_props = {
            "instance_name": instance_name,
            "availability_zone": availability_zone,
            "blueprint_id": blueprint_id,
            "bundle_id": bundle_id,
            "networking": lightsail.CfnInstance.NetworkingProperty(
                ports=[
                    lightsail.CfnInstance.PortProperty(
                        from_port=22,
                        to_port=22,
                        protocol="tcp",
                        cidrs=["0.0.0.0/0"],
                        ipv6_cidrs=["::/0"],
                    ),
                    lightsail.CfnInstance.PortProperty(
                        from_port=80,
                        to_port=80,
                        protocol="tcp",
                        cidrs=["0.0.0.0/0"],
                        ipv6_cidrs=["::/0"],
                    ),
                    lightsail.CfnInstance.PortProperty(
                        from_port=443,
                        to_port=443,
                        protocol="tcp",
                        cidrs=["0.0.0.0/0"],
                        ipv6_cidrs=["::/0"],
                    ),
                ]
            ),
            "user_data": user_data,
        }
        if key_pair_name:
            instance_props["key_pair_name"] = key_pair_name

        instance = lightsail.CfnInstance(
            self,
            "Instance",
            **instance_props,
        )

        static_ip = lightsail.CfnStaticIp(
            self,
            "StaticIp",
            static_ip_name=f"{instance_name}-ip",
            attached_to=instance.instance_name,
        )

        CfnOutput(self, "InstanceName", value=instance.instance_name)
        CfnOutput(self, "StaticIpAddress", value=static_ip.attr_ip_address)
        CfnOutput(self, "SiteUrl", value=site_url)
        CfnOutput(self, "RepoBranch", value=repo_branch)
        if domain_name:
            CfnOutput(self, "DomainName", value=domain_name)
