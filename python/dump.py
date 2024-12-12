from kubernetes import *
from plano import *

def collect_versions(output_dir, kubeconfig):
    connector = kubeconfig.connector

    touch(f"{output_dir}/versions/skupper.yaml")
    write_yaml(f"{output_dir}/versions/kubernetes.yaml", api_get_json(connector, "/version"))

def collect_resources(output_dir, kubeconfig):
    connector = kubeconfig.connector
    namespaces = "skupper", kubeconfig.namespace

    # Exclude some resource types
    def resource_type_excluded(resource_type):
        # Exclude resources that are not namespaced
        if not resource_type["namespaced"]:
            return True

        # Exclude subresources
        if not resource_type["singularName"]:
            return True

        # Exclude resources we can't read
        if "get" not in resource_type["verbs"]:
            return True

        # Exclude resources that contain sensitive information
        if resource_type["kind"] in ("Secret", "AccessGrant", "AccessToken"):
            return True

    # Exclude some resources
    def resource_excluded(resource):
        # Exclude resources that contain sensitive information
        if resource["metadata"]["name"].endswith(".crt"):
            return True

    resource_paths = list()

    # Get access info for the core resources
    for resource_type in api_get_json(connector, "/api/v1")["resources"]:
        if resource_type_excluded(resource_type):
            continue

        kind = resource_type["kind"]
        name = resource_type["name"]
        path = f"/api/v1/namespaces/@namespace@/{name}"

        resource_paths.append((kind, path))

    # Get access info for resources from the API groups
    for api_group in api_get_json(connector, "/apis")["groups"]:
        # XXX This needs to be every version!
        group_version = api_group["preferredVersion"]["groupVersion"]

        for resource_type in api_get_json(connector, f"/apis/{group_version}")["resources"]:
            if resource_type_excluded(resource_type):
                continue

            kind = resource_type["kind"]
            name = resource_type["name"]
            path = f"/apis/{group_version}/namespaces/@namespace@/{name}"

            resource_paths.append((kind, path))

    # Get and store the resources
    for resource_path in resource_paths:
        for namespace in namespaces:
            kind, path = resource_path
            path = path.replace("@namespace@", namespace)
            resources = api_get_json(connector, path)

            for resource in resources["items"]:
                if resource_excluded(resource):
                    continue

                name = resource["metadata"]["name"]
                output_file = f"{output_dir}/resources/{namespace}/{kind}-{name}.yaml"

                # Prune the noisy and unhelpful managedField data
                if "managedFields" in resource["metadata"]:
                    del resource["metadata"]["managedFields"]

                write_yaml(output_file, resource)

def collect_logs(output_dir, kubeconfig):
    connector = kubeconfig.connector
    namespaces = "skupper", kubeconfig.namespace

    for namespace in namespaces:
        pods = api_get_json(connector, f"/api/v1/namespaces/{namespace}/pods")

        for pod in pods["items"]:
            name = pod["metadata"]["name"]
            containers = [x["name"] for x in pod["spec"]["containers"]]

            for container in containers:
                output_file = f"{output_dir}/logs/{namespace}/{name}-{container}.txt"
                log = api_get(connector, f"/api/v1/namespaces/{namespace}/pods/{name}/log?container={container}")

                write(output_file, log)
