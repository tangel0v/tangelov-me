---
title: "Mejoras en tangelov.me"
slug: mejoras-tangelov-nikola
authors:
  - tangelov
date: 2018-12-01T20:00:00+02:00
tags:  ["gcp", "nikola"]
categories: ["cloud"]
draft: false
---

Cuando empecé a plantearme esta web hace un año aproximadamente la ví como un pasatiempo, un sitio donde plasmar cuando me apeteciera algunas de las pruebas y tests que hago en mi tiempo libre, esperando que a alguien le pudiese resultar útil. Bajo esa base, me comprometí conmigo mismo a cumplir con una serie de premisas:

* Los posts deberían de estar en castellano. Ya existe una cantidad de documentación de una calidad excelente en inglés y me parecía que se debía enrriquecer un poco la blogosfera hispana.

* Los post deberían de tratar temas que no estuviesen siendo tratados en la blogosfera hispana o de los cuales hubiera poca documentación en español o bien estuviese muy dispersa. Y la temática debía estar relacionada con las metodologías devops o la nube pública. El ritmo de publicación debe ser al menos de una vez al mes.

* Internet está llena de documentación anticuada. Me comprometía a ir revisando periódicamente el contenido para evitar lo que me ha pasado a mi en numerosas ocasiones... que al buscar documentación ésta ya no funcionara debido a que el producto ya había cambiado tanto que no era compatible (en Ansible es bastante sangrante).

<!--more-->

En general estoy contento con el resultado del blog, me ha permitido profundizar en un montón de cosas y espero le que haya servido a alguien más. Sin embargo para este año he decidido implementar una serie de cambios para hacer de este pasatiempo mucho más interesante.

## Cambios en Nikola

### Migración a v8
El año pasado mi conocimiento de Nikola se limitaba a unas pocas aproximaciones a los generadores de código estático que existen. No es el único que hay y podría destacar tanto Jekyll (escrito en Ruby) como Hugo (escrito en Go), pero sigo en él puesto que le tengo un especial cariño a Python.

Nikola ha cambiado durante el último año. El año 2018 ha supuesto para Nikola el abandono de Python 2 y cambiar a una nueva versión nativa en python 3. Hace un tiempo subí de la versión 7.8.5 a la nueva [8.0.X](https://getnikola.com/blog/nikola-v800-is-out.html) y me encontré con algunos puntos que tuve que cambiar de mi configuración.

En general la web es relativamente sencilla por lo que sólo tuve que deshabilitar las partes de la configuración relacionadas con las secciones puesto que yo no los uso y han desaparecido en la nueva versión. Pueden verse todos los cambios que realice en la configuración de Nikola [aquí](https://gitlab.com/tangelov/tangelov-me/commit/473f4a7f59ae9b150495710f2a6c840dc44d5536) y [aquí](https://gitlab.com/tangelov/tangelov-me/commit/3a16f93b72be6a4412e7a07d09597357e93fce59).

### _Nuevo_ tema
Cuando comencé el blog tuve muchas dudas sobre el tema a utilizar y al final adapté un tema sobrio y sencillo, fácil de leer: [jidn](https://themes.getnikola.com/v7/jidn/). Sin embargo, hubo varias cosas del tema que no me terminaron de convencer (si alguien quiere consultar cómo se veía originalmente hay una demo en la web oficial de Nikola):

* El tema no se ha actualizado desde mediados del 2017. No es que sea algo que me preocupe especialmente, pero me gusta utilizar cosas que están siendo soportadas.

* Algunas de las características del blog no funcionaban ni en el momento de la instalación (los iconos no se veían).

* Los márgenes del tema me parecían exagerados para el tamaño de las pantallas que hay hoy en día.

Gracias a que el código del tema está disponible, todo lo anterior está ya solucionado y además he cambiado el uso de FontAwesome por [Forkawesome](https://forkawesome.github.io/Fork-Awesome/) :) .

## Cambios en GCP
Este año me he certificado como Professional Architect en GCP y he seguido utilizando sus servicios. El coste en infraestructura durante todo el año ha sido de la increible cifra de 0 euros y estoy bastante contento con la versatilidad que me han ofrecido. Tengo previsto ampliar la información sobre GCP y utilizar más servicios para el año que viene:

* A nivel profesional hace años que utilizo infraestructura como código y estoy terminando de pasar toda la infraestructura que utilizo para el blog a código para publicarlo y ayudar a la gente que quiera hacer algo parecido. Tampoco descarto hacerlo en otras nubes y comparar su versatilidad.

* Quiero seguir exprimiendo los servicios del Tier free de Google Cloud porque he hecho algunas pruebas y han sido satisfactorias. Por ejemplo, estoy haciendo pruebas con Big Data y las exportaciones de los datos del App Engine, aunque no son las únicas.


## Pŕoximamente
Me gustaría centrarme en tres cosas principalmente para este año:

* La primera y fundamental es lograr que el blog siga tal y cómo está ahora. Al menos.

* Quiero hacer un tema propio con el que me identifique más que el que tengo ahora y quiero ver si logro encontrar un sistema de comentarios que pueda integrar :)

* Quiero colaborar más con los proyectos de la comunidad y aportar con más proyectos de calidad fuera del blog. Más playbooks y roles para la comunidad.



## Documentación

* El código de la web sigue estando disponible [aquí](https://gitlab.com/tangelov/tangelov.me)

* Generadores de código estático: [Jekyll (ENG)](https://jekyllrb.com/), [Hugo (ENG)](https://gohugo.io/) y [Nikola (ENG)](https://getnikola.com/)

* [Actualización de Nikola v7 a v8 (ENG)](https://getnikola.com/blog/upgrading-to-nikola-v8.html)


Revisado a 01-02-2020
