---
title: "Kubernetes (III): migrando una aplicación a Kubernetes"
slug: kubernetes-iii
authors:
  - tangelov
date: 2020-03-18T20:00:00+02:00
tags:  ["kubernetes", "docker", "contenedores"]
categories: ["cloud"]
draft: false
---

Tras haber aprendido algunos conceptos, ahora vamos a realizar un ejercicio similar al que podríamos tener que hacer en la vida real. La idea es coger una aplicación _tradicional_ y ejecutarla de la mejor manera posible en un clúster de Kubernetes.

La aplicación elegida es [Traccar](https://www.traccar.org/), una aplicación rusa de seguimiento GPS que cumple muchos de los puntos que buscaba:

* Es una aplicación con diferentes capas: tiene un frontal web, un backend de procesamiento y necesita una base de datos relacional para funcionar. Su frontal y su backend se encuentran acoplados en el mismo paquete.

* Está bien mantenida por sus desarrolladores y ofrece imágenes Docker oficiales (para no empezar todo el proceso de 0).

* Su frontend web está desarrollado actualmente en tecnologías no punteras como el gestor de componentes Sencha.

* Su backend está desarrollado en Java, sin un diseño específico para adaptarse _per se_ a un sistema como Kubernetes: gestiona cachés internas en local haciendo problemático su escalado.


¡Manos a la obra!

<!--more-->

## _Kubernetizando Traccar_

### Base de datos
Nunca debemos empezar la casa por el tejado: primero vamos a crear una base de datos relacional a la que conectaremos el backend de Traccar. Si desplegáramos el sistema en una nube pública podríamos utilizar alguna base de datos gestionada por el proveedor, pero por el momento vamos a seguir utilizando MicroK8s.

Por defecto Traccar utiliza una base de datos embebida en aplicaciones Java, llamada H2, pero también soporta otros sistemas como MySQL, PostgreSQL o SQL Server. Debido a su sencillez y consumo en este caso vamos a utilizar MySQL.

MySQL es una aplicación muy dependiente del estado por lo que lo primero que vamos a hacer es generar un _StatefulSet_ donde despleguemos nuestra base de datos, aplicando algunas recomendaciones extra. Estos serían los pasos a realizar:

1 - Creamos un [volumen](https://gitlab.com/tangelov/proyectos/-/raw/master/templates/kubernetes/traccar/basic-yaml/mysql-storage.yml) donde almacenar las bases de datos de MySQL.

2 - Creamos un [secreto](https://gitlab.com/tangelov/proyectos/-/raw/master/templates/kubernetes/traccar/basic-yaml/mysql-configmaps-secrets.yml) con el nombre de la BBDD y las contraseñas que vamos a necesitar.

3 - Creamos un [configmap](https://gitlab.com/tangelov/proyectos/-/raw/master/templates/kubernetes/traccar/basic-yaml/mysql-configmaps-secrets.yml) con la configuración extra [recomendada por Traccar para MySQL](https://www.traccar.org/mysql-optimization/)

4 - Creamos _[StatefulSet](https://gitlab.com/tangelov/proyectos/-/raw/master/templates/kubernetes/traccar/basic-yaml/mysql-def.yml)_ de MySQL 5.7

> Los secretos contienen el nombre (_traccar-db_), usuario (_traccaruser_) y contraseña (_traccarpassword_) de la base de datos de Traccar, así como la contraseña de MySQL de root (_traccarrootpassword_).


> Recordar también que si utilizamos las plantillas tenemos que cambiar algunas variables en las mismas.

Cada tipo de recurso tiene un link que contiene el YAML necesario para crearlo. Podemos ver que todo se ha ejecutado correctamente con el siguiente comando:

```bash
# Listamos todos los StatefulSets, ConfigMaps, Secretos, PersistentVolumeClaim y PersistentVolumes
kubectl get statefulsets,configmaps,secrets,pvc,pv

NAME                     READY   AGE
statefulset.apps/mysql   1/1     7m47s

NAME                                          DATA   AGE
configmap/mysql-config                        1      36m

NAME                                                       TYPE                                  DATA   AGE
secret/default-token-qnhrx                                 kubernetes.io/service-account-token   3      15d
secret/mysql-credentials                                   opaque                                4      36m

NAME                                          STATUS   VOLUME         CAPACITY   ACCESS MODES   STORAGECLASS    AGE
persistentvolumeclaim/mysql-storage-mysql-0   Bound    local-volume   10Gi       RWO            local-storage   27m

NAME                            CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                           STORAGECLASS    REASON   AGE
persistentvolume/local-volume   10Gi       RWO            Retain           Bound    default/mysql-storage-mysql-0   local-storage            40m
```

Si ahora nos metemos dentro del pod y usamos las credenciales que hemos pasado como secretos para conectarnos, veremos que nuestra base de datos ha sido creada correctamente:

```bash
# Nos conectamos al pod del StatefulSet de MySQL
kubectl exec -ti mysql-0 bash

root@mysql-0:/# mysql -u traccaruser -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 2
Server version: 5.7.33 MySQL Community Server (GPL)

Copyright (c) 2000, 2021, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> SHOW databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| traccar-db         |
+--------------------+
2 rows in set (0.00 sec)

```

### Traccar Server
Ya tenemos una base de datos funcional, ahora vamos a hacer lo mismo con el backend de Traccar. La primera idea que podríamos tener sería crear otro _StatefulSet_, pero de cara a hacerlo más manejable en el futuro vamos a utilizar un _Deployment_.

Lo primero que debemos hacer es generar un _service_ para que la IP de nuestro servidor MySQL dentro de Kubernetes sea estática.

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: mysql
  labels:
    app: mysql
spec:
  clusterIP: 10.152.183.254
  ports:
  - port: 3306
    protocol: TCP
  selector:
    app: mysql
```

Este fichero nos generará un servicio que permite que otras máquinas se conecten al MySQL a través de la IP 10.152.183.254.

> Es posible que el rango de ClusterIP sea diferente en el caso del lector y que haya que modificar las IPs. Para ello podemos ejecutar el comando _kubectl get svc --all-namespaces_ y ver el rango en que rango están otros services.

```bash
# Aplicamos el fichero recién creado
kubectl apply -f $FICHERO_MYSQL_SERVICE
service/mysql created

# Vemos que ahora tenemos un servicio con IP elegida
kubectl get svc --all-namespaces

NAME                   TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
kubernetes             ClusterIP   10.152.183.1     <none>        443/TCP    22d
mysql                  ClusterIP   10.152.183.254   <none>        3306/TCP   20d
```

Tras fijar la IP de la base de datos, vamos a generar el fichero de configuración utilizado por Traccar para configurarse.  Siguiendo los datos del [siguiente enlace](https://www.traccar.org/mysql/), podemos ver que su fichero de configuración es un XML localizado en la ruta _/opt/traccar/conf/traccar.xml_ y que el puerto que utiliza el servicio es el 8082.

Ahora tenemos que crear un fichero XML de nombre traccar.xml con la siguiente configuración:

```xml
<?xml version='1.0' encoding='UTF-8'?>

<!DOCTYPE properties SYSTEM 'http://java.sun.com/dtd/properties.dtd'>

<properties>
    <entry key='config.default'>./conf/default.xml</entry>

    <entry key='database.driver'>com.mysql.jdbc.Driver</entry>
    <entry key='database.url'>jdbc:mysql://10.152.183.254:3306/traccar-db?serverTimezone=UTC&amp;useSSL=false&amp;allowMultiQueries=true&amp;autoReconnect=true&amp;useUnicode=yes&amp;characterEncoding=UTF-8&amp;sessionVariables=sql_mode=''</entry>
    <entry key='database.user'>traccaruser</entry>
    <entry key='database.password'>traccarpassword</entry>

</properties>
```

Con este fichero, vamos a generar un secreto para guardar a buen recaudo nuestra configuración, puesto que almacena credenciales que no queremos que estén en texto plano:

```bash
kubectl create secret generic traccar-config --from-file=./traccar.xml
secret/traccar-config created
```

Ya tenemos todas las dependencias necesarias para crear nuestro _Deployment_:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: traccar-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: traccar
  template:
    metadata: 
      labels:
        app: traccar
    spec:
      containers:
      - name: traccar-backend
        image: traccar/traccar:4.12-debian
        ports:
          - containerPort: 8082
        volumeMounts:
        - name: traccar-conf
          mountPath: /opt/traccar/conf/traccar.xml
          subPath: traccar.xml
      volumes:
      - name: traccar-conf
        secret:
          secretName: traccar-config
---
apiVersion: v1
kind: Service
metadata:
  name: traccar-backend
  labels:
    app: traccar
spec:
  clusterIP: 10.152.183.250
  ports:
  - port: 8082
    protocol: TCP
  selector:
    app: traccar
```

Para comprobar que todo funciona perfectamente, vamos a ver los logs que el estado de los pods es _Running_ y que podemos acceder al endpoint del puerto 8082.

```bash
# Vemos que ambos pods se encuentran en el estado deseado
kubectl get pods
NAME                                      READY   STATUS    RESTARTS   AGE
mysql-0                                   1/1     Running   0          10m
traccar-backend-7f8d8fcd5-c8kmq           1/1     Running   0          8m5s

# No vemos nada raro en los logs del servicio
kubectl logs deployment/traccar-backend
Loading class `com.mysql.jdbc.Driver'. This is deprecated. The new driver class is `com.mysql.cj.jdbc.Driver'. The driver is automatically registered via the SPI and manual loading of the driver class is generally unnecessary.

# Ahora generamos un pod suelto con curl para comprobar que el endpoint funciona, puesto que todavía no es accesible desde el clúster
kubectl run -i --tty curl --image=curlimages/curl --restart=Never -- sh

/ $ curl 10.152.183.250:8082
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Traccar</title>
<link rel="icon" sizes="192x192" href="/icon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="app.css">
</head>
<body>
<div id="spinner"></div>
<div id="attribution">Powered by <a href="https://www.traccar.org/">Traccar GPS Tracking System</a></div>
<script id="loadScript" src="load.js"></script>
</body>
</html>
```

### Traccar Web
Ya tenemos una base de datos y un backend funcionando, así que ahora vamos a ponernos con la interfaz web.

Ésta está integrada dentro del pod de Backend y se encuentra habilitada por defecto, escuchando en el puerto 8082. Sin embargo, para acceder al servicio necesitamos crear algún punto de acceso puesto que ahora mismo sólo es accesible desde el interior del clúster. Para poder utilizarlo, vamos a crear un Ingress (también podríamos utilizar un servicio del tipo LoadBalancer si nuestro proveedor de K8s lo soportara).

Como estamos utilizando Microk8s, el endpoint de nuestro Ingress es siempre la dirección _http://127.0.0.1_ así que vamos a editar nuestro fichero /etc/hosts para utilizar un dominio personalizado:

```bash
vim /etc/hosts

127.0.0.1       traccar.prueba.test
```

Finalmente creamos un [ingress](https://gitlab.com/tangelov/proyectos/-/raw/master/templates/kubernetes/traccar/basic-yaml/traccar-web.yml) con el siguiente contenido:

```yaml
---
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: traccar-web
spec:
  rules:
    - host: traccar.prueba.test
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: traccar-backend
                port:
                  number: 8082
```

Si ahora abrimos un navegador y ponemos http://traccar.prueba.test veremos lo siguiente:

![traccar-web](https://storage.googleapis.com/tangelov-data/images/0028-00.png)

Y si nos metemos dentro de la aplicación con _admin_/_admin_ podemos ver que nuestro traccar ya es funcional :)

![traccar-web-full](https://storage.googleapis.com/tangelov-data/images/0028-01.png)


## Conclusiones
Con esto ya hemos terminado una migración de un servicio tradicional a Kubernetes. Sin embargo me interesa remarcar que __Kubernetes no es una panacea__ y aunque hemos logrado desacoplar ciertas partes de la herramienta y nuestro servicio se autorregenerará en caso de caída, seguimos teniendo limitaciones debido a la naturaleza de la aplicación:

* Traccar no soporta ningún sistema de clusterización o multinodo por lo que aunque teóricamente podríamos escalar el servicio, se comportaría como distintos servicios compartiendo una misma base de datos. Si instalásemos un cliente, éste solo aparecería en uno de los nodos.

* Traccar tiene acoplado el frontend y el backend y no podemos escalarlos de forma independiente.

Gestionar las espectativas depositadas en una "nueva" tecnología es tan importante como explotar los beneficios que aporta y tenemos que entender que nos vamos a encontrar con problemas nuevos que antes no teníamos y que van a requerir de aprendizaje, replantearnos cosas y aportar nuevas soluciones.

Un saludo a todos!


## Documentación

* [Página web oficial de Traccar (ENG)](https://www.traccar.org/)

* [Documentación oficial de Traccar (ENG)](https://www.traccar.org/documentation/)

* Dockers utilizados (ENG): [MySQL](https://hub.docker.com/r/mysql/mysql-server/) y [Traccar](https://hub.docker.com/r/traccar/traccar)

* [Como ejecutar MySQL en Openshift con StatefulSets (ENG)](https://www.redhat.com/en/blog/how-run-mysql-pod-ocp-using-ocs-and-statefulsets)

* [Referencia de configuración de Traccar (ENG)](https://www.traccar.org/configuration-file/)

* [Arquitectura de la plataforma Traccar (ENG)](https://www.traccar.org/architecture/)


Revisado a 01-03-2021
