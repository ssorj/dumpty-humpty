from kubernetes import *
from plano import *

def collect_versions(output_dir, kubeconfig):
    connector = kubeconfig.connector

    touch(f"{output_dir}/versions/skupper.yaml")
    write_yaml(f"{output_dir}/versions/kubernetes.yaml", api_get_json(connector, "/version"))

def collect_events(output_dir, kubeconfig):
    site_event_file = f"{output_dir}/site-namespace/events.yaml"
    controller_event_file = f"{output_dir}/controller-namespace/events.yaml"

    write_yaml(site_event_file, api_get_json(kubeconfig.connector, f"/api/v1/namespaces/{kubeconfig.namespace}/events"))
    write_yaml(controller_event_file, api_get_json(kubeconfig.connector, f"/api/v1/namespaces/skupper/events"))

    copy(site_event_file, site_event_file + ".txt")
    copy(controller_event_file, controller_event_file + ".txt")

def collect_resources(output_dir, kubeconfig):
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
    for resource_type in api_get_json(kubeconfig.connector, "/api/v1")["resources"]:
        if resource_type_excluded(resource_type):
            continue

        kind = resource_type["kind"]
        name = resource_type["name"]
        path = f"/api/v1/namespaces/@namespace@/{name}"

        resource_paths.append((kind, path))

    # Get access info for resources from the API groups
    for api_group in api_get_json(kubeconfig.connector, "/apis")["groups"]:
        # XXX This needs to be every version!
        group_version = api_group["preferredVersion"]["groupVersion"]

        for resource_type in api_get_json(kubeconfig.connector, f"/apis/{group_version}")["resources"]:
            if resource_type_excluded(resource_type):
                continue

            kind = resource_type["kind"]
            name = resource_type["name"]
            path = f"/apis/{group_version}/namespaces/@namespace@/{name}"

            resource_paths.append((kind, path))

    # Get and store the resources
    for resource_path in resource_paths:
        kind, path = resource_path
        path = path.replace("@namespace@", kubeconfig.namespace)
        resources = api_get_json(kubeconfig.connector, path)

        for resource in resources["items"]:
            if resource_excluded(resource):
                continue

            name = resource["metadata"]["name"]
            output_file = f"{output_dir}/site-namespace/resources/{kind}-{name}.yaml"

            # Prune the noisy and unhelpful managedField data
            if "managedFields" in resource["metadata"]:
                del resource["metadata"]["managedFields"]

            write_yaml(output_file, resource)

        kind, path = resource_path
        path = path.replace("@namespace@", "skupper")
        resources = api_get_json(kubeconfig.connector, path)

        for resource in resources["items"]:
            if resource_excluded(resource):
                continue

            name = resource["metadata"]["name"]
            output_file = f"{output_dir}/controller-namespace/resources/{kind}-{name}.yaml"

            # Prune the noisy and unhelpful managedField data
            if "managedFields" in resource["metadata"]:
                del resource["metadata"]["managedFields"]

            write_yaml(output_file, resource)

def collect_logs(output_dir, kubeconfig):
    def pod_excluded(pod):
        if not pod["metadata"]["name"].startswith("skupper-"):
            return True

    pods = api_get_json(kubeconfig.connector, f"/api/v1/namespaces/{kubeconfig.namespace}/pods")

    for pod in pods["items"]:
        if pod_excluded(pod):
            continue

        name = pod["metadata"]["name"]
        containers = [x["name"] for x in pod["spec"]["containers"]]

        for container in containers:
            output_file = f"{output_dir}/site-namespace/logs/{name}-{container}.txt"
            log = api_get(kubeconfig.connector, f"/api/v1/namespaces/{kubeconfig.namespace}/pods/{name}/log?container={container}")

            write(output_file, log)

    pods = api_get_json(kubeconfig.connector, f"/api/v1/namespaces/skupper/pods")

    for pod in pods["items"]:
        if pod_excluded(pod):
            continue

        name = pod["metadata"]["name"]
        containers = [x["name"] for x in pod["spec"]["containers"]]

        for container in containers:
            output_file = f"{output_dir}/controller-namespace/logs/{name}-{container}.txt"
            log = api_get(kubeconfig.connector, f"/api/v1/namespaces/skupper/pods/{name}/log?container={container}")

            write(output_file, log)
