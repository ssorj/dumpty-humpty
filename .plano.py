from dump import *
from kubernetes import *

@command
def run_():
    remove("output")

    context = "skewer"
    kubeconfig = parse_yaml(call("kubectl config view"))
    connector = get_cluster_connector(context, kubeconfig)
    namespaces = "skupper", get_current_namespace(context, kubeconfig)

    collect_resources("output", connector, namespaces)
