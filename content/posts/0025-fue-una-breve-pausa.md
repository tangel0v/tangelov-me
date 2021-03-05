---
title: "¿Una pausa? Certificaciones y más"
slug: breve-pausa
authors:
  - tangelov
date: 2020-01-01T05:00:00+02:00
tags:  ["gcp", "trabajo"]
categories: ["personal"]
draft: false
---

Buenas a todos, aunque lo pudiera parecer no he abandonado el blog (o al menos no lo he hecho definitivamente).

Hace unos meses que quería escribir este post y aunque no esperaba que se demorara tanto, creo que la ausencia de contenido durante estos seis meses merece una explicación seria y sincera.

<!--more-->

En principio iba a aprovechar que los meses centrales del año (Julio y Agosto) coinciden con las vacaciones de la mayoría de la gente, para finalizar diversos posts que tengo a medias y a profundizar en algunas tecnologías nuevas que quería conocer. Sin embargo aparecieron dos contratiempos en mi vida que han hecho que lo haya tenido que posponer hasta mediados de diciembre. 

~~He tenido un hijo precioso~~. Nah, es coña xD.


## Cloud Developer y Data Engineer
El primer contratiempo ha sido la necesidad profesional de continuar aprendiendo cosas nuevas en GCP: ahora no sólo soy [Professional Cloud Architect](https://cloud.google.com/certification/cloud-architect) sino también [Professional Cloud Developer](https://cloud.google.com/certification/cloud-developer) y [Professional Data Engineer](https://cloud.google.com/certification/data-engineer).

La preparación de las certificaciones no fue especialmente dura, pero si requirió de bastante tiempo (unas 100 horas el Professional Data Engineer y unas 10 el Cloud Developer):

* La certificación de _Professional Data Engineer_ se centra en los servicios de preparación, explotación, procesamiento y almacenado de datos en la nube y a la utilización de frameworks de _Machine Learning_ para aportar valor por encima de la búsqueda de patrones.

* La certificación de _Professional Cloud Developer_ se centra en como integrar ciertos servicios de GCP dentro de nuestras aplicaciones y cómo desarrollar pensando "en la nube". Esto aplica desde conocimientos de API/REST, métodos de despliegue en la nube y una pequeña parte de arquitectura de software y sistemas (microservicios, qué servicios de GCP debemos usar en que casos, etc.)

Ambas tecnologías son muy demandadas en el mercado actual y complementan muy bien mis conocimientos previos. Aunque ya conocía la teoría de algunas partes (DevOps, CICD, microservicios, etc) y algunas de las herramientas que se utilizan (como Apache Spark o BigQuery), la preparación del examen me ha servido para bajarlas más a tierra y conocer partes nuevas como el Machine Learning (que me ha parecido fascinante, pese al humo que hay en el marketing de estas tecnologías).

Mi metodología de trabajo para prepararme ambos exámenes no ha variado demasiado respecto al pasado:

* Al igual que en otras pruebas de GCP, los exámenes son complejos, de 50 preguntas tipo tests y multirrespuesta. Hay que leer con mucha pausa cada pregunta y cada respuesta puesto que son complejas y largas. Para prepararnos mejor, podemos utilizar los exámenes de prueba [1](https://cloud.google.com/certification/practice-exam/data-engineer) y [2](https://cloud.google.com/certification/practice-exam/cloud-developer).

* Leerse toda la documentación de Google Cloud debe de ser un _must_ puesto que existen preguntas que difícilmente habremos tocado en la vida real. Me han resultado de mucha ayuda la documentación de soluciones donde indican las diferencias entre Kafka y los servicios de mensajería de GCP o la lista de buenas prácticas a la hora de utilizar Cloud Dataproc.

* Debemos conocer los servicios que son competencia o que complementan a otros servicios de GCP (Jenkins y Kafka), así cómo cierta teoría: diferentes metodologías de despliegue (Blue-Green, rolling-update, etc), metodologías de trabajo DevOps (Agile, GitOps, etc).

* Google ofrece cursos oficiales en Coursera ([1](https://www.coursera.org/professional-certificates/gcp-data-engineering) y [2](https://www.coursera.org/specializations/developing-apps-gcp)). Cada certificación se corresponde con 5 o 6 cursos que se agrupan con el nombre de la misma. En general sólo me han parecido muy útiles los de Machine Learning en el _path_ de Data Engineer: empieza con lo básico y termina con mucha complejidad.

* La experiencia sigue siendo el mejor sistema de estudio posible, pero reconozco que los cursos de Linux Academy son muy buenos. A mi parecer ofrecen mejor la sensación de estar preparándote para utilizar los servicios de GCP que los cursos oficiales.

* También podemos utilizar Qwiklabs y las FAQs de la certificación.


## Distracciones personales
El tiempo dedicado al estudio me consumió todo el verano junto a Septiembre y a mediados de Octubre, pero cuando iba a retomar el blog apareció un segundo contratiempo: he tenido una _tremenda sobrecarga de trabajo_ que ha hecho que cuando llegara a casa decidiera desconectar más que escribir. También petó mi instalación de Linux en el PC y tuve que dedicarme a replataformarlo. Aunque no me llevó mucho tiempo y no perdí datos, si me dio pereza y estuve 10-12 días sin poder hacer nada con él.

Algunas de las cosas que he hecho (y que a nadie le importan) estos dos últimos meses:

* Me he comprado una Nintendo Switch y he jugado mucho al Super Mario Maker 2.

* Me he comprado los dos Age of Empires Definitive Edition y les he dado bien duro.

* Me he leído una biografía de Napoleón Bonaparte (de unas 1200 páginas).

* He recuperado la tradición de cocinar que había dejado un poco en suspenso.

Así que nada, a partir de ahora (más liberado) volvemos a la rutina y espero poder cumplir con mi objetivo de escribir entre uno y dos posts cada mes. Un saludo a todos!


## Documentación

* [Preparación de la certificación de Google Cloud Architect](https://tangelov.me/posts/gcp-professional-architect.html)

* [Coursera (ENG)](https://www.coursera.org): Especializaciones online (varios cursos agrupados) que aportan un nivel intermedio, bajo mi punto de vista insuficiente para el nivel de conocimiento exigido en la prueba.

* [Qwiklabs (ENG)](https://qwiklabs.com): Proporciona laboratorios para ganar experiencia extra respecto a nuestra experiencia profesional. Su precio es algo elevado y personalmente prefiero invertir mi dinero en Linux Academy.

* [Linux Academy (ENG)](https://www.linuxacademy.com): Proporciona cursos y laboratorios orientado a los exámenes de diferentes proveedores de nube pública (entre otras). Muy completos y útiles.

* [GCP FAQs (ENG)](https://cloud.google.com/certification/faqs/#0): Lista de FAQs de GCP

Revisado a 01/03/2021
