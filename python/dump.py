from plano import *

def collect_resources(output_dir, connector, namespaces):
    # Get data from the Kube API
    def api_get(path):
        return http_get_json(f"{connector.server_url}{path}", server_cert=connector.server_cert,
                             client_cert=connector.client_cert, client_key=connector.client_key)

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
    for resource_type in api_get("/api/v1")["resources"]:
        if resource_type_excluded(resource_type):
            continue

        kind = resource_type["kind"]
        name = resource_type["name"]
        path = f"/api/v1/namespaces/@namespace@/{name}"

        resource_paths.append((kind, path))

    # Get access info for resources from the API groups
    for api_group in api_get("/apis")["groups"]:
        group_version = api_group["preferredVersion"]["groupVersion"]

        for resource_type in api_get(f"/apis/{group_version}")["resources"]:
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
            resources = api_get(path)

            for resource in resources["items"]:
                if resource_excluded(resource):
                    continue

                name = resource["metadata"]["name"]
                output_file = f"{output_dir}/resources/{namespace}/{kind}-{name}.yaml"

                # Prune the noisy and unhelpful managedField data
                if "managedFields" in resource["metadata"]:
                    del resource["metadata"]["managedFields"]

                write_yaml(output_file, resource)
