import pulumi
import pulumi_gcp as gcp
import pulumi_docker as docker

# Variables
repo_url = "."  # Note: Docker build context usually points to a local path, not a GitHub URL string
project_id = "extended-creek-342715"
region = "europe-west12"
service_name = "demoapi"

# The path to your existing Artifact Registry
# Format: {region}-docker.pkg.dev/{project}/{repo_name}/{image_name}
image_name = f"{region}-docker.pkg.dev/{project_id}/{service_name}/{service_name}"

# Build and push the image to the existing Artifact Registry
docker_image = docker.Image(
    "demoapi-image",
    build=docker.DockerBuildArgs(
        context=repo_url,  # Ensure your Dockerfile is in this directory
    ),
    image_name=image_name,
)

# Deploy the image to Cloud Run
service = gcp.cloudrun.Service(
    "demoapi-service-from-pulumi",
    location=region,
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            containers=[
                gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                    image=docker_image.base_image_name, # Ensures we use the specific pushed digest
                ),
            ],
        ),
    ),
    traffics=[gcp.cloudrun.ServiceTrafficArgs(
        percent=100,
        latest_revision=True,
    )]
)

# Allow unauthenticated access (Optional: remove if you want a private API)
iam_everyone = gcp.cloudrun.IamMember("allow-everyone",
    location=service.location,
    service=service.name,
    role="roles/run.invoker",
    member="allUsers"
)

# Export the Endpoint URL
pulumi.export("url", service.statuses[0].url)