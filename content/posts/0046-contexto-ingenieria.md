---
title: "Sin contexto no hay ingeniería"
slug: contexto-ingeniería
authors:
  - tangelov
date: 2022-02-05T09:00:00+02:00
tags:  ["cloud", opinion"]
categories: ["personal"]
draft: false
---

¡Feliz año a todos! Siento haber tenido que reducir la cadencia de nuevos posts, pero he estado bastante ocupado y he focalizado mis esfuerzos en otros menesteres.

Este año me he lanzado a perfeccionar mi inglés, dedicándole mucho tiempo y esfuerzo. A modo de entrenamiento, añadí a mi feed personal los principales canales de noticias de los proveedores de nube pública más importantes, comencé a leer más libros técnicos en inglés y también me aficioné a podcasts de CICD, Kubernetes, Seguridad, etc.

Mi rutina de aprendizaje ha funcionado y además me ha permitido estar al día en las últimas metodologías y tecnologías del mundo Cloud. Sin embargo, esta nueva información ha terminado provocándome un debate interno bastante fuerte.

Este post va a ser un poco diferente, de opinión, así que recuerda que es __mi opinión__ y que podemos estar en desacuerdo sin que pase absolutamente nada.

<!--more-->

Me apasiona trabajar en consultoría. Cada proyecto muestra la visión de un cliente a la hora de afrontar un problema dentro de un contexto determinado, algo vital para diseñar la mejor solución posible.

En los últimos años, han aparecido nuevos paradigmas computacionales (Cloud, etc), lenguajes de programación (Rust, Go) o esquemas organizativos (basados en metodologías ágiles) que parecen estar reemplazando paulatinamente a otros más antiguos y estáticos.

Aunque la adopción de estos cambios puede surgir de forma natural, en ocasiones se producen por el resultado de modas. Siempre debemos evaluar si las nuevas tecnologías aportan valor o si este supera los inconvenientes causados por la migración a una nueva tecnología.

Pienso dividir este artículo en dos partes:

* El sesgo informativo de Silicon Valley.

* El ciclo de vida de los productos digitales.


## El sesgo informativo de Silicon Valley
Todos sabemos quiénes son los campeones del mundo IT: las compañías de Silicon Valley. Empresas como Microsoft, Google o Amazon son compañías enormes, que operan en mercados globales y que gracias a la economía de escala, _pueden_ competir fuera de los sectores que los vieron nacer.

Los problemas técnicos de estas empresas tienen un contexto muy específico: mejorar la resiliencia, escalabilidad y eficiencia de aplicaciones que son consumidas de forma global. En aplicaciones tan masivas, la economía de escala hace que cada pequeño punto de mejora, les permita ahorrar muchísimo y dedicar esos recursos a otras tareas.

También se ven forzados a gestionar los cambios muy rápido para adaptarse al mercado y añadir nuevas funcionalidades o servicios que sean requeridas por sus usuarios.

Aunque este modelo es ideal, no encaja especialmente bien con lo que he visto en mi carrera profesional. Bajo mi punto de vista, los modelos difieren por tres motivos:
- Un mercado interno y con pocas barreras.
- La naturaleza de las compañías totalmente digitales.
- La capacidad de inversión.

El primer punto se centra en las diferencias entre Estados Unidos y Europa. Pese a que ambos mercados tengan tamaños similares, las barreras lingüísticas y legales hacen que el crecimiento de una empresa europea tienda a ser más escalonado: nace y crece dentro del mercado interno de un Estado y se expande a otros países tras sufrir una cierta aculturación. La existencia en Estados Unidos de un marco lingüístico común, con una cultura más parecida, hace que la fricción sea menor.

Muchas empresas europeas están ligadas a ámbitos culturales. Por ejemplo, las empresas españolas tienden a expandirse por Latinoamérica, al igual que las empresas francesas lo hacen en la Francofonía. Fuera de esta regla, podemos ubicar a países con poco peso internacional o mercados internos pequeños, que orientan directamente su producción hacia el exterior.

Los dos últimos puntos están interrelacionados. La mayoría de artículos o libros escritos sobre innovación en IT forma parte de empresas cuyo producto es totalmente (o casi) digital. Son gente proveniente de grandes tecnológicas (como Google o Microsoft) o _"unicornios"_ más jóvenes (como Uber, Github o Stripe).

Este tipo de empresas pueden invertir hasta el último euro en mejoras técnicas puesto que cualquier inversión mejorará su producto, ya sea por simple eficiencia o por el valor que aportan las nuevas funcionalidades. En Europa no somos punteros en este sector y si una empresa más tradicional (como Inditex o Volkswagen), canalizara toda su inversión hacia un producto digital en detrimento de sus productos físicos, su economía se resentiría. Todo ello hace que el presupuesto que se pueda destinar a IT esté mucho más condicionado.

Por ejemplo, Kubernetes nace como resultado de condensar la experiencia de Google en gestión de servicios durante años. Es una herramienta genial, que aporta muchas facilidades para estandarizar y garantizar la resiliencia de las aplicaciones, pero usarlo _bien_ requiere de gente muy cualificada debido a su complejidad.

Una [encuesta](https://kubernetes.io/blog/2020/08/31/kubernetes-1-19-feature-one-year-support/) realizada en 2020 mostró que el 50% de los usuarios fueron incapaces de mantenerse dentro de versiones soportadas. Aunque el periodo ha sido ampliado, pienso que el porcentaje debía de ser mayor puesto que quien esté fuera de soporte será menos propenso a participar en este tipo de encuestas.

Imaginemos que una empresa desea modernizar su IT gracias a Kubernetes. ¿Cuánto podrá invertir en IT una empresa que no sea completamente digital? ¿Estamos seguros de necesitar sus capacidades a corto plazo? ¿Vamos a poder controlar la deuda técnica, seguir un mínimo de buenas prácticas y evitar que nuestros clústers se conviertan en jauja?

Estas preguntas son necesarias antes de adoptar cualquier nueva tecnología. Si la respuesta es no, a lo mejor debemos seguir otro camino como reducir abstracciones (seguir en máquinas virtuales pero con mejor operativa) o delegar la resiliencia y la escalabilidad sobre un PaaS (como Cloud Run en GCP o Fargate en AWS).

Es importante conocer las metodologías más punteras del mercado, pero debemos ser conscientes de nuestras limitaciones e intentar conseguir la mejor ingeniería posible haciendo uso de los recursos que disponemos.

Google o Netflix tienen consumidores en todo el mundo y por ello su servicio tiene que funcionar casi con un 100% de disponibilidad. Para llegar a esa meta, necesitas sistemas distribuidos globales con despliegues transparentes para el usuario. Si eres un e-commerce que opera en tres países dentro de la UE, es posible que no necesites tal nivel de excelencia por el momento y puedas limitarte a aplicar ventanas de mantenimiento en las horas de menor tráfico.

En definitiva, debemos ser cautos ante las modas tecnológicas y lograr la mejor ingeniería posible haciendo uso de los recursos disponibles. No necesitamos operar como Netflix o Google si no tenemos sus mismas necesidades.


## El ciclo de vida de las aplicaciones
El ciclo de vida de una aplicación es el proceso por el cual pasa una aplicación desde su concepción hasta su retirada de producción. 

En empresas más tradicionales, estos ciclos son relativamente largos (con más de cinco años fácilmente) y su stack tecnológico es más generalista, basados en lenguajes de programación comunes (como Python, Java, .NET o PHP) y en frameworks muy usados (Django, Spring o Symphony son algunos), que facilitan gran parte del desarrollo de la aplicación.

En empresas más _techies_ vemos más variabilidad y adaptabilidad. Sus desarrollos pueden ser productos totalmente a medida y son reemplazados con mayor frecuencia. Por ejemplo, algunos de los servicios ofertados por GCP o AWS, nacieron como productos internos que solucionaban problemas específicos (BigQuery, Hadoop o S3 son buenos ejemplos).

Ante una aplicación antigua, que presenta problemas, recomiendan [su reescritura]((https://timeular.com/blog/rewriting-an-existing-web-service-in-rust/) usando nuevos patrones y tecnologías. Esto mejora su eficacia y evita que tengamos que mantener software obsoleto.

Me parece una metodología de trabajo muy positiva que aprovecha la experiencia y el conocimiento acumulado por la comunidad para innovar. Además, existen lenguajes que son mucho más eficientes que otros para ciertos casos de uso. Discord utiliza Erlang, Rust o Go (entre otros) según las necesidades del servicio. Recomiendo que le echéis un ojo a sus post sobre _Engineering_ porque son increíbles.

La vida media de un microservicio en Uber [es de un año y medio](https://eng.uber.com/microservice-architecture/) y podemos ver patrones similares sobre reemplazo de servicios _legacy_ en [The Site Reliability Workbook](https://sre.google/workbook/table-of-contents/), publicado por Google, así como en otras publicaciones.

Sin embargo, la reescritura de una aplicación puede ser algo muy costoso, especialmente si su código está muy acoplado (algo muy común) y es un evento que tiende a retrasarse todo lo que sea posible en empresas más tradicionales.


## Conclusión
Este artículo no pretende despotricar hacia Silicon Valley o las empresas puramente digitales. Su capacidad de transformación e innovación es tan increíble como inspiradora. Tan sólo pretendo llamar la atención a aquellos que cómo yo, mientras ayudamos a evolucionar aplicaciones y servicios de terceros, podemos caer en las garras del efecto _WOW_ que pueden provocar algunas tecnologías.

Cada nueva tecnología debe ser probada y recibida de forma crítica para evaluar el esfuerzo que va a suponer su implementación y el valor que va a aportar. Por ejemplo, hoy en día asumimos casi como algo obligatorio el desarrollo de cada aplicación nueva bajo una arquitectura de microservicios, pero no debemos olvidar que empresas como Airbnb, Uber, Zalando o Shopify (entre otras), comenzaron sus plataformas en monolitos y lo sustituyeron por microservicios cuando la escalabilidad y la interdependencia entre equipos de desarrollo, lo volvieron algo inevitable.

No repitamos los errores que han tenido Istio o Uber de crear demasiados microservicios y tener que volver hacia atrás debido haber caído en la trampa de la sobreingeniería. Evitemos caer en la visión de túnel que nos hace tener en cuenta sólo una parte del problema y no el conjunto.

No cometamos el error de intentar grandes saltos cuando la tecnología y la metodología son incrementales. No puedes transformar a una compañía de un día para otro, tiene que ser con constancia y una dirección clara. Una mayor inversión, tanto en personal como en herramientas, puede acelerar el proceso, pero si nuestro equipo apenas domina un par de lenguajes y está comenzando a aplicar una pirámide básica de test, no pensemos en migrar a una plataforma de microservicios multilenguaje, con _service mesh_, _canaries_, _cirtuit breakers_ y _feature flags_, porque la gestión de expectativas ante un caso así, no es realista.

Tampoco busco criticar a las empresas más tradicionales. Ellas también tienen su propia forma de hacer las cosas y su capacidad de adaptación a los cambios se ve restringida por las limitaciones presupuestarias y de personal a las que se enfrentan. Nuestro trabajo como consultores suele ser guiarles de la mejor forma posible, pero siempre con cabeza.

Buscando información para este post, he llegado al blog personal de un desarrollador húngaro llamado Arnold Galovics que me ha provocado un par de carcajadas (adjunto los links en la documentación) bien buenas. Sus comentarios sobre microservicios me han recordado a algunas experiencias que yo personalmente he vivido. Equipos infradimensionados intentando adaptarse a tecnologías punteras que desconocían, equipos inexpertos o con una falta de motivación brutal, etc. 

Creo que ese tipo de políticas, causarán problemas independientemente de la arquitectura de utilices y aunque yo no si considero que los microservicios son el futuro de casi cualquier servicio, en ocasiones pueden ser sobreingeniería. Este comentario en concreto, me parece tremendamente lúcido:

> If the product is a regular end-consumer web-app, for example a store and it’ll take like 5000 users, 100 orders per month for the first 5 years, then probably it’s a bad idea to go with microservices. If the team is going to consist of junior engineers with a single senior developer, probably it’s not a good idea to go with microservices either. If the budget is really small for the project, you’ll end up with a messy system that noone wants to maintain.

Como ya he comentado antes, al trabajar en consultoría con un cliente hay que hacerlo con sentido común (el menos común de los sentidos) y gestionar de la mejor forma posible los recursos que disponemos. Es muy complicado llegar a tener el mismo contexto que tenga una _techie_ por lo que en ocasiones, simplemente conseguir una cierta automatización y una mayor cobertura de testing ya es un paso enorme que nos puede abrir puertas a mejoras mucho mayores. La ingeniería no es un sprint, sino una carrera de fondo.

Es posible que en este post, haya hecho un poco de cherry-picking, pero espero que al menos os haga pensar tanto como a mi.

Un saludo y hasta la próxima.


## Documentación

* [AirBNB's Great Migration: From Monolith to Service-Oriented (ENG)](https://www.infoq.com/presentations/airbnb-soa-migration/)

* [Service-Oriented Architecture: Scaling the Uber Engineering Codebase as We Grow (ENG)](https://eng.uber.com/service-oriented-architecture/)

* [Why and How Netflix, Amazon, and Uber Migrated to Microservices: Learn from Their Experiences (ENG)](https://www.hys-enterprise.com/blog/why-and-how-netflix-amazon-and-uber-migrated-to-microservices-learn-from-their-experience/)

* [From Monolith to microservices at Zalando (ENG)](https://www.youtube.com/watch?v=gEeHZwjwehs)

* [One team at Uber is moving from Microservices to Macroservices (ENG)](http://highscalability.com/blog/2020/4/8/one-team-at-uber-is-moving-from-microservices-to-macroservic.html)

* [Istio as an example of when not to do microservices (ENG)](https://blog.christianposta.com/microservices/istio-as-an-example-of-when-not-to-do-microservices/)

* [Don’t start with microservices in production – monoliths are your friend (ENG)](https://arnoldgalovics.com/microservices-in-production/) and [The Truth About Starting With Microservices (ENG)](https://arnoldgalovics.com/truth-about-microservices/)

* [How WhatsApp scaled to 1 billion users with only 50 engineers (ENG)](https://www.quastor.org/p/how-whatsapp-scaled-to-1-billion)

Revisado a 05/02/2022
