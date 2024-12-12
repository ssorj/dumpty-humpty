from dump import *
from kubernetes import *

kubeconfig = KubeConfig()

@command
def run_():
    remove("output")

    collect_versions("output", kubeconfig)
    collect_events("output", kubeconfig)
    collect_resources("output", kubeconfig)
    collect_logs("output", kubeconfig)

@command
def dev():
    kubeconfig = KubeConfig()
    print(api_get(kubeconfig.connector, "/api/v1/namespaces/west/pods"))
