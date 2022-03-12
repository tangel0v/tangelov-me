---
title: "Como está montada esta web (I): fundamentos básicos"
slug: como-montada-web-i
authors:
  - tangelov
date: 2018-02-20T22:00:00+02:00
tags:  ["gcp", "nikola"]
categories: ["cloud"]
draft: false
---

El nacimiento de esta web fue algo bastante meditado, estuve dándole muchas vueltas. Inicialmente pensé en implementarla de una manera tradicional: con un servidor LAMP y desplegando contra él. Pero a medida que fui ganando práctica en nuevas metodologías y tecnologías y a sentirme cómodo en ellas, decidí aprovecharlo.

> __Nota del autor__: Este artículo fue escrito cuando Tangelov.me estaba desplegado con Nikola. Aunque a lo largo del 2020, se ha migrado a Hugo, el repositorio original sigue [disponible](https://gitlab.com/tangelov/tangelov-me) para cualquiera que quiera utilizar Nikola en Google Cloud de la misma forma que yo lo hice. También escribí sobre el proceso de migración y el uso de Hugo en [el siguiente post](https://tangelov.me/posts/tangelov-en-hugo.html).

Así a groso modo, esta web está construida gracias a cuatro diferentes tecnologías:

* [Git](https://git-scm.com/): Para su desarrollo y crecimiento.

* [Python](https://www.python.org/): Para la generación de la página web en si.

* [Markdown](http://joedicastro.com/pages/markdown.html): Para la escritura del contenido del blog.

* [Google Cloud Platform](https://cloud.google.com/?hl=es): Donde se presta el servicio.

<!--more-->

## Proceso de desarrollo
El proceso de desarrollo es simple: utilizo _git_ para gestionar el código fuente de una página web desarrollada con Nikola.

Nikola es un generador de código HTML estático escrito en python. Dicha herramienta es obra de [Roberto Alsina](https://github.com/ralsina) y permite el uso de lenguajes de marcado (como [Markdown](https://en.wikipedia.org/wiki/Markdown)) para crear las páginas web, sin tener que picar nosotros todo el código HTML,el JS y CSS que tendría una página web normal.

El hecho de que sea HTML estático, lo hace seguro y rápido, al no haber base de datos que pueda ser atacada.

![Esquema de desarrollo](https://storage.googleapis.com/tangelov-data/images/0004-00.png)

Los primeros pasos son montar el entorno de desarrollo: comenzé con un repositorio vacío en _Gitlab_ clonado a mi equipo para empezar a trabjar. Después monté un _virtualenv_ e instalé nikola con el gestor de paquetes de Python (_pip_). Puesto que es un desarrollo que sólo hago yo: sólo suelo usar dos _branchs_: develop y master, que voy fusionando a medida que le hago retoques al tema o añado nuevos posts

```bash
# Creamos el repositorio de git en la carpeta que queramos
git clone git@gitlab.com:tangelov/tangelov.me.git

# Primero instalamos virtualenv si no lo tenemos instalado
pip3 install virtualenv --user

# Creamos el entorno de desarrollo con Python3
virtualenv nikola
source nikola/bin/activate
pip3 install "nikola[extras]" --upgrade

# Añadimos el primer commit y lo pusheamos al repositorio de código de Gitlab.
touch README.md
git add README.md
git commit -S -m "First commit" README.md
git push
```

Tras configurar git, toca hacer lo mismo con Nikola. Para ello hay inicializar el sitio de Nikola y elegir un [tema](https://themes.getnikola.com/). Toda la configuración se realiza en el fichero _conf.py_

```bash
# Iniciamos nuestro sitio de nikola
nikola init

# Instalamos el tema que queremos de nikola
nikola theme -i jidn

# Realizamos las modificaciones necesarias en el conf.py (tema, _pretty urls_, etc.)
vim conf.py

# Generamos un nuevo post
nikola new_post -f markdown

# Editamos el nuevo post generado
vim posts/00-nuevo-post.md
```

Al usar el último comando, podremos escribir el contenido de nuestro post en markdown. Una vez hecho tan sólo tenemos que ejecutar el comando ``nikola build`` para generar el HTML asociado. Aparecerá una carpeta llamada ~/output dentro de la estructura de ficheros de nikola, que contiene todo lo necesario para que la página web sea funcional en cualquier sitio que esté alojada.

## Uso de Google App Engine
Google App Engine es un servicio ofrecido por Google donde hospedar páginas web, generar APIs o Endpoints y mil cosas más. Forma parte de lo que hoy en día se llaman _PaaS_ o _Platform as a Service_ donde nosotros solo nos encargamos de desplegar y desarrollar y le dejamos al proveedor casi todo lo relacionado con la infraestructura.

Ya me había peleado con él y decidí utilizarlo gracias a su sencillez, capacidad de autoescalado y también a la existencia de un Tier gratuito (que aunque tiene poca chicha, me ofrece unos costes nulos o mínimos).

Es necesario realizar una serie de cambios y configuraciones para adoptar el código HTML generado por Nikola al App Engine de Google. Pero eso dará para otro post :)


## Documentación

* Se puede consultar el código de la web [aquí](https://gitlab.com/tangelov/tangelov-me)

* [Cómo instalar Nikola (ENG)](https://getnikola.com/getting-started.html)

* [Free Tier en Google Cloud Platform](https://cloud.google.com/free/docs/frequently-asked-questions?hl=es-419)

* [Google App Engine](https://cloud.google.com/appengine/)

* [Google Cloud Storage](https://cloud.google.com/storage/)

Revisado a 01-03-2022
