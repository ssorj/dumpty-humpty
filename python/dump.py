from plano import *

def collect_resources(output_dir, connector, namespaces):
    def api_get(path):
        return http_get_json(f"{connector.server_url}{path}", server_cert=connector.server_cert,
                             client_cert=connector.client_cert, client_key=connector.client_key)

    def resource_type_excluded(resource_type):
        if not resource_type["namespaced"]:
            return True

        if not resource_type["singularName"]:
            return True

        if "get" not in resource_type["verbs"]:
            return True

        if resource_type["kind"] in ("Secret", "AccessGrant", "AccessToken"):
            return True

    def resource_excluded(resource):
        if resource["metadata"]["name"].endswith(".crt"):
            return True

    resource_paths = list()

    for resource_type in api_get("/api/v1")["resources"]:
        if resource_type_excluded(resource_type):
            continue

        resource_name = resource_type["name"]
        resource_paths.append((resource_type["kind"], f"/api/v1/namespaces/@namespace@/{resource_name}"))

    for api_group in api_get("/apis")["groups"]:
        group_version = api_group["preferredVersion"]["groupVersion"]

        for resource_type in api_get(f"/apis/{group_version}")["resources"]:
            if resource_type_excluded(resource_type):
                continue

            resource_name = resource_type["name"]
            resource_paths.append((resource_type["kind"], f"/apis/{group_version}/namespaces/@namespace@/{resource_name}"))

    for resource_path in resource_paths:
        for namespace in namespaces:
            kind, path = resource_path
            path = path.replace("@namespace@", namespace)
            resources = api_get(path)

            for resource in resources["items"]:
                if resource_excluded(resource):
                    continue

                name = resource["metadata"]["name"]
                file_ = f"{output_dir}/resources/{namespace}/{kind}-{name}.yaml"

                if "managedFields" in resource["metadata"]:
                    del resource["metadata"]["managedFields"]

                write_yaml(file_, resource)
