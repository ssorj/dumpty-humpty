from dump import *
from kubernetes import *

@command
def run_():
    remove("output")

    kubeconfig = KubeConfig()
    connector = kubeconfig.get_cluster_connector()
    current_namespace = kubeconfig.get_namespace()

    collect_resources("output", connector, ("skupper", current_namespace))
    collect_logs("output", connector, ("skupper", current_namespace))

# @command
# def dev():
#     kubeconfig = KubeConfig()
#     connector = kubeconfig.get_cluster_connector("skewer")
#     current_namespace = kubeconfig.get_current_namespace("skewer")
