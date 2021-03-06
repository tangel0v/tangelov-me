---
title: "Kubernetes (IV): autenticación y autorización"
slug: kubernetes-iv
authors:
  - tangelov
date: 2020-04-28T10:00:00+02:00
tags:  ["kubernetes", "docker", "contenedores"]
categories: ["cloud"]
draft: false
---

Hoy vamos a continuar con la serie de posts relacionados con Kubernetes. Tras el contenido de los post [I](https://tangelov.me/posts/kubernetes-i.html), [II](https://tangelov.me/posts/kubernetes-ii.html) y [III](https://tangelov.me/posts/kubernetes-iii.html), ya sabemos un poco qué es Kubernetes, cómo almacenar datos en nuestro clúster y cómo acceder a nuestros servicios.

En cada post hemos visto como K8s está diseñado para ser escalable y para ello, cualquier servicio necesita ingentes cantidades de hardware (host, switchs, routers, cableado, discos duros, etc).

Si utilizamos una nube pública, nuestro proveedor se encargará de aprovisionar los recursos necesarios, pero seguirá de nuestra mano el tener que distribuir las cargas de trabajo a lo largo del clúster para lograr nuestros objetivos de servicio (alta disponibilidad, distribución en zonas o regiones, etc).

La gran necesidad de recursos nos lleva a hacernos una pregunta: ¿Cómo podemos aprovechar al máximo los recursos de nuestro clúster? La forma más completa se basa en desplegar diferentes aplicaciones que compartan hardware, pero puede no ser lo más seguro.

Así que, ¿cómo podemos aprovechar al máximo y de la manera más segura posible, los recursos de nuestro clúster?

<!--more-->

### Namespaces
Kubernetes está pensado para que podamos compartir los recursos de nuestro clúster entre diferentes aplicaciones. Esto permite generar clústers más grandes donde pueden convivir varias cargas de trabajo, en lugar de tener clústers pequeños y que dificultan la gestión del conjunto.

Aunque siempre hemos podido desplegar pods y asignarles unos [límites](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/cpu-constraint-namespace/) en el consumo de recursos (trataremos esto en otros posts), eso solo distribuye los recursos entre las aplicaciones.

Para poder agrupar, aislar o etiquetar objetos en K8s, así como para aplicar cuotas tenemos que utilizar una especie de _carpetas_ lógicas llamadas _namespaces_. Por el momento, sólo voy a utilizarlos para agrupar los recursos.

Gran parte de los objetos de Kubernetes están ligados al namespace en el que es creado y si no le indicamos ninguno, utiliza el namespace _default_. Éste es junto a _kube-system_ (donde se despliegan las herramientas propias del clúster) uno de namespaces que suelen existir por defecto en cualquier clúster.

La creación de namespaces es muy sencilla: si quisiésemos crear uno de nombre _ghost_, tan sólo ejecutaríamos el siguiente comando ```kubectl create namespace ghost``` y ya podríamos empezar a utilizarlo.

```bash
kubectl get namespaces
NAME              STATUS   AGE
default           Active    1d
ghost             Active    1d
kube-node-lease   Active    1d
kube-public       Active    1d
kube-system       Active    1d
```

Ya podríamos desplegar objetos en él. Algunos de ellos, como los _Persistent Volumes_ o las _Storage Class_ son comunes al clúster, pero otros como los _Deployment_ o los _Persistent Volume Claim_ si lo son. Para ver que objetos son comunes al clúster y no se encuentran _"namespaceados"_ (¡Toma palabro!), podemos ejecutar el siguiente comando ```kubectl api-resources```. Así podemos ver los tipos de objeto que podemos crear y si se definen a nivel de namespace o no.

```bash
NAME                              SHORTNAMES   APIGROUP                       NAMESPACED   KIND
bindings                                                                      true         Binding
componentstatuses                 cs                                          false        ComponentStatus
configmaps                        cm                                          true         ConfigMap
endpoints                         ep                                          true         Endpoints
events                            ev                                          true         Event
limitranges                       limits                                      true         LimitRange
namespaces                        ns                                          false        Namespace
nodes                             no                                          false        Node
persistentvolumeclaims            pvc                                         true         PersistentVolumeClaim
persistentvolumes                 pv                                          false        PersistentVolume
pods                              po                                          true         Pod
podtemplates                                                                  true         PodTemplate
replicationcontrollers            rc                                          true         ReplicationController
resourcequotas                    quota                                       true         ResourceQuota
secrets                                                                       true         Secret
serviceaccounts                   sa                                          true         ServiceAccount
services                          svc                                         true         Service
mutatingwebhookconfigurations                  admissionregistration.k8s.io   false        MutatingWebhookConfiguration
validatingwebhookconfigurations                admissionregistration.k8s.io   false        ValidatingWebhookConfiguration
customresourcedefinitions         crd,crds     apiextensions.k8s.io           false        CustomResourceDefinition
apiservices                                    apiregistration.k8s.io         false        APIService
controllerrevisions                            apps                           true         ControllerRevision
daemonsets                        ds           apps                           true         DaemonSet
deployments                       deploy       apps                           true         Deployment
[...]
```


## Autenticación en K8s
Aunque hayamos creado un namespace nuevo, sigue sin hacer separación lógica. Nuestro usuario puede ver los objetos del clúster independientemente del namespace en el que se encuentren. Esto es debido a que _podemos_ hacerlo: nuestra autenticación y autorización (somos administradores) lo permite. La configuración por defecto de Microk8s es ésta.

Para comenzar a limitar lo que se puede hacer en Kubernetes, primero debemos entender que cada usuario tiene primero que autenticarse (quien es) y autorizarse (que puede hacer dentro del clúster). Cualquier operador, cuenta robot o servicio necesita credenciales para interactuar contra el clúster, o mejor dicho, contra las APIs del clúster.

Podemos autenticarnos frente a Kubernetes de diferentes maneras: podemos utilizar certificados, cuentas de servicio o tokens JWT (a través de OpenID). Para simplificar el post, voy a utilizar _service account_, pero si alguien desea más información al respecto, puede revisar cómo funcionan el resto de sistemas en la documentación adjunta.

### Cuentas de servicio
Tras crear nuestro _namespace_ vamos a crear una _service account_ o cuenta de servicio de Kubernetes. Es un tipo de objeto que creamos a nivel de namespace y que nos permite autenticar nuestras aplicaciones dentro del clúster. Para generar una cuenta, podemos aplicar el siguiente código:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ghost-sa
  namespace: ghost
```

Si aplicamos ese fichero, se habrá generado una cuenta de servicio llamada _ghost-sa_ en el namespace _ghost_. También habrá aparecido un nuevo secreto que contiene el token que podemos utilizar para loguearnos en el clúster.

```bash
kubectl get sa,secrets -n ghost
NAME                      SECRETS   AGE
serviceaccount/default    1          1d
serviceaccount/ghost-sa   1         26s

NAME                          TYPE                                  DATA   AGE
secret/default-token-nstql    kubernetes.io/service-account-token   3       1d
secret/ghost-sa-token-9qvks   kubernetes.io/service-account-token   3      26s
```

Cuando utilizamos las cuentas de servicio dentro del clúster, éstas se autentican automáticamente, pero para probar nosotros vamos a obtener el token y a añadirlo a nuestro _kubeconfig_. Para obtener el token ejecutamos el siguiente comando:

```bash
kubectl get secrets -o jsonpath="{.items[?(@.metadata.annotations['kubernetes\.io/service-account\.name']=='ghost-sa')].data.token}" -n ghost | base64 --decode
```

Utilizando dicho token vamos a añadir una entrada en nuestro kubeconfig (suele estar en ~/.kube/config):

![kubeconfig-sa](https://storage.googleapis.com/tangelov-data/images/0030-01.png)

* La parte azul es la configuración del nuevo usuario que utiliza directamente el token que hemos obtenido en el paso anterior.

* La parte roja se corresponde con un nuevo contexto que utilizaremos para conectarnos con esta cuenta de servicio.


## Autorización en K8s
Ya tenemos nuestro _namespace_ y nuestra cuenta de servicio, pero antes de explicar cómo funciona la autorización, es necesario comentar cómo interactuamos contra Kubernetes:

* Kubernetes tiene diferentes APIs.

* Cada una posee diversos recursos sobre los que podemos realizar acciones.

* Cada API tiene una serie de _verbs_ o acciones, que podemos realizar sobre uno o más recursos.

Imaginemos que hemos generado una cuenta de servicio y nos hemos autenticado contra el clúster. Ahora cada operación que hagamos, 

Una forma de interactuar es utilizar _kubectl apply -f $fichero_. Si utilizaramos este [fichero de ejemplo](https://gitlab.com/tangelov/proyectos/-/raw/master/templates/kubernetes/basic-nginx-deployment.yml) estaríamos haciendo lo siguiente:

* Interactuaríamos contra la API de _apps/v1_.

* El resource creado sería un _Deployment_.

* Sería necesario tener una serie de verbs para que el recurso pueda ser creado. Podrían ser _get_, _delete_, _create_, etc.

Para poder configurar qué puede hacer cada usuario del clúster, tenemos que utilizar alguna de las estrategias de autorización de Kubernetes.


## Autorización mediante RBAC en K8s
RBAC significa _Role-based access control_ es un sistema que nos permite definir qué puede hacer qué y sobre qué dentro de nuestro clúster. Es la política más extendida y la recomendada por Kubernetes.

> RBAC no es la única política disponible. ABAC es otra política de permisos en Kubernetes pero es más antigua y compleja, por lo que no se recomienda. No voy a explicarla, pero si alguien desea más información al respecto, podemos hacer click [aquí](https://kubernetes.io/docs/reference/access-authn-authz/authorization/).

La mejor forma de entender cómo funciona RBAC es mediante un ejemplo. Imaginemos que hemos creado una cuenta de servicio y hemos asignado unos permisos que le permiten hacer las siguientes acciones:

![rbac-example](https://storage.googleapis.com/tangelov-data/images/0030-00.png)

* En el API Group 1, puede ejecutar cualquier acción en el recurso 1 y un par de acciones en el tipo de recurso 2.

* En el API Group 2, sólo puede ejecutar una acción en un tipo de recursos concreto.

* En el API Group 3, puede ejecutar algunas acciones en un tipo de recurso concreto.

Para utilizar RBAC, antes de nada tenemos que ver si éste se encuentra habilitado o no. Si nuestro clúster es muy antiguo, podemos ejecutar el comando ```kubectl api-versions | grep rbac.authorization.k8s.io/v1``` y si nos devuelve algún resultado es que está habilitado.

Si no estuviese habilitado, podemos habilitarlo en en clúster ya existente, relanzando el API Server de K8s con la flag _--authorization-mode=RBAC_. Si utilizamos algún proveedor de nube, nos encontramos con este estado:

* En Microsoft Azure, a día de hoy todavía no podemos habilitar RBAC en un clúster ya creado y debemos hacerlo en la creación del clúster. Si utilizamos la CLI de Azure, lo haríamos añadiendo la flag _--enable-rbac_ al comando.

* En AWS el servicio se lanzó habilitado por defecto.

* En Google Cloud está habilitado por defecto desde la versión de Kubernetes 1.6. Si deseamos actualizar un clúster ya existente para que utilice RBAC debemos actualizar el clúster con la opción _--no-enable-legacy-authorization_.

En MicroK8s tenemos que habilitarlo con el comando ```microk8s.enable rbac```.

```bash
microk8s.kubectl api-versions | grep rbac.authorization.k8s.io/v1

rbac.authorization.k8s.io/v1
rbac.authorization.k8s.io/v1beta1
```

### Roles y scopes
En estos momentos ya tenemos RBAC habilitado y una cuenta de servicio asociada en nuestro kubeconfig. Vamos a activarla con ```kubectl config use-context ghost```

Si ahora intentamos ejecutar cualquier comando, recibiremos un error:

```bash
~ kubectl get pods
Error from server (Forbidden): pods is forbidden: User "system:serviceaccount:ghost:ghost-sa" cannot list resource "pods" in API group "" in the namespace "default"

~ kubectl get pods -n ghost
Error from server (Forbidden): pods is forbidden: User "system:serviceaccount:ghost:ghost-sa" cannot list resource "pods" in API group "" in the namespace "ghost"
```

Estos errores demuestran que no tenemos permisos en nuestra cuenta de servicio. Para ilustrar como funciona RBAC vamos a añadirle dos permisos:

* Un permiso global a todo el clúster que nos permita ver que pods y los logs de los mismos en cualquier namespace del clúster. Dicho permiso no va a permitir borrar, desplegar nuevos pods o ver el contenido de los secretos.

* Un permiso específico para poder gestionar cualquier tipo de carga de trabajo en nuestro namespace, pero sin permitir que podamos borrarlos. Tampoco queremos que pueda tener permisos para modificar permisos en dicho namespace.

Antes de nada, cambiamos nuestro contexto con ```kubectl config use-context microk8s``` para volver a tener permisos. 

Cada grupo de permisos que definamos en Kubernetes, tiene un alcance o _scope_. Si éste aplica a un único namespace, estamos generando un objeto de tipo _Role_ y si aplica a todo el clúster, un objeto de tipo _ClusterRole_.

Para el permiso general, vamos a crear un fichero con el siguiente contenido:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-reader
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list"]
```

De esta forma le indicamos a Kubernetes (a través de la API de autorización _rbac.authorization.k8s.io/v1_), que el _ClusteRole_ cluster-reader puede realizar las acciones (verbs) en los siguientes objetos (resources). Así definimos "el qué" puede hacer de la autorización.

> NOTA: apiGroups está vacío debido a que nos estamos refiriendo a la API por defecto.

Ya hemos generado unos permisos para nuestras cuentas, pero todavía no se los hemos asignado. Para asignar un permiso general a todo el clúster debemos crear otro objeto llamado _ClusterRoleBinding_. Este sería el código de ejemplo:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ghost-cluster-reader-binding
subjects:
- kind: ServiceAccount
  name: ghost-sa
  namespace: ghost
  apiGroup: ""
roleRef:
  kind: ClusterRole
  name: cluster-reader
  apiGroup: ""
```

En este ejemplo, la cuenta de servicio _ghost-sa_ es asignado al _ClusterRole_ de nombre _cluster-reader_. Así definimos "el quién" de la autorización.

Ahora procedemos a aplicar los dos ficheros para generar el permiso y asignarlo a nuestra cuenta de servicio.

```bash
kubectl apply -f clusterrole.yaml 
clusterrole.rbac.authorization.k8s.io/cluster-reader created

kubectl apply -f clusterrolebinding.yaml 
clusterrolebinding.rbac.authorization.k8s.io/ghost-cluster-reader-binding created
```

El siguiente permiso es más específico y restringido en _scope_. En lugar de dar permisos sobre todo el clúster vamos a hacerlo sobre un único namespace. Este tipo de objetos son similares a los anteriores, pero sin el "clúster": _Role_ y _RoleBinding_ respectivamente. Éste sería su código:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ghost-operator
  namespace: ghost
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "watch", "list", "create", "update", "patch"]
- apiGroups: ["extensions"]
  resources: ["deployments"]
  verbs: ["get", "watch", "list", "create", "update", "patch"]
- apiGroups: ["apps"]
  resources: ["statefulsets"]
  verbs: ["get", "watch", "list", "create", "update", "patch"]
- apiGroups: [""]
  resources: ["secrets", "configmaps", "persistentvolumeclaims"]
  verbs: ["get", "watch", "list", "create", "update", "patch"]
```

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ghost-operator-binding
  namespace: ghost
subjects:
- kind: ServiceAccount
  name: ghost-sa
  namespace: ghost
  apiGroup: ""
roleRef:
  kind: Role
  name: ghost-operator
  apiGroup: ""
```

Una vez hayamos aplicado estos ficheros, podemos cambiar de contexto a la cuenta de ghost con ```kubectl config use-context ghost``` y verificar qué acciones podemos y cuales no podemos hacer.

> NOTA: Estoy utilizando los ficheros de mi repositorio de ejemplo y el acortador de URLs Opensource Kutt para que el post quede más pequeño.

```bash
# Desplegamos un Secret y un Configmap
kubectl apply -f https://kutt.it/SPtVom -n ghost

kubectl apply -f https://kutt.it/gs7T79 -n ghost

# Desplegamos un Deployment que utiliza dichos objetos
kubectl apply -f https://kutt.it/w2VfXM -n ghost
```

Como podemos ver, los permisos funcionan correctamente. ¿Pero y si intentamos desplegar un _StatefulSet_?

```bash
kubectl apply -f https://kutt.it/GbZiMq -n ghost
statefulset.apps/nginx-with-state created

kubectl get pvc -n ghost
NAME                     STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS    AGE
www-nginx-with-state-0   Pending                                      local-storage   9s
```

El PVC está en _Pending_ porque nuestro _StorageClass_ no permite el autoaprovisionamiento de discos. Si intentamos crear el _PersistentVolume_ veremos que no tenemos permisos y que debe crearlo alguien que si pueda.

Si intentamos crear otros objetos como _Daemonsets_, un _Service_ o intentamos modificar nuestros permisos, también recibiremos un error.

```bash
# Intentamos crear un Daemonset
kubectl apply -f https://kutt.it/cJeX5g -n ghost

Error from server (Forbidden): error when retrieving current configuration of:
Resource: "apps/v1, Resource=daemonsets", GroupVersionKind: "apps/v1, Kind=DaemonSet"
Name: "fluentd", Namespace: "ghost"
from server for: "basic-fluentd-daemonset.yml": daemonsets.apps "fluentd" is forbidden: User "system:serviceaccount:ghost:ghost-sa" cannot get resource "daemonsets" in API group "apps" in the namespace "ghost"

# Intentamos crear un Service
kubectl apply -f https://kutt.it/9QAO3m -n ghost

Error from server (Forbidden): error when retrieving current configuration of:
Resource: "/v1, Resource=services", GroupVersionKind: "/v1, Kind=Service"
Name: "nginx", Namespace: "ghost"
from server for: "basic-nginx-service-nodeport.yml": services "nginx" is forbidden: User "system:serviceaccount:ghost:ghost-sa" cannot get resource "services" in API group "" in the namespace "ghost"

# Intentamos añadirnos al grupo de cluster-admins de RBAC
kubectl create clusterrolebinding ghost-cluster-admin-binding --clusterrole=cluster-admin --user=ghost-sa

Error from server (Forbidden): clusterrolebindings.rbac.authorization.k8s.io is forbidden: User "system:serviceaccount:ghost:ghost-sa" cannot create resource "clusterrolebindings" in API group "rbac.authorization.k8s.io" at the cluster scope

```

Por último, podemos ver que los permisos generales funcionan al listar los pods de otros namespaces como _default_

```bash
# Aunque no hay nada
kubectl get pods -n default

No resources found in default namespace
```

## Conclusiones
El uso de RBAC nos abre un abanico infinito de posibilidades: podemos utilizarlo para dividir las responsabilidades en un grupo amplio de trabajo (un equipo de seguridad puede gestionar los _Roles_ y sus asignaciones, un equipo de almacenamiento los volúmenes y otro equipo los aplicativos y los _Services_) o simplemente como en mis ejemplos, podemos utilizarlo para dividir las responsabilidades por aplicación y que diferentes equipos multidisciplinares trabajen sobre la misma infraestructura.

Sin embargo, sólo soluciona parte de los problemas de compartir infraestructura: nada limita que un pod de un namespace se comunique con otro pod de otro namespace y esto puede provocar problemas de seguridad, pero eso dará para otro post...

Espero que os haya gustado y... ¡os veo en el pŕoximo post!


## Documentación

* [Cluster Multi-tenancy in GCP (ENG)](https://cloud.google.com/kubernetes-engine/docs/concepts/multitenancy-overview)

* [Cuotas en _namespaces_ de Kubernetes (ENG)](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/quota-memory-cpu-namespace/)

* [Autenticación en Kubernetes (ENG)](https://kubernetes.io/docs/reference/access-authn-authz/authentication/#authentication-strategies)

* [Accediendo a la API de Kubernetes (ENG)](https://kubernetes.io/docs/tasks/administer-cluster/access-cluster-api/)

* [Modos de autorización en Kubernetes (ENG)](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)

* [RBAC en Kubernetes (ENG)](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

* [Configuración de RBAC en nuestro clúster de Kubernetes, por Bitnami (ENG)](https://docs.bitnami.com/kubernetes/how-to/configure-rbac-in-your-kubernetes-cluster/)

* [Roles por defecto en clústers de Kubernetes (ENG)](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#discovery-roles)

* [Referencia de las APIs de Kubernetes (ENG)](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.19/)

* [Repositorio de plantillas de Kubernetes](https://gitlab.com/tangelov/proyectos/-/tree/master/templates/kubernetes)

Revisado a 01-03-2021
