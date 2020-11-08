---
title: "Packer: creando imágenes para cualquier proveedor"
slug: packer-i
authors:
  - tangelov
date: 2018-11-18T10:00:00+02:00
tags:  ["packer"]
categories: ["cloud"]
draft: false
---

Hashicorp es una de las compañías que considero que más están innovando y que más nos están facilitando la vida a los administradores de sistemas para adoptar tecnologías ágiles y nuevas formas de trabajar más orientadas a los proveedores de nube.

Su compromiso con los entornos multi-cloud (privada, pública y mixta) es innegable y su suite de herramientas facilita mucho la transición entre proveedores, evitando que podamos caer en exceso en el llamado [_vendor lock-in_](https://en.wikipedia.org/wiki/Vendor_lock-in)

Una de estas herramientas es [_Packer_](https://www.packer.io/intro/index.html)

![logo-packer](https://storage.googleapis.com/tangelov-data/images/0018-00.png)

<!--more-->

## Introducción
Como bien pone en su documentación, Packer es una herramienta de código abierto que nos permite generar imágenes para diferentes proveedores utilizando una única fuente para todos ellos.

Imaginemos que tenemos un entorno híbrido: parte de nuestra infraestructura está desplegada en AWS y otra parte está en un CPD propio montado sobre servidores de Openstack y VMWare. Ambas partes están conectadas a través de una VPN.
Packer nos permitiría que utilizando algún gestor de configuraciones como Chef, Puppet o Ansible fueramos generando imagenes ya configuradas a nuestro gusto para nuestras instancias tanto en AWS como en VMWare.

No tenemos que pensar que Packer sólo funciona con sistemas de Cloud pública puesto que tiene constructores para Docker, Openstack, VMWare o Virtualbox además de para GCP, Azure o Digitalocean (entre otros).

Personalmente le encuentro de mucha utilidad a la hora de generar POCs y demos o comparar el rendimiento entre diferentes proveedores de Cloud.

## Primeros pasos
Lo primero que debemos realizar es instalarlo. Así que vamos a la página oficial y nos lo descargamos [aquí](https://www.packer.io/downloads.html) y lo añadimos al PATH. Si ahora hacemos ```packer ---help``` este es el resultado que obtendremos.

```bash
tangelol@miau:~/packer$ packer --help
Usage: packer [--version] [--help] <command> [<args>]

Available commands are:
    build       build image(s) from template
    fix         fixes templates from old versions of packer
    inspect     see components of a template
    push        push a template and supporting files to a Packer build service
    validate    check that a template is valid
    version     Prints the Packer version
```

Una vez que tenemos instalado Packer vamos a generar una plantilla válida. Para este primer ejemplo vamos a utilizar Virtualbox y uno de los discos de _OSBoxes_, concretamente el de Ubuntu 18.04.1 y con él vamos a añadir el usuario osboxes para que no pida credenciales al hacer sudo y  vamos a generar un .OVA. Dicho proceso no voy a reproducirlo puesto que está muy extendido en Internet, pero en resumen sería [esto](https://www.maketecheasier.com/import-export-ova-files-in-virtualbox/)

Tras tener un OVA válido y haber instalado Packer podemos empezar a crear plantillas de Packer. Son archivos JSON que estructurados de una determinada manera nos permiten gestionar todo el proceso de configuración y despliegue en la nube. Nosotros en este tutorial vamos a usar los siguientes:

* _builders_: Son los constructores de las imágenes. Si vamos a usar más de un proveedor debemos completar más de uno (AWS, GCP o Azure) y son obligatorios.

* _provisioners_: Son los sistemas y scripts que van a configurar las máquinas que vamos a desplegar gracias a los _builders_.

* _variables_: Son variables que nos van a permitir añadir valores y configuraciones extra a Packer.


He generado la siguiente plantilla:

```json
{
    "builders": [
        {
            "type": "virtualbox-ovf",
            "source_path": "$HOME/Documentos/Ubuntu.ova",
            "ssh_username": "osboxes",
            "ssh_password": "osboxes.org",
            "shutdown_command": "echo 'packer' | sudo -S shutdown -P now"
        }
    ],
    "provisioners": [
        {
            "type": "shell",
            "inline": [
                    "sudo apt-add-repository universe",
                    "sudo apt-get install python3-pip -y",
                    "sudo pip3 install ansible"
            ]
        },
        {
            "type": "ansible-local",
            "playbook_file": "apache.yml"
        }
    ]
}
```
Como en otros ejemplos, vamos a explicar esta plantilla. Se encuentra dividida en tres grupos:

* Dentro de _builders_, hemos configurado uno que se conecta con la OVA antes generada y a la que aplica los _provisioners_ que ahora vamos a enseñar.

* Tenemos dos _provisioners_ uno que mediante comandos de shell prepara el entorno para que ansible funcione en él y otro que aplica un playbook de Ansible que instala apache y que esta accesible [aquí](https://gitlab.com/tangelov/proyectos/raw/master/templates/packer/apache.yml).

Si usamos _packer inspect $nombreplantilla_ podremos ver un resumen del contenido de nuestra plantilla.


## Nuestra primera plantilla
Una vez tenemos nuestra plantilla configurada y nuestros _provisioners_ escritos podemos comenzar a probar. Ahora vamos a validar que la sintaxis de nuestra plantilla es correcta y para ello debemos ejecutar _packer validate virtualbox.json_. En este caso recibiremos el siguiente mensaje:

```bash
Template validated sucessfully.
```

Ahora vamos a aplicarla con _packer build virtualbox.json_. Y este es el resultado:
![packer-example-01](https://storage.googleapis.com/tangelov-data/images/0018-01.gif)

En este caso habremos generado una nueva imagen OVA, que si la arrancamos... veremos que tendrá nuestro Apache instalado.

## Multicloud
Tras haber creado una simple prueba de concepto vamos a realizar un despliegue multicloud con GCPy AWS. Debido a que las nubes públicas no son exactamente iguales, el resultado de la acción de packer va a variar: mientras que en GCP y AWS vamos a crear imágenes, si añadieramos Azure, crearíamos discos duros.

La plantilla que vamos a utilizar es la siguiente, añadiendo configuraciones a _builders_:

```json
{
    "builders": [
        {
        }
    ],

    "provisioners": [
        {
            "type": "shell",
            "inline": [
                    "sudo apt-add-repository universe",
                    "sudo apt-get install python3-pip -y",
                    "sudo pip3 install ansible"
            ]
        },
        {
            "type": "ansible-local",
            "playbook_file": "apache.yml"
        }
    ]
}
```

### Google Cloud Platform
El primero que hemos añadido es Google Cloud y para ello hemos añadido una serie de objectos extra:

```json
{
"variables": {
            "gcp_credentials_json": "{{ env `GCP_CREDENTIALS_JSON` }}",
            "gcp_project_id": "{{ env `GCP_PROJECT_ID` }}",
            "image_naming": "my-apache",
            "gcp_region": "europe-west1",
            "gcp_zone": "europe-west1-b",
            "username": "tangelov"
    },
    "builders": [
        {
            "type": "googlecompute",
            "account_file": "{{ user `gcp_credentials_json` }}",
            "project_id": "{{ user `gcp_project_id` }}",
            "source_image_family": "ubuntu-1804-lts",
            "image_family": "{{ user `image_naming` }}",
            "image_name": "{{ user `image_naming` }}-{{ timestamp }}",
            "machine_type": "n1-standard-1",
            "ssh_username": "{{ user `username` }}",
            "zone": "{{ user `gcp_zone` }}"
        }
    ],
}
```

Como se puede ver, hemos añadido las credenciales para poder conectarnos a la nube (que las pasamos como variables de entorno) y una serie de configuraciones extra para que la imagen creada se llame "_my-apache_". Si hacemos _packer build multicloud.json_ y vamos a la consola de GCP, veremos algo parecido a lo siguiente:

![gcp-image](https://storage.googleapis.com/tangelov-data/images/0018-02.png)

La configuración que podemos darle a nuestras imágenes es muy extensa y puede consultarse [aquí](https://www.packer.io/docs/builders/googlecompute.html)

### Amazon Web Services
El siguiente builder que hemos configurado se conecta contra Amazon Web Services. Sin embargo Packer soporta cuatro formas diferentes de crear instancias en Amazon. Nosotros vamos a usar _amazon-ebs_ por su sencillez pero podemos ver las distintas posibilidades en su documentación.

Lo primero que vamos a hacer es añadir unas variables extras a nuestro fichero para que podamos conectarnos a AWS y además hemos cambiado las regiones a usar puesto que no son exactamente iguales:

```json
{
"variables": {
	    "gcp_credentials_json": "{{ env `GCP_CREDENTIALS_JSON` }}",
	    "gcp_project_id": "{{ env `GCP_PROJECT_ID` }}",
	    "gcp_region": "europe-west1",
	    "gcp_zone": "europe-west1-b",
	    "aws_access_key": "{{ env `AWS_ACCESS_KEY` }}",
	    "aws_secret_key": "{{ env `AWS_SECRET_KEY` }}",
	    "aws_region": "us-east-1",
	    "image_naming": "my-apache",
	    "username": "tangelov"
    }
}
``` 

En este caso vamos a crear una imagen en GCP en Europa y otra en AWS en Estados Unidos.

Una vez hemos añadido las variables, ahora vamos a añadir el builder que nos permita crear las imágenes:

```json
{
	    "type": "amazon-ebs",
	    "access_key": "{{ user `aws_access_key` }}",
	    "secret_key": "{{ user `aws_secret_key` }}",
	    "source_ami_filter": {
	        "filters": {
		    "virtualization-type": "hvm",
		    "name": "ubuntu/images/*ubuntu-bionic-18.04-amd64-server-*",
		    "root-device-type": "ebs"
		},
		"owners": ["099720109477"],
		"most_recent": true
	    },
	    "ami_name": "{{ user `image_naming` }}-{{ timestamp }}",
	    "instance_type": "t2.small",
	    "ssh_username": "ubuntu",
	    "region": "{{ user `aws_region` }}"

}
```

En este caso, las imágenes de Ubuntu gestionadas por Amazon siempre requieren que nos conectemos a través del usuario ubuntu. Lo que más difiere es que en Amazon el filtrado para obtener la imagen de Ubuntu más reciente utiliza un _source\_ami\_filter_ algo más complejo que en GCP.

El resultado final de la plantilla sería éste:

```json
{
    "variables": {
	    "gcp_credentials_json": "{{ env `GCP_CREDENTIALS_JSON` }}",
	    "gcp_project_id": "{{ env `GCP_PROJECT_ID` }}",
	    "gcp_region": "europe-west1",
	    "gcp_zone": "europe-west1-b",
	    "aws_access_key": "{{ env `AWS_ACCESS_KEY` }}",
	    "aws_secret_key": "{{ env `AWS_SECRET_KEY` }}",
	    "aws_region": "us-east-1",
	    "image_naming": "my-apache",
	    "username": "tangelov"
    },	    
    "builders": [
        {
	    "type": "googlecompute",
	    "account_file": "{{ user `gcp_credentials_json` }}",
	    "project_id": "{{ user `gcp_project_id` }}",
	    "source_image_family": "ubuntu-1804-lts",
	    "image_family": "{{ user `image_naming` }}",
	    "image_name": "{{ user `image_naming` }}-{{ timestamp }}",
	    "machine_type": "n1-standard-1",
	    "ssh_username": "{{ user `username` }}",
	    "zone": "{{ user `gcp_zone` }}"
	},
	{
	    "type": "amazon-ebs",
	    "access_key": "{{ user `aws_access_key` }}",
	    "secret_key": "{{ user `aws_secret_key` }}",
	    "source_ami_filter": {
	        "filters": {
		    "virtualization-type": "hvm",
		    "name": "ubuntu/images/*ubuntu-bionic-18.04-amd64-server-*",
		    "root-device-type": "ebs"
		},
		"owners": ["099720109477"],
		"most_recent": true
	    },
	    "ami_name": "{{ user `image_naming` }}-{{ timestamp }}",
	    "instance_type": "t2.small",
	    "ssh_username": "ubuntu",
	    "region": "{{ user `aws_region` }}"

	}
    ],
    
    "provisioners": [
	{
	    "type": "shell",
	    "inline": [
		    "sleep 90",
		    "sudo apt-get update",
		    "sudo apt-get install python3-pip -y",
	            "sudo pip3 install ansible"
	    ]
	},
        {
	    "type": "ansible-local",
	    "playbook_file": "apache.yml"
	}
    ]
}
```

Si ahora hicieramos _packer build multicloud.json_ veríamos algo parecido a esto:
![global-build-01](https://storage.googleapis.com/tangelov-data/images/0018-03.png)

![global-build-02](https://storage.googleapis.com/tangelov-data/images/0018-04.png)

![global-build-03](https://storage.googleapis.com/tangelov-data/images/0018-05.png)

Si además fuesemos a las consolas de las nubes, veríamos lo siguiente (lo he lanzado dos veces):
![global-image-01](https://storage.googleapis.com/tangelov-data/images/0018-06.png)

De esta forma, podríamos portar de una manera relativamente simple o hacer pruebas en diferentes proveedores de nube. En el futuro escribiré más posts al respecto.


## Limpieza
Si alguien quiere rehacer este taller puede consultar los ficheros que he creado [aquí](https://gitlab.com/tangelov/proyectos/tree/master/templates/packer).

Para evitar costes no previstos si estamos utilizando los tier gratuitos debemos borrar los siguientes recursos:

* En AWS debemos borrar las imágenes (AMIs) y las snapshots generadas, dentro de EC2 / Elastic Block Store
.
* En GCP debemos borrar las imágenes y los discos, dentro del Compute Engine.


## Documentación

* [¿Qué es Packer? (ENG)](https://www.packer.io/intro/index.html)

* [Configuración de Azure en Packer (ENG)](https://www.packer.io/docs/builders/azure-setup.html)

* [Configuración de GCP en Packer (ENG)](https://www.packer.io/docs/builders/googlecompute.html)

* [Configuración de AWS en Packer (ENG)](https://www.packer.io/docs/builders/amazon.html)

* [Página principal de OSBoxes (ENG)](https://www.osboxes.org/)

Revisado a 01/02/2020
