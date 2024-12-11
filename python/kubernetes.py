from plano import *

from collections import namedtuple as _namedtuple

Connector = _namedtuple("Connector", ("server_url", "server_cert", "client_cert", "client_key"))

def get_cluster_connector(context, kubeconfig_data):
    cluster_data = next((x["cluster"] for x in kubeconfig_data["clusters"] if x["name"] == context))
    user_data = next((x["user"] for x in kubeconfig_data["users"] if x["name"] == context))

    return Connector(cluster_data["server"], cluster_data["certificate-authority"],
                     user_data["client-certificate"], user_data["client-key"])

def get_current_namespace(context, kubeconfig_data):
    return "west" # XXX
