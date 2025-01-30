from dump import *
from kubernetes import *

kubeconfig = Kubeconfig()

@command
def run_():
    remove("output")

    # collect_versions("output", kubeconfig)
    # collect_events("output", kubeconfig)
    collect_resources("output", kubeconfig)
    # collect_logs("output", kubeconfig)

@command
def dev():
    # print(api_get(kubeconfig.connector, "/api/v1/namespaces/west/pods"))
    print(api_get(kubeconfig.connector, "/api/v1"))
