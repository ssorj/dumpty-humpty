from collections import namedtuple as _namedtuple
from plano import *

class Kubeconfig:
    def __init__(self):
        if "KUBECONFIG" in ENV:
            self.data = read_yaml(ENV["KUBECONFIG"])
        else:
            self.data = read_yaml("~/.kube/config")

    def _get_cluster(self, name):
        try:
            return MapAccessor(next((x["cluster"] for x in self.data["clusters"] if x["name"] == name)))
        except StopIteration:
            return None

    def _get_context(self, name):
        try:
            return MapAccessor(next((x["context"] for x in self.data["contexts"] if x["name"] == name)))
        except StopIteration:
            return None

    def _get_user(self, name):
        try:
            return MapAccessor(next((x["user"] for x in self.data["users"] if x["name"] == name)))
        except StopIteration:
            return None

    def _get_current_context(self):
        assert "current-context" in self.data
        return self._get_context(self.data["current-context"])

    @property
    def connector(self):
        context = self._get_current_context()
        cluster = self._get_cluster(context.cluster)
        user = self._get_user(context.user)

        return Connector(cluster.server, cluster.certificate_authority, user.client_certificate, user.client_key)

    @property
    def namespace(self):
        return self._get_current_context().namespace

Connector = _namedtuple("Connector", ("server_url", "server_cert", "client_cert", "client_key"))

class MapAccessor:
    def __init__(self, data):
        self._data = {k.replace("-", "_"): v for k, v in data.items()}

    def __getattr__(self, name):
        return self._data[name]

def api_get(connector, path):
    return http_get(f"{connector.server_url}{path}", server_cert=connector.server_cert,
                    client_cert=connector.client_cert, client_key=connector.client_key)

def api_get_json(connector, path):
    return parse_json(api_get(connector, path))
