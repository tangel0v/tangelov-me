---
title: "Controlando el trabajo repetitivo"
slug: controlling-toil
authors:
  - tangelov
date: 2023-03-12T10:00:00+02:00
tags:  ["devops", "gitlab", "ci"]
categories: ["devops"]
draft: false
---

En un mundo cada vez más digitalizado y acelerado, aparecen nuevos servicios de forma constante para ofrecer soluciones a los problemas cotidianos que nos encontramos en IT. Gracias a una barrera de entrada cada vez más baja, podemos tenerlos listos y funcionando con un poco de conocimiento técnico y siguiendo la propia guía del fabricante (cuando no tienes acceso directamente a su SaaS).

Aunque es algo positivo, puede llegar a convertirse en una _trampa_. Cada nuevo servicio que añadimos a nuestro stack añade un punto extra de complejidad y mantenimiento y puede que no merezca la pena. Siempre tenemos que decidir entre las funcionalidades y el mantenimiento de dicho servicio. Además, la instalación siempre es la parte que menos trabajo da y posteriormente necesitaremos mantenerlo actualizado, gestionar sus dependencias, y más esporádicamente, realizar migraciones entre versiones.

Aunque Docker y los contenedores facilitan mucho esta tarea, incorporan otros puntos de fricción. Si utilizamos Kubernetes necesitamos tener en cuenta que nuestros servicios soporten las APIs correctamente, que estemos en versiones soportadas, que nuestra aplicación sea segura, etc.

En este post voy a explicar cómo he hecho para gestionar el mantenimiento de servicios y cómo estoy optimizando todo el proceso para que el tiempo que tengo que dedicarle sea cómodo para mi. Espero que os guste.

<!--more-->

## Un poco de contexto
Fuera del trabajo, mantengo la infraestructura de un par de blogs y un par de servidores que tengo desplegados en casa. Siempre a modo de hobby, pero tratando de ser lo más profesional posible. Para ello, me autoimpuse una serie de normas que intento seguir a rajatabla:

* Toda la infraestructura y sus despliegues deben hacerse con código y automatizarse si merece la pena.
* No existen las _deadlines_. Cualquier mejora puede ser pospuesta hasta que me apetezca hacerla o tenga tiempo efectivo.
* El tiempo de mantenimiento en total no puede superar las 2 horas mensuales.

Estas tres reglas me han permitido mantener mis servicios en el tiempo sin agobiarme. He visto a mucha gente empezar un proyecto personal y quemarse en poco tiempo al no poder gestionar sus propias expectativas o por verse enterrado en montañas de tareas causadas de todo lo que habían montado inicialmente.

Aunque siempre me gustaría hacer un poco más, en general estoy bastante contento. Mis servicios tienen unos SLAs que podrían ser la envidia de algunas compañías y siguen muchas de las buenas prácticas de la industria en cuanto a seguridad. Sin embargo, estas limitaciones también han hecho que no añada algunos servicios que quería probar por superar la regla total de las dos horas mensuales.

Para añadir más servicios tengo tres alternativas: 

* Asumir que la ley de las dos horas no es realista y ampliar el tiempo dedicado a mantenimiento si añado más servicios.
* Buscar gente que colabore conmigo y compartir el tiempo de mantenimiento.
* Optimizar los procesos actuales para liberar tiempo.

Y la tercera fue la opción elegida.

### SRE: Site Reliability Engineering
La lectura de los dos libros sobre _Site Reliability Engineering_ (SRE), publicados por Google, ha sido vital a la hora de tomar esta decisión.

Site Reliability Engineering es una _nueva_ disciplina que busca eliminar los huecos existentes entre el desarrollo y la operación de aplicaciones y servicios. Su premisa consiste en que los equipos de Dev y Ops colaboren desde la creación de la aplicación para detectar posibles problemas y en el uso de software para gestionar el ciclo de vida de la misma, automatizando las tareas siempre que sea posible.

En ocasiones, la decisión de ciertos componentes de una aplicación (como una base de datos relacional, por ejemplo), puede simplemente mover la carga de trabajo del desarrollo a las operaciones o viceversa y la colaboración desde el minuto uno permite detectar posibles errores.

Estas prácticas nacieron en Google (al menos bajo la terminología de SRE) y se han popularizado durante los últimos años. Pese a que encontré algunos de los consejos bastante irrealizables fuera del mundillo de las grandes techies, si pienso que su idea sobre cómo se debe gestionar el _toil_ es acertada y vital para controlar el _burnout_ de los miembros de un equipo.

_Toil_ significa en inglés _trabajo duro o repetitivo_, y en informática supone la inmensa mayoría del trabajo de un equipo de operaciones. Se corresponde con el mantenimiento de una aplicación: parches de seguridad, actualización de librerías, gestión de dependencias, etc.

Aunque es __necesario__ para que una aplicación sea segura, apenas aporta valor para el usuario final: no suele aportar nuevas funcionalidades al servicio y además es algo bastante desagradecido. Nadie es ascendido por mantener bien una aplicación, así que la gente prefiere dedicarse a otras tareas y sin procesos fuertes, es común que se deje de lado.

En mi caso, la mayoría de mi trabajo repetitivo es la revisión y la gestión de las dependencias que utilizan mis aplicaciones y servicios, con casi un 80% del tiempo total mensual.


## Una vuelta de tuerca a Renovate
Para ser más eficiente, pensé que podía darle una vuelta de tuerca a [Renovate](https://tangelov.me/posts/gestion-de-dependencias.html).

Renovate es una herramienta que nos permite, de forma automática, hacer un seguimiento a las dependencias que utilizamos en nuestros proyectos. Cuando una dependencia publica una nueva versión, Renovate crea un _Merge Request_ en nuestro repositorio para que lo revisemos. En este post, se va a asumir que ya lo estamos utilizando, puesto que ya traté en el blog cómo instalarlo e integrarlo con Gitlab. Si alguien tiene dudas sobre cómo hacerlo, le recomiendo que revise el post adjunto.

Tras dos años utilizando Renovate, el proceso de gestión dependencias es el mismo:
* Renovate abre distintos Merge Requests a lo largo del mes y se van acumulando.
* Aprovechando las ventanas de mantenimiento mensuales, reviso y mergeo manualmente cada dependencia y valido su funcionamiento.
* Tras mergear las dependencias, se realiza un despliegue automático.

El principal problema del proceso de revisión de los _Merge Request_ es que es __activo__. Es un trabajo que me obliga a estar pendiente del proceso y que no puedo compaginar con otras tareas domésticas (como sí hago con el despliegue).

Lo primero que hice fue investigar cuán flexible era Renovate y cómo podía adaptar su comportamiento a mis necesidades. Mi objetivo era mergear de forma automática cualquier dependencia que no fuese una _major_ puesto que tras dos años usándolo, no he tenido incidencias relacionadas con este tipo de actualizaciones.

Por ejemplo, si una librería se actualiza de la versión 1.9.0 a la versión 1.9.1 o a la 1.10.0, dicha actualización debería ser automática y sin revisión manual. Si por el contrario, la actualización salta de la versión 1.9.0 a la 2.0.0, quiero que el _Merge Request_ se cree, pero sin seguir el resto del proceso.

Renovate aporta para algunas dependencias (Python, Javascript y Java) unas _badges_ que ayudan a ver si las dependencias son seguras o no (con porcentajes de uso y validaciones), pero no era lo que buscaba. Tras un rato buscando distintas opciones por su documentación, logré tener un resultado que se ajustaba a lo que quería. Llegados a este punto, los ficheros de configuración de Renovate quedaron así:

```json
{
  "extends": [
    "config:base"
  ],
  "prConcurrentLimit": 0,
  "rebaseWhen": "auto",
  "masterIssue": true,
  "pip_requirements": {
    "fileMatch": [
      "requirements.txt",
      "requirements-test.txt"
    ]
  },
  "packageRules": [
    {
      "matchUpdateTypes": [
        "minor",
        "patch",
        "pin",
        "digest"
      ],
      "matchCurrentVersion": "!/^0/",
      "automerge": true,
      "automergeType": "pr",
      "platformAutomerge": true
    }
  ]
}
```

Los cambios respecto a la configuración [original](https://gitlab.com/tangelov-functions/messages-to-matrix/-/blob/98549cb2ed59e5dc52575ad949624ee26f566019/renovate.json) habilitan lo siguiente:

* Se habilita el automergeo, basándose en _Pull Requests_.
* Sólo se permite el automergeo cuando la actualización sea de tipo _minor_, _patch_, _pin_, _digest_ y si cumplen un determinado patrón.
* Se habilita _platformAutomerge_ para integrarlo mejor con Gitlab que el sistema que ofrece por defecto.

> _PlatformAutomerge_ permite el uso nativo de las APIs nativas de Github, Gitlab y Azure DevOps y no funciona con otros proveedores. Debido a las diferencias entre las plataformas de Git que existen, el soporte de Renovate difiere y antes de seguir este tutorial, recomiendo revisar bien su documentación.

Este comportamiento es especialmente útil para mantener el código de Python de las Cloud Functions que uso debido a que sus dependencias se actualizan habitualmente, pero lo he extendido a los módulos y proveedores de Terraform (y a futuro lo haré con mis playbooks de Ansible). Busco que siempre que sea posible, las máquinas trabajen por mi :D .

Después de haber aplicado los cambios, detecté que tenía algún error en la configuración. El sistema funcionaba perfectamente en algunos repositorios pero e no en otros y tuve que volver a ponerme a buscar. Tras releer la documentación de Renovate,  descubrí que el automergeo de ramas requería tener pipelines de testing o deshabilitar dicha verificación lo cual no me parecía buena idea.

Pese a que quizás el proceso se estaba complicando de más, el código de mis funciones es sencillo y en apenas un par de horas añadí algún test utilizando la documentación oficial:


```python
import os, sys
from unittest import mock

# We install all the dependencies in the folder lib
file_path = os.path.dirname(__file__)
module_path = os.path.join(file_path, "../lib")
sys.path.append(module_path)

# We import the main library from the parent folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main

# Create a mock context
mock_context = mock.Mock()
mock_context.event_id = '612345678901234'
mock_context.timestamp = '2023-01-01T22:00:00.000Z'
mock_context.resource = {
    'name': 'projects/my-dummy-project/topics/my-dummy-project',
    'service': 'pubsub.googleapis.com',
    'type': 'type.googleapis.com/google.pubsub.v1.PubsubMessage',
}

# Demo data with "Integration test for messages-to-matrix-function"
mock_context.data = {
    'data': '"SW50ZWdyYXRpb24gdGVzdCBmb3IgbWVzc2FnZXMtdG8tbWF0cml4IGZ1bmN0aW9u"'
}

# Checking e2e functionality in the main checking_backup function
def test_main_function():
    checking = main.messages_to_matrix(mock_context.data, mock_context)
    assert "messages-to-matrix" in checking
```

Mis funciones son sencillas y se utilizan para integrar distintos eventos, son básicamente disparadores para llamar a otros servicios. Por ello, decidí realizar un test end-to-end completo que replicase la funcionalidad de la aplicación. Esta decisión me obligó a simular el entorno de ejecución al completo y a mejorar el entorno de desarrollo para que todo funcionase como la seda.

A la hora de integrar Terraform, todo fue mucho más sencillo puesto que el sistema de testing ya era [consistente](https://tangelov.me/posts/opa.html). Y ahora sí, a la segunda, todo funcionaba como quería.


## Conclusión
Este desarrollo se hizo el mes pasado y aunque quizás es un poco pronto, estoy bastante contento con el resultado. El proceso de leer la documentación, montar el sistema y probarlo me llevó como diez horas y ha reducido el tiempo dedicado a mantenimiento en torno a la mitad.

¿Ha merecido la pena? Indudablemente si. Tardaré unos seis meses en recuperar lo invertido, pero me ha aportado conocimiento para escribir este post y ahora me da mucho menos pereza hacer el mantenimiento. El siguiente paso es elegir los nuevos servicios que voy a meter y sobre todo, cómo voy a integrarlos en este sistema de testing.

Soy consciente de que no es un sistema perfecto (aunque no he tenido ningún problema). Si un desarrollador no sigue la nomenclatura estándar, el sistema puede mergear cosas que no debe, pero espero que los tests lo detecten y lo impidan.

En cualquier caso, si manteneis algún servicio, os animo a todos a hacer este ejercicio, puesto que algo que sea _barato_ puede no serlo tanto si al final requiere de mucho tiempo de trabajo. 

Un saludo y gracias por vuestra atención, hasta más ver.


## Documentación

* [Página oficial de Google sobre SRE (ENG)](https://sre.google)
* [Libros oficiales de Google sobre SRE (ENG)](https://sre.google/books/)
* [¿Qué es la ingeniería de confiabilidad del sitio (SRE)?](https://www.redhat.com/es/topics/devops/what-is-sre)
* [Merge confidence in Renovate (ENG)](https://docs.renovatebot.com/merge-confidence/)
* [Automerge configuration in Renovate (ENG)](https://docs.renovatebot.com/key-concepts/automerge/)
* [Testing Event Driven Functions (ENG)](https://cloud.google.com/functions/docs/testing/test-event)

Revisado a 12-03-2023
