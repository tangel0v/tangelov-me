---
title: "Vault (I): introducción a la gestión de secretos"
slug: vault-i
date: 2020-10-14T08:00:00+02:00
authors:
  - tangelov
tags: ["vault", "security"]
categories: ["cloud"]
draft: false
---


Considero a Hashicorp una de las empresas que más están innovando actualmente: su compromiso con los entornos multi-nube (privada, pública y mixta) y su suite de herramientas están facilitando mucho la transición entre proveedores y reduciendo la curva de aprendizaje de la nube.

<!--more-->


## Introducción
Hashicorp tiene distintas herramientas: algunas como Terraform son para la administración y despliegue de infraestructura, pero otras como Consul son un _Service Mesh_ y _Nomad_ es un orquestador de aplicaciones (competencia de Kubernetes). En este artículo, vamos a hablar de una en concreto, Hashicorp Vault.

_Hashicorp Vault_ es una herramienta para la gestión, control de acceso y almacenamiento de _secretos_. Un secreto puede ser cualquier cosa que sea sensible: un certificado, una contraseña o cualquier dato que necesitemos en una aplicación para que ésta funcione correctamente y tenga que guardarse a buen recaudo.

A día de hoy todos, los proveedores de nube pública tienen algún sistema de gestión y almacenamiento de secretos como servicio. Google Cloud y Amazon Web Services tienen sus respectivos _Secret Manager_ y Microsoft Azure tiene su _Azure Key Vault_. Son servicios relativamente sencillos de usar: almacenamos secretos y podemos tanto rotarlos como consumirlos a través de una API. Vault es una de las pocas alternativas si queremos desplegar en nuestro CPD un gestor de secretos y aunque podemos usar el de cualquier nube pública, su uso nos ata bastante a dicho proveedor.

Todo depende de las necesidades y requisitos que tengamos.

![secretos-multinube](https://storage.googleapis.com/tangelov-data/images/0036-00.png)


## Descripción del producto
Vault está diseñado para ser seguro y extensible para facilitar la creación, gestión y renovación de secretos. Para entender cómo está estructurado, Hashicorp proporciona un esquema a alto nivel de su herramienta.


### Arquitectura
Vault está diseñado para ser seguro, extensible y facilitar la creación, gestión y renovación de secretos. Hashicorp provee un esquema a alto nivel sobre su funcionamiento:

![arquitectura-vault](https://storage.googleapis.com/tangelov-data/images/0036-01.png)

Vemos que la aplicación tiene tres partes diferenciadas:

* Una API Rest que funciona a través del protocolo HTTPS.

* Varios elementos dentro de la sección llamada _Barrier_ y que constituye el núcleo de la aplicación. Hay un servicio de generación de tokens, varios servicios de auditoría, los sistemas de gestión de secretos, etc.

* El sistema de almacenamiento o _Storage Backend_ donde se almacenan los secretos.

Vault considera que el sistema de almacenamiento no es confiable por lo que cifra su contenido con una clave privada. Antes de arrancar la aplicación, ésta debe tener configurado algún _Storage Backend_ y sólo después de arrancar, Vault arranca su API para que los clientes puedan interactuar con ella.

Una vez inicializamos Vault, el _almacén de secretos_ arranca en estado _sealed_. En este estado, los secretos que guarda no son accesibles y necesitamos desbloquearlo para comenzar a utilizarlo.

Para desbloquearlo, necesitamos introducir alguna de las claves que nos ha generado Vault. Por defecto, utiliza una llave maestra dividida en cinco partes y es necesario introducir al menos tres para abrir el _cofre_. Si alguien quiere más información acerca del algoritmo de claves utilizado, podemos leer más [aquí](https://en.wikipedia.org/wiki/Shamir's_Secret_Sharing).

Tras desbloquear la aplicación, Vault pasará a estar en estado _unseal_, cargará su configuración y podremos empezar a interaccionar con sus motores de secretos, sistemas de auditoría y de autenticación/autorización.

Utiliza un sistema que deniega cualquier acceso salvo que éste haya sido __explícitamente__ permitido. De esta forma sólo los usuarios con los permisos correctos, pueden habilitar, deshabilitar o interactuar con uno o más motores de secretos.

Cuando un usuario o un robot intenta acceder a Vault sigue, a grosso modo, este proceso:

1. En primer lugar, el usuario se autentica contra la aplicación.

2. Después se valida su nivel de accesos a través de las políticas que hayamos definido (funcionan como una especie de ACLs). Las políticas creadas habilitan el acceso de forma explícitamente y deniegan cualquier tipo de acceso de omisión.

3. Si todo es correcto, se genera un token válido que nos autoriza ante la herramienta y nos permite realizar las acciones asignadas según las políticas que tengamos asignadas.

Si tenemos interés y queremos ver más información al respecto, podemos hacer click [aquí](https://www.vaultproject.io/docs/internals/architecture).


### Uso de Vault
Tras un ligero paso por su arquitectura, ahora vamos a explicar un poco cual es el funcionamiento de Vault:

![uso-de-vault](https://storage.googleapis.com/tangelov-data/images/0036-02.png)

1. Tras arrancar Vault y hacer el _unseal_, lo primero que hace el servidor es conectarse al sistema de almacenamiento. De esta forma, Vault ya podrá leer y escribir en él.

2. Una vez hemos desbloqueado Vault, tenemos que configurar alguno de sus motores de secretos y guardar algún secreto. El más habitual es el sistema de clave-valor, pero existen [muchos otros](https://www.vaultproject.io/docs/secrets).

3. Un usuario puede acceder ahora a dicho secreto a través de la API de Vault.


## Instalación y configuración
Cuando comencé este post hace meses, la instalación de la aplicación se realizaba en una máquina virtual, pero la plataforma ha evolucionado y ahora vamos a hacerlo sobre un clúster de Kubernetes.

La idea a tratar a lo largo de varios post es la siguiente:

* Desplegamos Vault en un clúster local y utilizamos como sistema de almacenamiento un bucket de Google Cloud Platform.

* Después configuramos varios motores de secretos, para que puedan ser utilizados por una aplicación.

* En tercer lugar, habilitamos alguno de los sistemas de autenticación soportados por Vault y le asignamos permisos para poder utilizar uno o más motores de secretos.

La idea es la siguiente:

* Desplegamos Vault en un clúster local y utilizamos como sistema de almacenamiento un bucket de Google Cloud Storage.

* Después conectamos la aplicación contra varios motores de secretos (Clave-Valor, Amazon Web Services, Microsoft Azure y Google Cloud Platform).

* En tercer lugar, creamos algunas políticas de acceso y probamos su funcionamiento.

* En el último punto, desplegamos una aplicación e inyectamos los secretos automáticamente en ella. Verificamos el rotado de secretos y las diferentes posibilidades que tenemos al respecto.


### Instalación con Helm
Para instalar Vault, vamos a utilizar Helm, el gestor de aplicaciones sobre Kubernetes. Podemos instalarlo siguiendo las instrucciones de [su propia página](https://helm.sh/docs/intro/install/).

> La versión de Helm que debemos desplegar es la versión 3. La versión 2 se encuentra en modo de mantenimiento y va a ser descontinuada en diciembre de 2020.

Una vez tenemos Helm en nuestro PC, necesitamos cumplir los siguientes prerrequisitos:

* Tener previamente creado Un bucket de Google Cloud Storage para utilizarlo como sistema de almacenamiento.

* Una llave JSON de una cuenta de servicio con permisos para poder leer y escribir en dicho bucket.

* El fichero de variables de ejemplo para instalar Vault, que podemos descargar de [aquí](https://gitlab.com/tangelov/proyectos/-/raw/master/templates/helm/helm-vault-values.yaml).

> __NOTA__: No olvideis cambiar la variable GCP_BUCKET y GCP_PROJECT_ID por el nombre del bucket y el proyecto que vayais a utilizar en la sección de _config_.

Con los prerrequisitos cumplidos, podemos proceder a su instalación.

```bash
# Creamos un namespace para desplegar Vault en él
kubectl create namespace vault

# Creamos el secreto con la llave de GCP para que Vault la utilice.
kubectl create secret generic gcs-key --from-file=key.json -n vault

# Añadimos el repositorio oficial de Helm de Hashicorp
helm repo add hashicorp https://helm.releases.hashicorp.com && helm repo update

# Desplegamos la herramienta con el siguiente comando
helm install vault hashicorp/vault --values myvalues-vault.yaml -n vault
```

Si todo ha ido bien, veremos que que los pods se encuentran en este estado:

```bash
kubectl get pods -n vault

NAME                                    READY   STATUS    RESTARTS   AGE
vault-0                                 0/1     Running   0          94s
vault-1                                 0/1     Running   0          94s
vault-2                                 0/1     Running   0          94s
vault-agent-injector-846dbdc57b-xxx9g   1/1     Running   0          94s
```

Vault está en ejecución, pero todavía no es accesible: no está en estado _READY_. Es algo normal, puesto que ni hemos desbloqueado la herramienta y ni está inicializada.

Comenzamos inicializando Vault: para ello ejecutamos el comando _vault init_ dentro de uno de los pods del clúster, indicando el número de claves a generar y el número mínimo de ellas necesarias para desbloquear el baúl. En este laboratorio vamos a simplificar un poco el sistema de claves y sólo vamos a generar una clave, pero para entornos productivos lo recomendable es crear un mínimo de cinco y que sea necesario el uso de al menos tres para lograr un desbloqueo satisfactorio.

```bash
# Inicializamos Vault con una sola clave y guardamos el contenido en un fichero JSON
kubectl exec vault-0 -n vault -- vault operator init -key-shares=1 -key-threshold=1 -format=json > vault-keys.json
```

En este fichero se han almacenado las claves de desbloqueo del baúl, los tokens de acceso y las claves de recuperación (si las creamos). Si abrimos el fichero, veremos algo parecido a esto:

```json
{
  "unseal_keys_b64": [
    "ABCDEFGHIJKLMN//OPQRSTUVWXYZABCDEFGH+IJKLMN="
  ],
  "unseal_keys_hex": [
    "MUCHOSNUMEROSENHEXADECIMAL"
  ],
  "unseal_shares": 1,
  "unseal_threshold": 1,
  "recovery_keys_b64": [],
  "recovery_keys_hex": [],
  "recovery_keys_shares": 5,
  "recovery_keys_threshold": 3,
  "root_token": "A.BCDEFGHIJKLMNOPQRSTUVWXY"
}

```

Ahora utilizando el token de _unseal_, vamos a desbloquear todos los nodos del cluster:

```bash
# Obtenemos el contenido del fichero JSON y lo guardamos en una variable
VAULT_UNSEAL=$(cat vault-keys.json | jq -r ".unseal_keys_b64[]")

# Abrimos el baúl con la clave que acabamos de sacar
# Debemos repetirlo por cada uno de los nodos del clúster de Vault
kubectl exec vault-0 -n vault -- vault operator unseal $VAULT_UNSEAL
kubectl exec vault-1 -n vault -- vault operator unseal $VAULT_UNSEAL
kubectl exec vault-2 -n vault -- vault operator unseal $VAULT_UNSEAL

# Al ejecutar el comando anterior, veremos algo similar a lo siguiente
Key                    Value
---                    -----
Seal Type              shamir
Initialized            true
Sealed                 false
Total Shares           1
Threshold              1
Version                1.13.1
Storage Type           gcs
Cluster Name           vault-cluster-xxxxxxxx
Cluster ID             xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
HA Enabled             true
HA Cluster             https://vault-0.vault-internal:8201
HA Mode                standby
Active Node Address    http://10.244.120.76:8200

```

Nuestro clúster ya está inicializado y en estado _unsealed_ por lo que ya podemos comenzar a utilizarlo.

### Primeros pasos con Hashicorp Vault
Vault ya está desbloqueado, pero antes de comenzar a utilizarlo necesitamos entender un poco más como funciona.

* Vault proporciona acceso a diferentes motores de secretos: podemos utilizarlo para generar secretos de diferentes tipos. Cada motor se almacena en forma de un _path_ interno. El más básico es sistema de clave-valor, pero hay una gran cantidad de ellos.

* Cualquier usuario o aplicación que interactue con alguno de los motores de secretos necesita autenticarse previamente y estar autorizado en el motor de secretos. Cuando inicializamos Vault, recibimos un token que podemos utilizar para configurar otros sistemas de autenticación.

El flujo de una aplicación podría ser el siguiente:

![app-vault-example](https://storage.googleapis.com/tangelov-data/images/0036-03.png)

Ahora podemos loguearnos dentro del clúster y a habilitar un sistema de autenticación.

```bash
# Obtenemos las credenciales y las almacenamos en una variable
VAULT_TOKEN=$(cat vault-keys.json | jq -r ".root_token")

# Accedemos con Kubectl a uno de los nodos del clúster
kubectl exec -it vault-0 -n vault -- /bin/sh

# Nos logueamos con el token que acabamos de obtener
/ $ vault login

Token (will be hidden): 
Success! You are now authenticated. The token information displayed below
is already stored in the token helper. You do NOT need to run "vault login"
again. Future Vault requests will automatically use this token

# Habilitamos el sistema de autenticación de Kubernetes
/ $ vault auth enable kubernetes

Success! Enabled kubernetes auth method at: kubernetes/
```

Y hasta aquí va a llegar el post de hoy. En siguientes posts, trataremos la gestión de la autenticación y la autorización contra Vault, así cómo el uso de diferentes tipos de secretos. ¡¡Hasta la próxima!!


## Documentación

* [Valores por defecto para instalar Vault a través de Helm](https://raw.githubusercontent.com/hashicorp/vault-helm/master/values.yaml)

* [Configuración de Hashicorp Vault (ENG)](https://www.vaultproject.io/docs/configuration)

* [Configuración a través de Helm de Hashicorp Vault (ENG)](https://www.vaultproject.io/docs/platform/k8s/helm/configuration)

* [Tutorial sobre cómo instalar Vault en Minikube (ENG)](https://learn.hashicorp.com/tutorials/vault/kubernetes-minikube)

* [Arquitectura de Hashicorp Vault (ENG)](https://learn.hashicorp.com/tutorials/vault/reference-architecture)

* [Arquitectura a bajo nivel de Hashicorp Vault (ENG)](https://www.vaultproject.io/docs/internals/architecture)

Revisado a 01-05-2023
