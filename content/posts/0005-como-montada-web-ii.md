---
title: "Como está montada esta web (II): Nikola y Google App Engine"
slug: como-montada-web-ii
authors:
  - tangelov
date: 2018-02-20T23:00:00+02:00
tags:  ["gcp", "nikola"]
categories: ["cloud"]
draft: false
---

En el primer post explicamos las tecnologías utilizadas para desarrollar y hospedar esta web. En esta sección profundizaremos un poco más y daremos los pasos necesarios para que nuestro código HTML estático funcione perfectamente en Google App Engine.

<!--more-->

## Configuración en conf.py
La documentación de Nikola es muy buena y puede consultarse [aquí](https://getnikola.com/conf.html). Trata prácticamente todo lo configurable en la aplicación, por lo que me voy a centrar sólo en los cambios necesarios (no en el título, o en como cambiar de tema) para que lo generado funcione en la nube de Google.

> __Nota del autor__: Este artículo no representa el estado actual de la web puesto que se ha migrado a Hugo a lo largo del 2020. Para saber más sobre el proceso de migración, puede acceder al [siguiente post](https://tangelov.me/posts/tangelov-en-hugo.html).

Google App Engine no soporta por defecto _Pretty URLs_ por lo que debemos deshabilitalas en Nikola.
![Pretty URLS](https://storage.googleapis.com/tangelov-data/images/0005-00.png)

_Pretty URLs_ son las configuraciones que nos permiten que cuando accedemos a una página web, no tengamos que poner siempre .html al final de cada fichero. Se entiende mucho mejor con un ejemplo: si anteriormente para acceder al post anterior, lo hacíamos a través de la URL https://tangelov.me/como-montada-web-i/ ahora lo haremos a través de https://tangelov.me/como-montada-web-i/index.html .

Este cambio habrá roto algunas de las configuraciones que deberemos cambiar. Todas las referencias internas que no apuntasen al .html directamente fallarían y de caja es lo que pasará con algunas de las URLs de la estructura del tema (archivo, categorías, etc). Procedemos a cambiarlas para que apunten a sus HTMLs.
![Rutas internas](https://storage.googleapis.com/tangelov-data/images/0005-01.png)

En mi caso, también cambié el archivo para que fuese un sólo fichero y darle más homogeneidad al conjunto.
![Archivo](https://storage.googleapis.com/tangelov-data/images/0005-02.png)

Con esto, nuestro código ya funcionará en GAE, pero también necesitamos desplegarlo.

## Configuración de Google App Engine (GAE)
Como ya se ha comentado, Google App Engine es una Plataforma como servicio que permite a desarrolladores, publicar sus páginas web, proporcionando autoescalado, certificados SSL (vía Let's Encrypt), protección ante caídas de servicio... Google ofrece este servicio en dos modalidades diferentes: _standard_ y _flexible_

Como nosotros utilizamos HTML puro, podemos usar el _standard_. Éste se diferencia del flexible por una cantidad más limitada de frameworks que se pueden ejecutar. Actualmente podemos usar Python (2.7, 3.X), Java (8, 11), PHP (5.5, 7.2, 7.3 o 7.4), NodeJS (10, 12, 14 o 16), Ruby (2.5, 2.6 y 2.7) y Go (1.11 o 1.12+).

Antes de realizar el despliegue, necesitamos crear la _"infraestructura"_ en Google Cloud que nos permita hacerlo. En este caso caso concreto la he dividido en dos partes:

* El servicio de Google App Engine en Europa.

* Un _bucket_ de Google Cloud Storage donde se almacenan los ficheros estáticos no generados por Nikola.

En primer lugar, si no lo hemos realizado antes, debemos configurar la CLI de GCP en nuestro PC (escribí [aquí](https://tangelov.me/posts/conectar-gcp-con-linux.html) sobre ello) y realizar las siguientes operaciones (la primera vez).
```bash
# Generamos el bucket para almacenar todo el contenido estático no generado por Nikola
gsutil mb -p $nombre_proyecto -c $tipo -l $localizacion gs://$nombre_bucket/

# Damos permisos de lectura para todo el mundo (así es público)
gsutil iam -r ch allUsers:objectViewer gs://$nombre_bucket

# Creamos el servicio de App Engine
gcloud app create --region=europe-west
```

Con esto ya tendríamos la estructura previa, ahora vamos a generar el fichero app.yaml que necesita App Engine para gestionarlo y a agregar una ligera explicación:

```yaml
runtime: python27
api_version: 1
threadsafe: true
instance_class: B1

handlers:
- url: /
  static_files: index.html
  upload: index.html
  secure: always

- url: /(.*)
  static_files: \1
  upload: (.*)
  secure: always

basic_scaling:
  max_instances: 1
```

En este fichero, le estamos indicando al GAE como queremos que se comporte con nuestro código:

* El _runtime_ se corresponde al framework o lenguaje que estará corriendo por debajo. Por defecto, usa python27 y es el que vamos a usar.

* _api_version_ lo dejamos en 1.

* _threadsafe_ se utiliza para que nuestra aplicación sea capaz de realizar peticiones concurrentes.

* Los _handlers_ se corresponden con el contenido de la aplicación. En este caso le estamos diciendo que suba el index.html a la ruta raiz y que suba todo el resto del contenido. _secure_ indica que siempre se utilizará HTTPS.

* Por último tenemos el autoescalado: GAE soporta diferentes tipos de autoescalado y yo he elegido el tipo básico y limitarlo a una sola instancia para _controlar la factura al máximo_. Por ello _instance\_class_ apunta a una B1.

Colocamos dicho fichero en la carpeta _~/files_ dentro de nikola para que cuando ejecutemos las build, lo mueva él mismo a la raíz del código generado.

## Despliegues
Personalmente intento organizar el contenido del blog de forma física y lógica: por ello los posts y todos los ficheros asociados a los mismos tienen un código numérico. De esta forma, el post de código 0001-_NombredelPost_ tendrá relacionadas todos los ficheros que comiencen por 0001-*.

Para este ejemplo, vamos a suponer que hemos escrito un nuevo post, que hemos subido todos los ficheros al bucket de Google y que hemos modificado las URLs dentro del post para apuntar hacia allí.

Nikola tiene cosas muy chulas y una de ellas es un soporte nativo para despliegues, pudiendo añadir configuraciones extra que nos los hagan. Tan sólo tenemos que añadirlas al archivo _conf.py_:

![Despliegues en Nikola](https://storage.googleapis.com/tangelov-data/images/0005-03.png)

Cuando ejecutemos ``nikola deploy gcloud`` nos moveremos a la carpeta _output_ y desplegaremos el código ahí generado.

Resumiendo:

* Cargamos el virtualenv del nikola (``source $ruta_del_virtualenv/bin/activate``)

* Añadimos un post (``nikola new_post -f markdown``) y lo editamos (``vi $nombre_del_post``)

* Una vez que estamos contentos con el contenido, confirmamos el cambio (``git commit -a -S -m "Algo sobre el post"``) y lo subimos al repositorio remoto (``git push``)

* Subimos los imágenes a un bucket de Google Cloud Storage (``gsutil rsync -d ~/images/ gs://$nombre_del_bucket/images``)

* ``nikola build`` para generar el HTML (a veces hago un ``nikola serve`` para probar el contenido en local)

* Lanzamos el despliegue: ``nikola deploy gcloud``

## Documentación

* [Migrando nuestro Blog a Google App Engine con Nikola (ENG)](https://ontoblogie.clabaut.net/en/posts/201712/migrating-blog-to-nikola-%2B-gae.html)

* Google App Engine: [Standard](https://cloud.google.com/appengine/docs/standard/) y [Flexible](https://cloud.google.com/appengine/docs/flexible/)

* [Primeros pasos con Google App Engine](https://cloud.google.com/appengine/docs/standard/python/quickstart)

* [Google Cloud Storage (ENG)](https://cloud.google.com/storage/docs/how-to)

Revisado a 01/03/2022
