---
title: "AWS Certified Solutions Architect - Professional"
slug: aws-solutions-architect
authors:
  - tangelov
date: 2021-05-16T14:00:00+02:00
tags:  ["aws", "certification"]
categories: ["personal"]
draft: false
---

Los que me conocen saben que siempre intento planificar a medio plazo e invertir mi tiempo para lograr un fin gracias al trabajo duro y la constancia.

Esto hace que en ocasiones, tenga invertir todo el tiempo del que dispongo para conseguir algo en concreto. Es algo que [ya ha ocurrido en el pasado](https://tangelov.me/posts/gcp-professional-architect.html) [varias veces](https://tangelov.me/posts/breve-pausa.html) y que ha vuelto a ocurrir por el mismo motivo.

Debido a las ansias de conocimiento y a un cambio de posición laboral, he dedicado unos tres meses (unas 120 horas en total) en prepararme una certificación nueva y por fin puedo decir que soy un _Solutions Architect_ de nivel Professional en Amazon Web Services. Gracias a poder reaprovechar parte del conocimiento que poseía de GCP, he podido realizar algunos _atajos_, pero igualmente la preparación del examen ha requerido mucho tiempo de estudio debido a la inmensa cantidad de servicios de los que dispone AWS.

> __Nota del autor__: pese a que en el momento de escribir el post, recomendé A Cloud Guru, ahora mismo (en 2023) la mejor plataforma para estudiar AWS es Cantrill, cuyo link dejaré en la documentación del post.

<!--more-->

Como en entregas anteriores, voy a dejar aquí mis recomendaciones para prepararse para la prueba:

* Me parece un examen más justo que los que me he encontrado en Google Cloud Platform. Aquí se busca demostrar maestría sobre los servicios de Amazon, sin añadidos. Tenemos que conocer los servicios en profundidad, cómo combinarlos para conseguir X propósitos y cómo hacerlo de la mejor manera posible. 

* Debido a la gran cantidad de servicios diferentes, recomiendo profundizar lo máximo posible puesto que existen servicios que tienen propósitos muy parecidos y que pueden llevarnos a la confusión (como Amazon SNS y Amazon Eventbridge).

* El examen consta de 75 preguntas tipo-test y multirrespuesta, que debemos responder en menos de tres horas. Tanto los enunciados como las respuestas pueden ser muy largas, así que tenemos que medir muy bien nuestro tiempo y comprender bien qué se nos pide en cada pregunta. Esto puede ser un problema si nuestro nivel de inglés es bajo y creo que es necesario tener un nivel decente para afrontar la prueba con garantías.

* Si el inglés no es nuestro idioma nativo, podemos pedir algunas facilidades (como tener más tiempo) antes de programar la fecha del examen y pagarlo.

* Para planificar el estudio, recomiendo comenzar por la guía del examen que AWS nos proporciona y después comprar algún tipo de formación. El curso de [A Cloud Guru](https://acloudguru.com/course/aws-certified-solutions-architect-professional) me ha parecido muy completo, aunque no lo suficiente como para permitirte pasar el examen.

> Además... ofrecen un examen de prueba que me parece _una ida de olla como una catedral_. Con una dificultad innecesaria que puede desanimar a cualquiera. Me parece que está mal planteado y que puede darte más dudas que certezas sobre lo bien que conoces Amazon Web Services. Personalmente, no recomiendo que lo haga nadie hasta que no esté muy bien preparado.

* Amazon también nos proporciona herramientas para evaluar nuestro nivel: podemos probar [algunas preguntas](https://d1.awsstatic.com/training-and-certification/docs-sa-pro/AWS-Certified-Solutions-Architect-Professional_Sample-Questions.pdf) sueltas gratis o comprar alguno de los exámenes de prueba (que tienen un coste reducido). En el caso de suspender, tendremos que esperar 14 días para repetir el examen, pero recibiremos feedback que nos indicará en qué partes hemos fallado más y nos dará una información muy valiosa a la hora de volver a presentarnos.

* Como en los exámenes de GCP, la experiencia vital me parece el mejor sistema de entrenamiento posible, pero si no es el caso, recomiendo conocer a fondo diferentes estrategias de despliegue, de arquitecturizar los elementos que conforman una aplicación y las ventajas y los inconvenientes de cada uno de ellos. También es importante conocer el vocabulario típico de negocio y costes como TCO, OPEX, CAPEX, etc.

* Tras haber hecho algún curso, recomiendo complementar el conocimiento con la documentación oficial de AWS. Es exhaustiva y está muy bien ordenada. También recomiendo echarle un vistazo a los whitepapers publicados por AWS para profundizar más.


## Documentación

* [Whizlabs (ENG)](https://www.whizlabs.com/): Proporciona cursos y laboratorios para aprender además de exámenes de prueba con preguntas parecidas y que nos ayudarán a evaluar si estamos preparados para afrontar el examen real.

* [Udemy (ENG)](https://www.udemy.com/course/aws-solutions-architect-professional/): Udemy es una plataforma que posee gran cantidad de cursos formativos y por lo que vi por la red, la gente recomendaba este curso (aunque yo no lo he comprado).

* [Cantrill.io (ENG)](https://learn.cantrill.io/): La plataforma que más me gusta en la actualidad. Muy actualizado y enfocado en lo más importante y necesario para pasar el examen.

* [A Cloud Guru (ENG)](https://acloudguru.com/course/aws-certified-solutions-architect-professional): Es el curso que yo he utilizado como base para preparar mis apuntes y creo que proporciona una buena base.

* [Arquitecturas de referencia de AWS (ENG)](https://aws.amazon.com/es/architecture/reference-architecture-diagrams/?whitepapers-main.sort-by=item.additionalFields.sortDate&whitepapers-main.sort-order=desc&awsf.whitepapers-tech-category=*all&awsf.whitepapers-industries=*all): Amazon publica una serie de arquitecturas de referencia para implementar que podemos utilizar como base en nuestro día a día. Aunque son muchísimos, si recomiendo echarle un ojo por encima a los relacionados con la parte de metodología.

* [AWS Well-Architected (ENG)](https://aws.amazon.com/architecture/well-architected/?wa-lens-whitepapers.sort-by=item.additionalFields.sortDate&wa-lens-whitepapers.sort-order=desc): Una serie de buenas prácticas que Amazon recomienda utilizar cuando se haga arquitectura (de aplicaciones y/o infraestructura) en su plataforma.

* [AWS FAQs](https://aws.amazon.com/faqs/?nc1=h_ls): Lista de FAQs de AWS.


Revisado a 01/05/2023
