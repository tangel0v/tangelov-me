---
title: "Tangelov.me en Hugo"
authors:
  - tangelov
date: 2020-11-01T20:00:00+02:00
tags:  ["hugo", "nikola"]
categories: ["cloud"]
draft: false
---

A finales del año 2018 hice una pequeña retroespectiva sobre qué futuro quería para este blog. En ese momento mis metas se centraron en continuar escribiendo contenido, adaptar más el tema a mis gustos y lograr una mayor interacción con la comunidad (con colaboraciones, habilitando un sistema de comentarios, etc).

Tras realizar varias pruebas, me di cuenta de algunas de las limitaciones que tenía Nikola respecto a otros generadores de código estático: su comunidad es reducida y su desarrollo, sin llegar a detenerse, avanza muy lentamente. A mi pesar, descubrí que algunas de las funcionalidades que deseaba, iban a necesitar mucho trabajo y decidí priorizar la creación de nuevo contenido frente a la funcionalidad.

Esto cambió hace unos meses: recibí un correo de parte de un mibro de Platform9 donde me daba feedback respecto al blog y me hacía una serie de recomendaciones para lograr tener más visibilidad. Tomé nota al respecto y me puse manos a la obra: era el momento de dejar atrás Nikola por otro generador.

A nivel personal, no había utilizado ningún otro generador de código estático, pero tras unas cuantas pruebas rápidas decidí utilizar Hugo, puesto que teóricamente cubría todas las necesidades que había detectado.

<!--more-->


## De Nikola a Hugo
Hugo es un generador de código estático (similar a Nikola), programado en Go, pero con una comunidad mucho más grande que su amigo escrito en Python. Tiene muchas más funcionalidades, una velocidad de desarrollo más rápida y gracias al tamaño de su comunidad, un número de temas disponibles casi incontable.

Previamente a empezar, hice una toma de requisitos simple: el nuevo sitio debía tener al menos las mismas funcionalidades que el original. El problema es que esa frase tiene más implicaciones de las que podría parecer a priori:

![esquema-tangelov-me-2020](https://storage.googleapis.com/tangelov-data/images/0037-00.png)

El esquema anterior muestra todas las dependencias que a día de hoy forman parte de esta página web. No sólo hay que migrar el tema y el contenido de un sistema a otro, sino también todas sus integraciones. A día de hoy, podríamos dividir este blog en tres partes:

1. Una parte de infraestructura, que no se ve impactada, puesto que se gestiona a través de un repositorio aparte y que se despliega de forma manual (por poco tiempo).

2. El contenido del blog y el sistema de despliege, que se encuentran en Gitlab. También se genera una imagen de Docker privada y algunos tests contra un entorno de _Staging_.

3. Por último, tenemos una parte en Github que se alimenta a través de un mirroring desde Gitlab, que a su vez genera mediante el uso de Travis CI, un contenedor que es públicamente accesible en DockerHub.


### Migrando el aspecto: Jidn
El aspecto de una web es tan importante como su contenido y forma parte de su ser. Por ello iba a ser lo primero que iba a migrar.

Tras [instalar Hugo](https://gohugo.io/getting-started/installing/), primero tenemos que generar el arquetipo de una nueva web con el comando ```hugo new site $nombre-del-site```. Dicho comando genera una serie de carpetas y ficheros que vamos a explicar:

* _Archetypes_: es  donde se pueden crear plantillas para el contenido para nuestra página web.

* _Content_: almacena los distintos ficheros en Markdown que van a convertirse en las entradas y secciones de nuestra web.

* _config.toml_: es el fichero de configuración general para todo el sitio web. Aquí seleccionamos el comportamiento del renderizado, el tema a utilizar, etc.

* _Layouts_: en este directorio podemos crear ciertas plantillas HTML para extender (o sobreescribir) las funcionalidades del tema que seleccionemos.

* _Static_: es el directorio donde se ubican todos los elementos estáticos de nuestra web como (CSS, Javascript, etc).

* _Public_: es el directorio donde se procesan todos los elementos y se renderiza la página web definitiva.

* _Themes_: es la carpeta donde debemos ubicar el tema que vaya a usar nuestra página web.

```bash
# Así se ve la estructura básica de carpetas en Hugo
.
├── archetypes
│   └── default.md
├── config.toml
├── content
├── data
├── layouts
├── public
├── resources
│   └── _gen
│       ├── assets
│       └── images
├── static
└── themes
```

Una vez hemos inicializado el sitio web, ya podemos comenzar a portar el tema. El tema que utilizaba en Nikola es una versión modificada del tema [Jidn](https://github.com/jidn/nikola-jidn) y que tiene las siguientes características:

* Es un tema derivado de Lanyon, del que toma su característica barra lateral. Lanyon es un tema portado de otro generador de código estático (Jekyll) y que se encuentra disponible en Hugo.

* Jidn tiene un sistema de gestión de autores que me gusta mucho, pero utiliza código Python para proporcionar dicha funcionalidad y ésta no va a funcionar con Hugo.

Primero comenzamos modificando el fichero _config.toml_ con los siguientes valores:

```toml
baseURL = "https://tangelov.me"
languageCode = "es"
DefaultContentLanguage = "es"
title = "Estando en las nubes"
uglyurls = true

theme = "Lanyon"

[languages]
  [languages.es]
    title = "Estando en las nubes"
    languageName = "Español"
    weight = 1

[taxonomies]
  author = "authors"
  tag = "tags"
  category = "categories"
```

Gracias a este cambio, Hugo ya sabe que debe utilizar el tema Lanyon, pero todavía no podemos utilizarlo debido a que no está instalado. Podemos hacerlo de múltiples formas: la más básica es descargar el tema y copiarlo dentro de la carpeta _themes_. pero existen mejores formas de hacerlo. La forma recomendada es mediante el uso de submódulos de git (así seguimos automáticamente las actualizaciones del tema original). Para hacerlo, tan sólo necesitamos ejecutar el siguiente comando:

```bash
# Le indicamos a Git que genere en el carpeta themes/Lanyon una referencia al repositorio oficial del tema
git submodule add https://github.com/tummychow/lanyon-hugo themes/Lanyon
```

Si ahora ejecutamos ```hugo serve -D``` y accedemos a http://localhost:1313, veremos algo similar a ésto:

![hugo-lanyon](https://storage.googleapis.com/tangelov-data/images/0037-01.png)

No debemos olvidar que nuestro fin no es utilizar Lanyon como tema, sino replicar el tema Jidn. Aunque podríamos modificar las plantillas del tema original, me parece más elegante utilizar las funcionalidades de las carpetas _layouts_ y _static_ para modificar las funcionalidades de Lanyon. Así desacoplamos nuestras modificaciones del tema original y lo mantenemos intacto como una dependencia.

* El primer paso es copiar el siguiente fichero en [_css/jidn.css_](https://gitlab.com/tangelov/tangelov-me/-/raw/master/themes/mod-jidn/assets/css/jidn.css) a la carpeta _static_. Así Hugo puede acceder al CSS del anterior tema.

* El siguiente paso es modificar el comportamiento por defecto de Lanyon gracias al uso de plantillas en _layouts_:

    * Primero creamos la carpeta _default_. Dentro colocamos las plantillas que modifican el renderizado por defecto de los elementos del blog que no tienen una plantilla dedicada. Aquí for ejemplo añadimos el código HTML que adapta el sistema de autores de Jidn a Hugo.

    * En segundo lugar, creamos la carpeta _partials_ y dentro colocamos las plantillas que modifican el comportamiento de las cabeceras de la web, el footer y la barra lateral. Aquí también personalizamos las entradas de la barra lateral.

    * En tercer lugar, creamos las carpetas _authors_ y _posts_ y creamos un fichero _list.html_ en cada una de ellas. Así personalizamos el renderizado que nos listan los posts y los autores del blog.

    * Por último, creamos en la raíz de _layouts_, un nuevo fichero _index.html_ para simplemente traducir los botones de paginación que se muestran en el fondo de la página web.

Todos estos cambios (que pueden consultarse en el repositorio) han hecho que nuestra página pase a estar así:

![hugo-jidn](https://storage.googleapis.com/tangelov-data/images/0037-02.png)

> Para ver exactamente el cambio que produce nuestra plantilla respecto a la original, podemos utilizar el comando diff. A modo de ejemplo ```diff layouts/partials/sidebar.html themes/Lanyon/layouts/partials/sidebar.html```, nos mostraría las diferencias entre la sidebar original y la nuestra.

Y de esta forma tendríamos migrado nuestro tema a Hugo :) .


### Migrando el contenido
Una vez que tenemos el tema funcionando, ahora vamos a proceder a migrar el contenido del blog. Al igual que Nikola, Hugo soporta Markdown como lenguaje para escribir los posts, pero debemos ubicarlos en subcarpetas dentro de _content_. Para nuestro caso, vamos a tener tres tipos de contenido: autores, posts y páginas.

Lo primero que vamos a migrar son los posts y las páginas. Cada tipo tiene una carpeta propia (posts, pages), con un fichero dedicado para cada entrada. Si, por ejemplo, queremos crear un elemento nuevo podemos utilizar el siguiente comando ```hugo new pages/sobre-mi.md``` o ```hugo new posts/00050-nuevo-post.md```.

![hugo-page](https://storage.googleapis.com/tangelov-data/images/0037-03.png)

Como podemos ver en la captura anterior, los metadatos de Hugo se encuentran entre '\-\-\-'. Dichos metadatos se asignan a categorías, fechas, autores y etiquetas y son utilizados para agrupar los posts. Estos descriptores son diferentes en Nikola, por lo que tenemos que migrarlos de uno a otro. A modo de ejemplo, así quedaría un post:

![hugo-nikola-post](https://storage.googleapis.com/tangelov-data/images/0037-04.png)

Ahora vamos a copiar todos los posts y las páginas del repositorio basado en Nikola al nuevo y después vamos a migrar los metadatos al formato de Hugo. Si queremos que algún elemento no tenga autor (como las páginas), simplemente lo omitimos.

Como ya he comentado antes, una de las cosas que más me gustaba del tema de Jidn era su sistema de autores. Por ello, una vez hemos terminado de migrar los posts y las páginas, vamos a adaptar el sistema de autores. 

Dentro de _content_, vamos a crear una nueva carpeta llamada _authors_. Cada autor que queramos añadir debe ser una carpeta con su nombre (en este caso tangelov) y contener en su interior un fichero _\_index.md_.

```bash
.
└── authors
    └── tangelov
        └── _index.md
```

Cada _\_index.md_ debe contener una [estructura de metadatos](https://gitlab.com/tangelov/go-tangelov-me/-/raw/master/content/authors/tangelov/_index.md) que será usada por Hugo para completar la información del autor en cada post en el que esté asignado:

* _Name_: es el nombre que el autor va a tener en el blog

* _Photo_: es la URL del avatar del autor del post o página.

* _Bio_: es un pequeño resumen o una presentación del mismo.

* _Location_: es el lugar donde se encuentra el autor.

* _License_: es el tipo de licencia que van a tener sus posts.

* _Email_: es el correo electrónico a través del cual se puede contactar con el autor.

* _Identity_: es una lista de identidades online que se adjuntarán a modo de firma en cada artículo. Su estructura se corresponde con un nombre (que es [el nombre del icono en Forkawesome](https://forkaweso.me/Fork-Awesome/icons/) y la URL de su usuario en dicho servicio).

Y finalmente, ya tendríamos una replica totalmente funcional en local de nuestro blog :)

![hugo-final-style](https://storage.googleapis.com/tangelov-data/images/0037-05.png)


### Adaptando Hugo a Google App Engine
Ya hemos finalizado la fase 1 de la migración: nuestro blog está portado y funcionando en local. Podemos generar todo el HTML definitivo gracias al comando ```bash hugo```, pero para poder desplegarlo en Google App Engine, todavía necesitamos añadir un par de elementos extra:

* Google App Engine no soporta el uso de _Pretty URLs_ en páginas estáticas, por lo que tenemos que añadir en el fichero (si no lo hemos hecho ya) _config.toml_ la clave _uglyurls = true_.

* Para poder desplegar cualquier cosa en Google App Engine, necesitamos que existan dos ficheros en la raíz de la web resultante: _app.yaml_ (la configuración del servicio de App Engine) y un favicon (favicon.ico - opcional). Si los copiamos en la raíz de la carpeta _static_, cuando rendericemos la web, estarán en la raíz de la web definitiva.

Tras estos cambios, ya podríamos desplegar a mano la primera versión del _nuevo_ tangelov.me. Tan sólo necesitamos ejecutar los siguientes comandos:

```bash
# Primero renderizamos la web
# Recomendamos borrar primero el contenido para evitar algún tipo de problema
hugo mod clean --all && hugo

# Nos metemos en la carpeta y desplegamos (si está gcloud bien configurado)
cd public && gcloud app deploy --project $PROJECT_ID
```

Y ya podríamos acceder a través de cualquier navegador web.


## Mismo contenido, nuevas integraciones
Aunque nuestro blog ya está listo para desplegarse en la nube de nuevo, por el camino se han perdido todas las integraciones que teníamos: los despliegues son manuales y no hay ningún tipo de automatismo. El siguiente paso es arreglar dichas integraciones y automatizaciones.

La primera acción va a centrarse encorregir el sistema de testing de la aplicación y el sistema de despliegues automáticos hacia GCP.

Copiamos la carpeta de tests de la versión de Nikola y el fichero _requirements-test.txt_ a la raíz del nuevo repositorio. Uno de los tests (que seguirán de momento en Python 3), debe de ser modificado para que apunte a la nueva URL de Feeds que genera Hugo:

```python3
    if CI.startswith('post/'):
        tempfeed = feedparser.parse(''.join([URL, 'index.xml']))
        prodfeed = feedparser.parse('https://tangelov.me/index.xml')

        assert tempfeed.entries[0].title != prodfeed.entries[0].title
```

Después de corregir el sistema de tests, vamos a centrarnos en el fichero que gestiona el sistema de CI/CD. Tenemos que realizar pocos cambios: tras migrar las variables de los Pipelines de un repositorio a otro, solo cambiamos la forma de generar el HTML final gracias al uso del contenedor de Klakegg y a adaptar todas las referencias del viejo pipeline al nuevo repositorio (ahora llamado go-tangelov-me):

```bash
# Línea para generar el código estático con Nikola
docker run --rm -v $PWD:/site -w /site registry.gitlab.com/paddy-hack/nikola:8.1.1 nikola build

# Línea que reemplaza la anterior para generar el código estático con Hugo
docker run --rm -v $PWD:/src klakegg/hugo:0.76.5-debian
```

En este momento el blog ya es plenamente funcional, pero aún falta arreglar el sistema de mirroring con Github y la generación de contenedores públicos a través de Travis CI:

* Para solucionar el primer punto, primero desactivamos el mirroring en el repositorio viejo, borramos las variables del pipeline y configuramos el mirroring en el nuevo repositorio siguiendo [este tutorial](https://docs.gitlab.com/ee/user/project/repository/repository_mirroring.html#setting-up-a-push-mirror-from-gitlab-to-github).

* Para solucionar el primer punto, modificamos el fichero .travis.yml y añadiendo las siguientes líneas tras eliminar las referencias a Nikola:

```yaml
install:
  - curl -LO https://github.com/gohugoio/hugo/releases/download/v0.76.5/hugo_0.76.5_Linux-64bit.deb
  - sudo dpkg -i hugo_0.76.5_Linux-64bit.deb

script:
  - hugo
  - echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USER" --password-stdin
  - docker build -t $DOCKER_USER/tangelov-me:latest .
  - docker push $DOCKER_USER/tangelov-me:latest
```

Y finalmente... la migración había terminado.

## Estado actual y pŕoximas mejoras
El blog ahora mismo las mismas funcionalidades que su versión anterior y tengo pensadas una serie de mejoras a añadir en el pronto plazo:

* Modificar el título de los posts para que sean más descriptivos. Este cambio ya está hecho y lamento si a alguien le rompo momentáneamente el sistema de Feeds.

* Añadir un sistema de comentarios: estoy pensando en utilizar Staticman, pero todavía no he tomado ninguna decisión.

* Publicar paneles de visualización de posts públicos.

* Añadir una mejor traducción a ciertas partes de la web.

Y nada, espero que os haya gustado y os espero en el próximo posts. ¡Muchas gracias!


## Documentación

* [Página oficial de Hugo (ENG)](https://gohugo.io/)

* [Repositorio en Github de Hugo (ENG)](https://github.com/gohugoio/hugo)

* [Lanyon Theme for Hugo (ENG)](https://themes.gohugo.io/lanyon/)

* [Docker de Hugo por Klakegg (ENG)](https://hub.docker.com/r/klakegg/hugo/)

* El nuevo código de la web está disponible [aquí](https://gitlab.com/tangelov/go-tangelov.me).

Revisado a 02-11-2020
