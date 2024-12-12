from plano import *

from collections import namedtuple as _namedtuple

Connector = _namedtuple("Connector", ("server_url", "server_cert", "client_cert", "client_key"))

class MapAccessor:
    def __init__(self, data):
        self._data = {k.replace("-", "_"): v for k, v in data.items()}

    def __getattr__(self, name):
        return self._data[name]

class KubeConfig:
    def __init__(self):
        if "KUBECONFIG" in ENV:
            self.data = read_yaml(ENV["KUBECONFIG"])
        else:
            self.data = read_yaml("~/.kube/config")

    def get_cluster(self, name):
        try:
            return MapAccessor(next((x["cluster"] for x in self.data["clusters"] if x["name"] == name)))
        except StopIteration:
            return None

    def get_context(self, name):
        try:
            return MapAccessor(next((x["context"] for x in self.data["contexts"] if x["name"] == name)))
        except StopIteration:
            return None

    def get_user(self, name):
        try:
            return MapAccessor(next((x["user"] for x in self.data["users"] if x["name"] == name)))
        except StopIteration:
            return None

    def get_current_context(self):
        assert "current-context" in self.data

        return self.get_context(self.data["current-context"])

    def get_cluster_connector(self, context_name=None):
        if context_name is None:
            context = self.get_current_context()
        else:
            context = self.get_context(context_name)

        cluster = self.get_cluster(context.cluster)
        user = self.get_user(context.user)

        return Connector(cluster.server, cluster.certificate_authority, user.client_certificate, user.client_key)

    def get_namespace(self, context_name=None):
        if context_name is None:
            context = self.get_current_context()
        else:
            context = self.get_context(context_name)

        return context.namespace

def api_get(connector, path):
    return http_get(f"{connector.server_url}{path}", server_cert=connector.server_cert,
                    client_cert=connector.client_cert, client_key=connector.client_key)

def api_get_json(connector, path):
    return parse_json(api_get(connector, path))
