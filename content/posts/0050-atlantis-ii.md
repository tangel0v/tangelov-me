---
title: "Atlantis: best practices y limitaciones"
slug: atlantis-ii
authors:
  - tangelov
date: 2022-11-12T09:00:00+02:00
tags:  ["devops", "terraform", "sops"]
categories: ["cloud"]
draft: false
---

Este es el tercer y último post sobre Atlantis que voy a escribir para esta serie. Si los dos primeros explicaban cómo configurar la herramienta y cómo desplegarla sobre Cloud Run, en éste vamos a aplicar algunas buenas prácticas y a mejorar la solución, por lo que asumimos que se han leído los dos anteriores ([I](https://tangelov.me/posts/atlantis-i.html) y [II](https://tangelov.me/posts/cloud-run.html)).

El [primer post](https://tangelov.me/posts/atlantis-i.html) de la serie, creaba en el servicio de Atlantis una serie de variables de entorno, que tras convertirse temporalmente en ficheros _[tfvars](https://developer.hashicorp.com/terraform/language/values/variables#variable-definitions-tfvars-files)_, nos permitían inicializar y ejecutar nuestro código.

Esta solución, aunque servía como ejemplo, también tenía muchas limitaciones:

* No escala. Las variables de entorno sólo pueden tener un valor al mismo tiempo. Si nuestra instancia gestiona múltiples proyectos con las mismas variables de entorno, no podría reutilizarlas con seguridad y además, deben de definirse en el servidor, obligando a redesplegar / reiniciar la solución en cada cambio. 

* Los proyectos _cliente_ deben estar autocontenidos, para evitar en la medida de lo posible dependencias externas ajenas a su control y que impacten en su desarrollo.

* Tal y cómo estaba configurado, tampoco nos proporcionaba garantías ante despliegues más automatizados y por eso vamos a añadir testing.

<!--more-->


## Integrando SOPS en nuestro repositorio
La primera parte de este post se va a centrar en solucionar los dos primeros puntos de fricción: vamos a eliminar las variables de entorno y a contener todas las dependencias de cada proyecto en un único punto. Para ello, vamos a utilizar una herramienta de gestión de secretos que nos permita su almacenamiento de forma cifrada dentro de nuestros repositorios de código. Aunque hay distintas posibilidades, mi favorita es [SOPS](https://tangelov.me/posts/sops-i.html).

Al interactuar con múltiples sistemas de gestión de llaves de cifrado y soportar de forma nativa la solución de GCP (Cloud KMS), la elección de SOPS es natural.

Antes de nada necesitamos crear una nueva clave de Cloud KMS para ser utilizada por SOPS. Accedemos a GCP a través de la consola, habilitamos la API de Cloud KMS, creamos un _keyring_ de nombre _"atlantis"_ y una nueva llave, con el mismo nombre:

![cloud-kms](https://storage.googleapis.com/tangelov-data/images/0050-00.png)

> Si alguien revisa el código adjunto verá que he preferido dejar esta llave fuera de Terraform para evitar que por error pudiera ser borrada en un plan y perdiéramos el acceso a todos los secretos cifrados con ella.

Una vez tenemos la llave ha sido creada, ahora necesitamos configurar una serie de permisos en GCP para que pueda ser utilizada por todos los actores involucrados:

* Los desarrolladores de los repositorios cliente necesitan el rol  _Cloud KMS CryptoKey Encrypter/Decrypter_ puesto que van a crear y mantener los ficheros _tfvars_ cifrados.

* La cuenta de servicio utilizada en GCP por Atlantis tiene que poder descifrar los ficheros, así que le asignamos el rol _Cloud KMS CryptoKey Decrypter_ sobre la clave antes creada.

En Terraform, nuestro código quedaría de la siguiente manera:

```hcl
## Data sources para acceder a la clave de Cloud KMS desde Terraform
## Se puede gestionar desde el repositorio de Atlantis u cualquier otro
data "google_kms_key_ring" "atlantis" {
  name     = "atlantis"
  location = var.gcp_default_region
}

data "google_kms_crypto_key" "atlantis" {
  name     = "atlantis"
  key_ring = data.google_kms_key_ring.atlantis.id
}


## Recursos para que los usuarios puedan cifrar y descifrar los ficheros
resource "google_kms_crypto_key_iam_policy" "atlantis_kms_write" {
  crypto_key_id = data.google_kms_crypto_key.atlantis.id
  policy_data = data.google_iam_policy.kms_write.policy_data
}

data "google_iam_policy" "kms_write" {
  binding {
    role = "roles/cloudkms.cryptoKeyEncrypterDecrypter"

    members = [
      "group:developers@tangelov.me",
    ]
  }
}


## Recursos para que Atlantis pueda descifrar los ficheros
resource "google_kms_crypto_key_iam_policy" "atlantis_kms" {
  crypto_key_id = data.google_kms_crypto_key.atlantis.id
  policy_data = data.google_iam_policy.kms.policy_data
}

data "google_iam_policy" "kms" {
  binding {
    role = "roles/cloudkms.cryptoKeyDecrypter"

    members = [
      "serviceAccount:${google_service_account.atlantis_sa.email}",
    ]
  }
}
```

Con estos cambios, tanto Atlantis como los desarrolladores pueden comunicarse utilizando ficheros cifrados, pero estos no existen aún. Para crearlos, necesitamos configurar SOPS en el repositorio cliente, creando un fichero en la raíz del mismo de nombre _.sops.yaml_ con el siguiente contenido:

```yaml
creation_rules:
  - gcp_kms: projects/proyecto1/locations/region1/keyRings/atlantis/cryptoKeys/atlantis
```

De esta forma le decimos a SOPS que debe cifrar los ficheros con la llave _atlantis_ de Cloud KMS en el proyecto1 en la region1. Para crear los ficheros, tan sólo usamos los comandos ```sops init-tfvars/prd.tfvars.enc``` y ```sops apply-tfvars/prd.tfvars.enc```

Si hubiéramos metido la pata y los permisos no fuesen los correctos, recibiríamos un error como el siguiente:

```bash
Failed to get the data key required to decrypt the SOPS file.

Group 0: FAILED
  projects/proyecto1/locations/region1/keyRings/atlantis/cryptoKeys/atlantis: FAILED
    - | Error decrypting key: googleapi: Error 403: Permission
      | 'cloudkms.cryptoKeyVersions.useToDecrypt' denied on resource
      | 'projects/projecto1/locations/region1/keyRings/atlantis/cryptoKeys/atlantis'
      | (or it may not exist)., forbidden
```

SOPS no impide que nuestros desarrolladores sigan probando su código a mano:

```bash
# Desciframos el fichero de init-tfvars y ejecutamos terraform init
sops -d init-tfvars/prd.tfvars.enc > init-tfvars/prd.tfvars
terraform init -backend-config ./init-tfvars/prd.tfvars

# Desciframos el fichero de apply-tfvars y ejecutamos terraform plan, apply, etc
sops -d init-tfvars/prd.tfvars.enc > init-tfvars/prd.tfvars
terraform apply -var-file ./apply-tfvars/prd.tfvars

# Limpiamos
rm init-tfvars/prd.tfvars apply-tfvars/prd.tfvars
```

Nuestros desarrolladores ya pueden trabajar con SOPS, pero... ¿Cómo hacemos lo mismo con Atlantis?


### Añadiendo SOPS a nuestro contenedor
Aunque Atlantis permite la ejecución de comandos personalizados dentro de sus workflows, difícilmente va a poder hacerlo si no tiene la herramienta a mano. Por ello antes de cambiar nada en el workflow, tenemos que modificar el Dockerfile de Atlantis para añadirlo al contenedor. Con añadir estas pocas líneas bastaría:

```
# Download sops from Internet
ENV DEFAULT_SOPS_VERSION=3.7.3
RUN curl -Ls https://github.com/mozilla/sops/releases/download/v${DEFAULT_SOPS_VERSION}/sops-v${DEFAULT_SOPS_VERSION}.linux.amd64 -o /usr/local/bin/sops && \
    chmod +x /usr/local/bin/sops
```

Una vez hemos modificado el [fichero](https://gitlab.com/canarias2/atlantis/-/raw/main/docker/Dockerfile), tan sólo tenemos que construir de nuevo la imagen y redesplegar el servicio. De esta  forma, SOPS puede ser utilizado sin problemas por Atlantis.

Ahora sólo tenemos que actualizar el workflow que hemos definido en el repositorio cliente (atlantis.yaml) para integrar SOPS y ya estaría:

```yaml
version: 3
automerge: false
delete_source_branch_on_merge: true
parallel_plan: true
parallel_apply: true
projects:
- name: dummy
  dir: .
  terraform_version: v1.2.8
  delete_source_branch_on_merge: true
  apply_requirements: [mergeable, approved]
  workflow: standard
workflows:
  standard:
    plan:
      steps:
      - run: sops -d init-tfvars/prd.tfvars.enc > init-tfvars/prd.tfvars
      - run: sops -d apply-tfvars/prd.tfvars.enc > apply-tfvars/prd.tfvars
      - init:
          extra_args: ["-backend-config", "./init-tfvars/prd.tfvars"]
      - plan:
          extra_args: ["-var-file", "./apply-tfvars/prd.tfvars"]
      - run: rm init-tfvars/prd.tfvars apply-tfvars/prd.tfvars
allowed_regexp_prefixes:
- feature/
- fix/
```

Como podemos ver, la ejecución funciona correctamente:

![atlantis-with-sops](https://storage.googleapis.com/tangelov-data/images/0050-01.png)


## Testing con Conftest
Tras asegurar que nuestros secretos pueden ser almacenados de forma segura, ahora vamos a mejorar más la calidad de la solución añadiendo testing. Utilizando _Unit Testing_ podemos garantizar que se cumplan una serie de buenas prácticas dentro de nuestros _planes_ de Terraform. Esta funcionalidad, aunque está en beta, es nativa en Atlantis gracias al uso de _conftest_, una CLI de la que ya he hablado [en posts anteriores](https://tangelov.me/posts/opa.html).

Gracias a Conftest, podemos escribir tests en Rego que aseguren un mínimo de calidad y seguridad en nuestra infraestructura. Es algo vital a la hora de evitar problemas, especialmente si queremos implementar CI/CD completo para nuestra infraestructura como código. Actualmente la integración nativa de Atlantis para testing tiene las siguientes características:

* No está habilitada por defecto y hacerlo, requiere modificar la configuración general o el arranque del servicio.

* Una vez habilitada, se configura dentro del [repo.yaml](https://gitlab.com/canarias2/atlantis/-/raw/main/docker/dummy_repo_config.yaml) en el servidor de Atlantis y solo puede referenciar a carpetas locales, [sin dar soporte a carpetas remotas](https://github.com/runatlantis/atlantis/issues/2454).

Aunque la documentación de la funcionalidad es regular y no explica paso a paso como usarla, yo si voy a hacerlo. Primero añadimos al fichero de configuración del servidor la siguiente linea:

```yaml
enable-policy-checks: "true"
```

Así habilitaríamos la funcionalidad en el siguiente reinicio o despliegue. El siguiente paso es definir qué políticas se van a aplicar, quien es el encargado de revisarlas si fallan y su ubicación. Nuestro fichero repo.yaml quedaría así:

```yaml
repos:
 - id: /.*/
   allowed_overrides: [workflow, apply_requirements, delete_source_branch_on_merge]
   allow_custom_workflows: true
policies:
  owners:
    users:
      - tangelov
  policy_sets:
    - name: non-deletion
      path: /home/atlantis/.atlantis
      source: local
```

Como se puede ver, hemos generado una política llamada _non-deletion_, que almacena las políticas en la carpeta _/home/atlantis/.atlantis_ y que puede ser revisada en caso de fallo por _tangelov_.

Tras estas modificaciones, ya podemos reiniciar el servicio o recrear el contenedor y comenzar a configurar el repositorio cliente. Vamos a definir un nuevo paso en nuestro workflow donde se ejecutarán los tests:

```yaml
workflows:
  standard:
    plan:
      steps:
      - run: sops -d init-tfvars/prd.tfvars.enc > init-tfvars/prd.tfvars
      - run: sops -d apply-tfvars/prd.tfvars.enc > apply-tfvars/prd.tfvars
      - init:
          extra_args: ["-backend-config", "./init-tfvars/prd.tfvars"]
      - plan:
          extra_args: ["-var-file", "./apply-tfvars/prd.tfvars"]
      - run: rm init-tfvars/prd.tfvars apply-tfvars/prd.tfvars
    policy_check:
      steps:
      - show
      - policy_check:
          extra_args: ["-p ${PWD}/policy/" , "--all-namespaces"]
```

Para que no haya dudas, vamos a explicar un poco más los añadidos al workflow:

* Hemos creado un nuevo paso llamado policy\_check que se ejecuta tras el _plan_.

* Primero ejecutamos show para que Atlantis genere un plan de Terraform en formato JSON. Es __obligatorio__ para poder pasar los tests después y de lo contrario el pipeline fallará.

* Ejecutamos los tests, pero modificando ligeramente su comportamiento. Por defecto, Atlantis sólo ejecuta un [_namespace_](https://www.openpolicyagent.org/docs/latest/policy-language/#packages) o _package_ y sólo busca tests en los ficheros locales del servidor. De esta forma nos aseguramos que pasen todos los tests y que podemos añadir tests extra en el repositorio que vamos a desplegar si queremos.

Ahora mismo el sistema es bastante limitado. Si seleccionamos una carpeta que no contenga tests, ni falla da detecta errores y si queremos añadir nuevos policy sets, tenemos que añadirlos al fichero repo.yaml y reiniciar Atlantis puesto que el servicio [no recarga su configuración](https://github.com/runatlantis/atlantis/issues/330) ni utilizando variables de entorno.

Para no tener este cuello de botella, hemos añadido al ejemplo un workaround. Al añadir ```-p ${PWD}/policy/``` a la ejecución de Conftest, le indicamos que mire dentro del propio repositorio cliente en la carpeta policy además de en la carpeta que Atlantis configura por defecto. Así podemos añadir tests de manera más dinámica, mientras mantenemos la integración entre Atlantis y Conftest.

Si ahora ejecutamos nuestro repositorio _dummy_ a través de Atlantis, recibiremos este error:

![atlantis-conftest-error](https://storage.googleapis.com/tangelov-data/images/0050-02.png)

 Como no estamos cumpliendo las reglas de etiquetado impuestas en los tests, podemos o pedir al administrador que nos apruebe el cambio de forma manual, o adaptar nuestro código para que pase los tests.

![atlantis-conftest-val](https://storage.googleapis.com/tangelov-data/images/0050-03.png)

Los tests añadidos comprueban si un recurso va a ser borrado, reemplazado o si está mal etiquetado según las normas definidas. Por ello, nuestro último paso va a ser habilitar el _automerge_ en el repositorio de ejemplo. Así nuestros ramas se mergearán automáticamente si se pasan todos los tests y el plan es aplicado.

![atlantis-automerge](https://storage.googleapis.com/tangelov-data/images/0050-04.png)


## Extra: Terraform Cloud
Atlantis puede integrarse con Terraform Cloud y lo hace de forma sencilla, tan sólo tenemos que modificar dos cosas:

* El fichero donde indicamos el _remote_ del estteriormente necesitaremos mantenerlo actualizado, gestionar sus dependencias, y más esporádicamente, realizar migraciones entre versiones.

Aunque Docker y los contenedores facilitan mucho esta tarea, incorporan otros puntos de fricción. Si utilizamos Kubernetes necesitamos tener en cuenta que nuestros servicios soporten las APIs correctamente, que estemos en versiones soportadas, que nuestra aplicación sea segura, etc.

En este post voy a explicar cómo he hecho para gestionar el mantenimiento de servicios y cómo estoy optimizando todo el proceso para que el tiempo que tengo que dedicarle sea cómodo para mi. Espero que os guste.

Un poco de contexto
Fuera del trabajo, mantengo la infraestructura de un par de blogs y un par de servidores que tengo desplegados en casa. Siempre a modo de hobby, pero tratando de ser lo más profesional posible. Para ello, me autoimpuse una serie de normas que intento seguir a rajatabla:

Toda la infraestructura y sus despliegues deben hacerse con código y automatizarse si merece la pena.ado para que apunte a un workspace de Terraform Cloud.

* Crear una variable de entorno con un token para acceder a dicho workspace.

En resumen:

```hcl
terraform {
  cloud {
    organization = "tangelov"
    workspaces {
      name = "dummy"
    }
  }
```

```hcl
 # Definimos una nueva variable de entorno en el despliegue que coge el valor
 # del token de un secreto en GCP
 env {
          name = "ATLANTIS_TFE_TOKEN"
          value_from {
            secret_key_ref {
              key = "latest"
              name = google_secret_manager_secret.atlantis_tfe_token.secret_id
            }
          }
        }
```

La integración nos permite utilizar el almacenamiento del estado de Terraform en la nube, pero si intentamos hacer ejecuciones remotas debido a nuestra configuración actual, fallarán a la hora de generar cualquier plan:

```
│ Error: Saving a generated plan is currently not supported
│ 
│ Terraform Cloud does not support saving the generated execution plan
│ locally at this time.
```


## Conclusiones finales
En general he disfrutado mucho con este "mini" proyecto de investigación y he aprendido mucho tanto de Terraform Cloud (ya hablaremos del tema) como de Atlantis. Sin embargo, es fácil ver que ambas soluciones se solapan y que una está recibiendo mucho más cariño que la otra últimamente.

Aunque la gestión relacionada con la seguridad (secretos, grupos, almacenamiento del estado, etc.) es mucho mejor en Terraform Cloud, hoy sólo nos vamos a centrar en los puntos fuertes y los flacos de Atlantis.

Como ya hemos comentado anteriormente, Atlantis es una herramienta enfocada al uso de GitOps, pero no me ha permitido hacer todo lo que me hubiera gustado. He sido incapaz de aplicar automáticamente el código tras pasar los tests y hacer que éste se mergeara. Parece que su diseño obliga a pasar por una validación a través de comentarios en Gitlab o Github en cuanto añades tests (y no voy a aplicar automáticamente nada sin testing) y deja el siguiente paso en espera, obligándonos a poner ```atlantis apply -p dummy```. 

Debido a mi experiencia profesional, esto me preocupa porque en entornos grandes y complejos, los pipelines genéricos pueden generar muchos comentarios (ruido) y no tienen porqué adaptarse a sus necesidades. Por ejemplo, es habitual que hasta que no se mergee a _main_ el código no sea aplicado en Producción y esto no lo podemos hacer con Atlantis.

Aparte de esto, me sigue pareciendo una herramienta muy versátil y configurable. Podemos añadir cualquier otra CLI (Infracost, Regula o cualquier otra herramienta) al contenedor y personalizar la ejecución al gusto. También podemos gestionar los pipelines de forma centralizada eligiendo qué pueden modificar los usuarios y que no, algo muy útil en determinadas ocasiones y creo que bien configurada puede ser segura y proporcionar workflows de infraestructura consistentes a pequeños equipos de desarrolladores.

En resumen, una herramienta interesante, consistente, que será muy útil a algunos y que se quedará corta a otros. En cualquier caso, espero que os haya gustado esta serie de posts y nos vemos en la siguiente. Un abrazo a todos.


## Documentación
* [Repositorio oficial de SOPS en Github (ENG)](https://github.com/mozilla/sops)

* [Página oficial de Conftest (ENG)](https://www.conftest.dev/)

* [How to enable Conftest policies in Atlantis (ENG)](https://www.runatlantis.io/docs/policy-checking.html)

* [Configure Terraform Cloud with Atlantis (ENG)](https://www.runatlantis.io/docs/terraform-cloud.html#using-atlantis-with-terraform-cloud-remote-operations-or-terraform-enterprise)

* [Repositorio Dummy de Terraform para usar con Atlantis](https://gitlab.com/canarias2/archetype)

* [Repositorio Dummy de Terraform para usar con Atlantis y Terraform Cloud](https://gitlab.com/canarias2/archetype/-/tree/feature/terraform-cloud)


Revisado a 12-11-2022
