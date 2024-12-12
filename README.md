# Dumpty Humpty

## Theses

- Logs are included only for pods with names starting with "skupper-".
  User application logs are excluded.
- All resource kinds are included, except Secrets, AccessGrants, and
  AccessTokens.  We could do redactions instead.
- All resource instances are included except those with names ending
  in ".crt".
- The managedFields sutbree is pruned out of the resource YAML, since
  it's noisy and not a debugging aid.
- YAML files have a copy with a .txt extension, so you can view them
  in a web browser.

## Default dump file name

`skupper-dump-<site-name>-<date>.tar.gz`

## Dump file content

~~~
index.md
index.html
versions/
  kubernetes.yaml
  kubernetes.yaml.txt
  skupper.yaml
  skupper.yaml.txt
site-namespace/
  events.yaml
  events.yaml.txt
  resources/<kind>-<name>.yaml
  resources/<kind>-<name>.yaml.txt
  logs/<pod-name>-<container-name>.txt
controller-namespace/
  events.yaml
  events.yaml.txt
  resources/<kind>-<name>.yaml
  resources/<kind>-<name>.yaml.txt
  controller-<id>-log.txt
~~~

#### `report.md`

A consolidated report highlight potential problems.  This is not yet
specced out.

#### `versions/kubernetes.yaml`

Kube API: `/version`

#### `versions/skupper.yaml`

Same as the output of `skupper version --output yaml`.

#### `site-namespace/events.yaml`

Kube API: `/api/v1/namespaces/<site-namespace>/events`

#### `site-namespace/resources/<kind>-<name>.yaml`

Kube APIs:

 - `/api/v1/namespaces/<site-namespace>/<plural-name>`
 - `/apis/<group-name>/<version>/namespaces/<site-namespace>/<plural-name>`

#### `site-namespace/logs/<pod-name>-<container-name>.txt`

Kube API: `/api/v1/namespaces/<site-namespace>/pods/<pod-name>/log?container=<container-name>`

#### `controller-namespace/events.yaml`

Kube API: `/api/v1/namespaces/skupper/events`

#### `controller-namespace/resources/<kind>-<name>.yaml`

Kube APIs:

 - `/api/v1/namespaces/skupper/<plural-name>`
 - `/apis/<group-name>/<version>/namespaces/skupper/<plural-name>`

#### `controller-namespace/logs/<pod-name>-<container-name>.txt`

Kube API: `/api/v1/namespaces/skupper/pods/<pod-name>/log?container=<container-name>`

## An example dump file

~~~
skupper-dump-west-2024-12-12/
  report.md
  report.html
  versions/
    skupper.yaml[.txt]
    kubernetes.yaml[.txt]
  site-namespace/
    events.yaml[.txt]
    resources/
      ConfigMap-skupper-network-status.yaml[.txt]
      ConfigMap-skupper-router.yaml[.txt]
      ConfigMap-skupper-site-leader.yaml[.txt]
      Endpoints-backend.yaml[.txt]
      Endpoints-skupper-router-1.yaml[.txt]
      Endpoints-skupper-router-local.yaml[.txt]
      Pod-frontend-578d87bcd8-pkkhc.yaml[.txt]
      Pod-skupper-router-67fc7fd88c-j86wk.yaml[.txt]
      ServiceAccount-default.yaml[.txt]
      ServiceAccount-skupper-router.yaml[.txt]
      Service-backend.yaml[.txt]
      Service-skupper-router-1.yaml[.txt]
      Service-skupper-router-local.yaml[.txt]
      Deployment-frontend.yaml[.txt]
      Deployment-skupper-router.yaml[.txt]
      ReplicaSet-frontend-578d87bcd8.yaml[.txt]
      ReplicaSet-skupper-router-67fc7fd88c.yaml[.txt]
      ReplicaSet-skupper-router-7484489f7.yaml[.txt]
      RoleBinding-skupper-router.yaml[.txt]
      Role-skupper-router.yaml[.txt]
      EndpointSlice-backend-bd5dr.yaml[.txt]
      EndpointSlice-skupper-router-1-w6rkj.yaml[.txt]
      EndpointSlice-skupper-router-local-r98qv.yaml[.txt]
      Certificate-skupper-local-ca.yaml[.txt]
      Certificate-skupper-local-server.yaml[.txt]
      Certificate-skupper-site-ca.yaml[.txt]
      Certificate-skupper-site-server.yaml[.txt]
      Listener-backend.yaml[.txt]
      RouterAccess-skupper-router.yaml[.txt]
      Site-west.yaml[.txt]
      SecuredAccess-skupper-router-1.yaml[.txt]
    logs/
      skupper-router-67fc7fd88c-j86wk-router.txt
      skupper-router-67fc7fd88c-j86wk-config-sync.txt
  controller-namespace/
    events.yaml[.txt]
    events.yaml[.txt].txt
    resources/
      Endpoints-skupper-grant-server.yaml[.txt]
      Pod-skupper-controller-7867f76fc8-59hbt.yaml[.txt]
      ServiceAccount-default.yaml[.txt]
      ServiceAccount-skupper-controller.yaml[.txt]
      Service-skupper-grant-server.yaml[.txt]
      Deployment-skupper-controller.yaml[.txt]
      ReplicaSet-skupper-controller-7867f76fc8.yaml[.txt]
      EndpointSlice-skupper-grant-server-zbrtm.yaml[.txt]
      Certificate-skupper-grant-server.yaml[.txt]
      Certificate-skupper-grant-server-ca.yaml[.txt]
      SecuredAccess-skupper-grant-server.yaml[.txt]
    logs/
      skupper-controller-7867f76fc8-59hbt-controller.txt
~~~
