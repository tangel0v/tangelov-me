---
title: "Aplicaciones para DevOps (II)"
slug: devops-apps-ii
authors:
  - tangelov
date: 2023-05-20T06:00:00+02:00
tags:  ["apps"]
categories: ["devops"]
draft: false
---

Gracias a la proliferación de las aplicaciones web y a su portabilidad entre distintos sistemas operativos, hoy en día es más fácil que esa aplicación que desees esté disponible para Linux. Como usuario del sistema operativo del pingüino os puedo asegurar lo mucho que se nota el cambio de tendencia. Hace años escribí un [post](https://tangelov.me/posts/devops-apps.html) sobre este tema y creo que ha pasado el suficiente tiempo para retomarlo.

El uso de frameworks web no es el único motivo. Las grandes _forjas_ de software como Github, Gitlab o más reciente [Codeberg](https://codeberg.org/), permiten a las comunidades ligadas al software libre o el código abierto comunicarse mejor y organizarse. Todo ello ha contribuido a la creación de mejores herramientas para el desarrollo de herramientas nativas y que el número de ellas se haya disparado. Además, Linux es uno de los sistemas operativos más utilizados por programadores y otra gente del mundillo que busca que sus herramientas sean multiplataforma desde un inicio.

La libertad que caracteriza a Linux también tiene algún inconveniente. Puesto que cada distribución va por libre, se ha generado fragmentación que complicaba el mantenimiento de las aplicaciones. No era nada raro que una distribución no tuviera la librería adecuada para que una aplicación funcionara y en este post, vamos a ver cómo la comunidad ha buscado formas para facilitar este proceso, así cómo aplicaciones que son muy útiles para nuestro día a día.

<!--more-->

## Empaquetando aplicaciones: Flatpak, Snap y AppImage
La solución dada para los problemas de compatibilidad y la fragmentación han sido las llamadas _aplicaciones autocontenidas_. Son sistemas que empaquetan el código de la aplicación junto a las librerías que utilizan para que éste pueda funcionar independientemente de la versión del sistema operativo. 

Aunque choca con la visión tradicional de almacenar todas las librerías en /var/lib y que éstas sean compartidas por todas las aplicaciones, siento que a día de hoy es más fácil que las actualizaciones lleguen a cualquier distribución gracias a estos sistemas. No todo es positivo puesto que esta metodología requiere más espacio en disco o puede suponer una mayor lentitud en el arranque de la misma.

Fundamentalmente hay tres a día de hoy: Flatpak, Snap y AppImage:
* __Flatpak__: Es un sistema de empaquetamiento y administración de aplicaciones para Linux que permite ejecutar aplicaciones aisladas del resto del sistema operativo. Es un desarrollo comunitario, aunque está fuertemente ligado a Gnome y Red Hat.

* __Snap__: Similar a Flatpak en muchos aspectos, este desarrollo de Canonical está ligado a una tienda centralizada (algo que causó bastantes asperezas), pero permite tener aplicaciones aisladas del sistema operativo y igual que el anterior.

* __AppImage__: Es un sistema que empaqueta todas las dependencias y librerías dentro de un paquete que se comporta como si fuese una máquina virtual dedicada a la aplicación. Generalmente tan sólo necesitas hacer dos clicks en la aplicación y se abrirá sin problemas.

Cada uno tiene sus ventajas e inconvenientes, algunos consumen más espacio en disco, otros proporcionan un mejor aislamiento entre aplicaciones, pero no puedo parar de agradecer lo sencillo que es tener a día de hoy software puntero gracias a estos frameworks y servicios. 

[Flatpak](https://flatpak.org/setup/) y [Snap](https://snapcraft.io/docs/installing-snapd) vienen preinstalados por defecto en multitud de distribuciones, pero en caso contrario su instalación es muy sencilla. Para utilizar aplicaciones de formato AppImage no necesitamos instalar nada en particular, tan sólo descargar la aplicación, darle permisos de ejecución y listo.

Tras instalar Flatpak y Snap, necesitamos saber que se descargan las aplicaciones de algún repositorio. Snap tiene su propia tienda, Snapcraft y aunque Flatpak es descentralizado, la mayoría de desarrolladores utiliza Flathub, el repositorio más conocido.

En este post, vamos a centrarnos en aplicaciones que sean accesibles desde alguna de estas plataformas, pero no significa que estén disponibles para instalar de forma tradicional o que no sean multiplataforma.

## Aplicaciones para DevOps II
Al igual que en el post anterior, voy a evitar las aplicaciones más conocidas como Thunderdbird, Discord o IDEs como VS Code o JetBrains, puesto que mi idea es mostrar aplicaciones más desconocidas, o que fuesen muy útiles para mi. Mi foco en esta lista va a estar en herramientas ligadas a productividad y a procesos de trabajo como escritura de documentación, programación, organización de las tareas, etc.

* __Flameshot__: Generar documentación de calidad requiere estar haciendo capturas de pantalla e insertando explicaciones en las mismas constantemente. Flameshot es un programa multiplataforma y que uso tanto a nivel personal como profesional desde hace años. De una forma muy sencilla, nos permite crear capturas de pantalla y añadir ciertos efectos que nos pueden ser muy útiles como etiquetas de texto, flechas o difuminar ciertas partes de la misma para ocultar datos personales, etc. Es absolutamente imprescindible y tan buena que he logrado que bastantes conocidos míos pasen a utilizarla.

* __Apostrophe__: Si Flameshot me cubre la parte de las imágenes de la documentación, Apostrophe es un editor en Markdown nativo que utilizo para escribir documentación a veces gracias a sus diversos modos de escritura.  No es obligatorio pero sí bastante útil, especialmente si no quieres utilizar aplicaciones web que pueden llegar a ser bastante pesadas.

* __Paper__: Otra de mis tareas habituales es revisar cosas que me han parecido útiles o interesantes. Pueden ser desde nuevas tecnologías que puedo integrar en mis proyectos o mejoras más inmediatas. En cualquier caso, son tareas que voy quitándome en función del tiempo disponible. He estado tomando notas en ficheros de texto ordenados por fecha desde antes que existiera Evernote, pero he decidido darle una oportunidad a Paper puesto que puedo agrupar las notas en libretas y usar una libreta por tema.

* __Kooha__: En ocasiones la mejor manera de ver un proceso en acción es a través de un video. Kooha es un grabador de pantalla que nos permite grabar una terminal, una ventana o una pantalla y exportarlo a distintos formatos. Yo lo uso para crear los gifs que veis en algunos de mis posts y para ilustrar algunos procesos si creo que sólo con el texto no ha quedado claro.

* __Podman Desktop__: Con todos los cambios realizados en Docker y la ausencia de Docker Desktop en Linux hasta hace poco, migré mi plataforma de contenedores a Podman. Podman es una CLI potente pero que tiene más funcionalidades que Docker (soporte a secretos, etc) y está pensada para proporcionar una cierta compatibilidad con Kubernetes. Tras el "abandono" de Docker, la comunidad no se ha quedado parada y ha creado una interfaz gráfica para gestionar nuestras imágenes y contenedores. Si eres usuario de Linux y estás planteándote usar Podman, es una herramienta indispensable. Aunque es recomendable aprenderse los comandos típicos, es imposible saberse todas las opciones y a mi me resulta muy cómodo para ver un estado general de los contenedores o para limpiar de imágenes sin uso el mismo.

* __Pods__: Si utilizamos contenedores pero no queremos usar algo "parecido" a Docker Desktop, podemos utilizar _Pods_. Es una herramienta más sencilla, con menos opciones que Podman Desktop pero que nos permite gestionar los aspectos más básicos de los mismos: arrancar, parar y borrar contenedores, limpiar imágenes no usadas, etc. Muy recomendable.

* __Furtherance__: Es la herramienta que he elegido para registrar cuanto tiempo dedico a cada una de mis tareas. La he utilizado para medir cuanto tiempo le dedico cada mes a mis tareas personales, para medir cuanto tiempo me lleva escribir un post o cuanto tiempo he necesitado para prepararme una certificación. Es una aplicación con una interfaz sencilla y que tiene las funcionalidades que necesito, aunque no la utilizo siempre. Por ejemplo, gracias a Furtherance, se que escribir la serie completa de posts sobre Cloud Run y Atlantis me llevó más de cuarenta horas y me permite estimar mejor el tiempo que necesitaré para escribir una nueva serie en el futuro.

  Existen una grandísima cantidad de herramientas para gestionar y medir nuestro tiempo y organizar nuestro trabajo. Las hay para todos los gustos y dependiendo de las metodologías que más nos gusten tenemos otras aplicaciones como __Done__, __Flowtime__ (para trabajar con metodologías Pomodoro), __List__ o __Planner__ (integrado con TodoIst).

* __MicroK8s__ o __Minikube__: Son distribuciones de Kubernetes empaquetadas que nos permiten arrancar un cluster en pocos segundos y muy útiles a la hora de comprobar si nuestros desarrollos se ejecutan correctamente en el orquestador. Al no ser usuario a diario de Kubernetes, son una opción muy potente y que arranco o apago en función de mis necesidades, pero imprescindibles cuando me dedico a hacer la revisión anual que le hago a todo el contenido del blog y para probar ciertos servicios sin guarrear mis propias máquinas.

* __Open Lens__: Es un IDE desarrollado específicamente para tener una interfaz gráfica con la que ver y gestionar nuestros recursos en Kubernetes. Aunque no lo uso mucho, si que he conocido mucha gente a la que le ha sido muy útil (el principal motivo por el que lo instalé)

* __Obsidian__ o __Logsec__: Ambas son aplicaciones que nos permiten crear bases de conocimiento basadas en ficheros Markdown e interrelacionarlas entre sí. Probé ambas durante varias semanas y aunque las terminé desinstalando porque no se ajustaban a lo que yo quería, creo que puede ser tremendamente útil para otros. Por ello, recomiendo que las probéis, qué busquéis tutoriales sobre su uso y que les echéis un vistazo.

* __Beekeeper Studio__: Como técnico, en ocasiones tengo que interactuar con alguna base de datos y Beekeeper Studio es una herramienta tremendamente versátil. Gracias a su compatibilidad con MySQL, Postgres, SQLite, SQL Server, Oracle database, CockroachDB y Amazon Redshift, se que va a cubrir la gran mayoría de mis necesidades en lo relativo a bases de datos. Recomiendo su uso, es multiplataforma y de código abierto, aunque también tiene una versión premium que es de pago.

* __Foliate__: Es un lector de EPUBs con una interfaz muy cuidada y que utilizo para gestionar mi librería de libros digitales y tener un fácil acceso tanto a libros técnicos como novelas o ensayos. Os recomiendo que le echéis un ojo.

Y con esta última, el post estaría completo, espero que estas aplicaciones os sean útiles y si tenéis una alternativa mejor, podéis contactar conmigo a través de los medios habituales. ¡Hasta la próxima!


## Documentación

* [Página web oficial de Flatpak (ENG)](https://www.flatpak.org/)

* [Página web oficial de Flathub (ENG)](https://flathub.org/es)

* [Página web oficial de Flameshot (ENG)](https://flameshot.org/)

* [Repositorio de código de Apostrophe (ENG)](https://gitlab.gnome.org/World/apostrophe)

* [Repositorio de código de Paper (ENG)](https://gitlab.com/posidon_software/paper)

* [Repositorio de código de Kooha (ENG)](https://github.com/SeaDve/Kooha)

* [Repositorio de código de Furtherance (ENG)](https://github.com/lakoliu/Furtherance), [Done (ENG)](https://flathub.org/apps/dev.edfloreshz.Done), [Flowtime (ENG)](https://github.com/Diego-Ivan/Flowtime), [List (ENG)](https://github.com/mrvladus/List) y [Planner](https://useplanner.com/)

* [Página oficial de Podman Desktop (ENG)](https://podman-desktop.io/) y de [Pods (ENG)](https://flathub.org/es/apps/com.github.marhkb.Pods)

* [Página web oficial de MicroK8s (ENG)](https://microk8s.io/) y de [Minikube (ENG)](https://minikube.sigs.k8s.io/docs/)

* [Página web oficial de Lens (ENG)](https://k8slens.dev/)

* [Página web oficial de Obsidian (ENG)](https://obsidian.md/)

* [Comparativa entre LogSec y Obsidian, por Pablo Bernardo](https://pablo-bernardo.medium.com/una-comparativa-ente-obsidian-y-logseq-puntos-a-revisar-antes-de-profundizar-en-una-de-ellas-db7aa39f1fa6)

* [Página oficial de Beekeeper Studio (ENG)](https://www.beekeeperstudio.io/)

* [Página web oficial de Foliate (ENG)](https://johnfactotum.github.io/foliate/)

Revisado a 20/05/2023
