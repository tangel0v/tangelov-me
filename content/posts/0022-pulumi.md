---
title: "Pulumi: programando infraestructura"
slug: pulumi
authors:
  - tangelov
date: 2019-03-07T18:00:00+02:00
tags:  ["pulumi", "terraform", "iac"]
categories: ["cloud"]
draft: false
---

En el [post anterior](https://tangelov.me/posts/terraform-i.html) hablamos por encima de infraestructura como código y la importancia de utilizar herramientas que podamos utilizar en el proveedor que queramos para evitar tener que estar aprendiendo lenguajes y sintaxis nuevos cada vez que utilizamos un proveedor nuevo.

Para ello, Terraform utiliza un lenguaje propio, el _Hashicorp configuration language_ o HCL. Como podemos leer en su Github, la idea detrás de la creación de este lenguaje es que sea de fácil lectura para _máquinas_ y para humanos. También buscaban que no fuese necesario tener conocimientos previos de algún lenguaje de programación y que fuese ligeramente diferente a otro previo como JSON o YAML.

Pero... ¿y si ya sabemos programar? ¿No podríamos utilizar ese conocimiento para desplegar infraestructura en lugar de aprender un lenguaje nuevo? Si ambas respuestas son afirmativas, nuestra respuesta es [Pulumi](https://www.pulumi.com/).

<!--more-->

## Introducción
Pulumi es una herramienta que nos permite realizar despliegues sobre plataformas de Cloud pública o privada. Aunque el número de proveedores que soporta es mucho menor que Terraform, soporta AWs, Microsoft Azure, GCP junto a Openstack y Kubernetes por lo que cubrirá la mayor parte de nuestas necesidades.

Al igual que Terraform, Pulumi es otra herramienta de infraestructura cómo código y de código abierto. Sin embargo, la principal fortaleza de Pulumi es que si ya tenemos conocimientos previos de programación, podemos usarlos para desplegar dicha infraestructura. Soporta Node.js (Javascript, Typescript o cualquier otro lenguaje compatible), Python3 y Go, aunque si miramos su [documentación](https://pulumi.io/reference/faq.html#how-can-i-add-support-for-my-favorite-language) es posible añadir cualquier lenguaje que queramos.

## Instalación y configuración
La instalación de Pulumi consta de dos partes: una CLI que se encarga de hacer y un interprete para el lenguaje que vayamos a usar. Para instalar la CLI tan sólo deberemos ejecutar el siguiente comando, según la plataforma:

* Linux o MacOS: ```curl -fsSL https://get.pulumi.com | sh```

* Windows: ```powershell @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; iex ((New-Object System.Net.WebClient).DownloadString('https://get.pulumi.com/install.ps1'))" && SET "PATH=%PATH%;%USERPROFILE%\.pulumi\bin"```

Una vez que ya lo tenemos instalado, deberíamos de poder hacer ```pulumi version``` en una terminal y comprobar que nos devuelve ésta. Para este ejemplo, vamos a utilizar Python 3, que es la versión soportada.

Antes de empezar debemos de crearnos una cuenta en la plataforma Cloud de [Pulumi](https://app.pulumi.com), donde se almacenará el estado de nuestros despliegues.

![pulumi-welcome](https://storage.googleapis.com/tangelov-data/images/0022-00.png)

Y crear un Token de acceso en nuestra cuenta: para ello hacemos click en nuestro usuario y dentro de _Access Tokens_ le damos a crear uno nuevo.

![pulumi-config](https://storage.googleapis.com/tangelov-data/images/0022-01.png)

Ahora vamos a iniciar nuestro nuevo proyecto de Python con ```pulumi new azure-python -n basic-azure```. Le indicamos a la CLI que queremos iniciar un nuevo proyecto basado en la plantilla de Azure con python, con el nombre de _basic-azure_, en el _stack_ dev y en el entorno público.

![pulumi-azure-config](https://storage.googleapis.com/tangelov-data/images/0022-02.png)

Se nos habrán generado cuatro ficheros:

* \_\_main\_\_.py : contiene el código por el cual nos vamos a conectar a una cuenta de almacenamiento de Microsoft Azure en una cuenta y en un grupo de recursos concreto.

* _Pulumi.$stackname.yaml_: contiene la configuración propia del stack que hemos configurado en el paso anterior.

* _Pulumi.yaml_: contiene la configuración común a todos los stacks.

* _requirements.txt_: contiene los paquetes necesarios para que Pulumi pueda funcionar con el código que programemos.


## Uso de Pulumi con Microsoft Azure

### Primeros pasos
He decidido que este tutorial se haga con Microsoft Azure, para añadirle un poco más de variedad al blog. Ya [vimos](https://tangelov.me/posts/conectando-gnulinux-con-azure.html) como conectar contra este proveedor desde nuestro PC. Este paso es un prerrequisito necesario para que Pulumi pueda comunicarse con Azure o de lo contrario no funcionará.

Tras realizar la configuración en el paso anterior, veremos que nos indica crear un entorno virtual de python3, activarlo e instalar los requisitos del mismo. Así que vamos a ello:

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Primero vamos a modificar el nombre de algunas variables en \_\_main.py\_\_ para que los nombres del grupo de recursos y de la cuenta de almacenamiento sean personalizados.

```python
import pulumi
from pulumi_azure import core, storage

# Variables to create the core structure in Azure
az_prefix = "az"
az_suffix = "example"
az_location = "westeurope"

# Create an Azure Resource Group
resource_group = core.ResourceGroup(az_prefix + "rg" + az_suffix,
    name=az_prefix+"rg"+az_suffix,
    location=az_location)

# Create an Azure resource (Storage Account)
account = storage.Account(az_prefix + "sa" + az_suffix,
    resource_group_name=resource_group.name,
    location=resource_group.location,
    account_tier='Standard',
    name=az_prefix+"sa"+az_suffix,
    account_replication_type='LRS')

# Export the connection string for the storage account
pulumi.export('connection_string', account.primary_connection_string)
```

Y ahora ejecutamos ```pulumi up```. Nos hará una evaluación previa sobre si nuestra sintaxis es correcta, si incumplimos alguno de los requisitos del proveedor y finalmente nos preguntará si queremos aplicar los cambios. Le decimos que si y seguimos:

![pulumi-up-basic](https://storage.googleapis.com/tangelov-data/images/0022-03.png)

![pulumi-up-basic2](https://storage.googleapis.com/tangelov-data/images/0022-04.png)

### Creación de los elementos de red
Una vez ya tenemos un grupo de recursos donde podemos almacenar los elementos en la nube y una cuenta de almacenamiento, vamos a seguir desplegando elementos. Si nuestra intención es desplegar una máquina virtual, necesitaremos crear una estructura de red acorde con varias subrredes añadiendo el siguiente código:

```python
# Create an Azure Virtual Network
network01 = network.VirtualNetwork(az_prefix + "vn" + az_suffix,
    address_spaces=az_vn_address,
    dns_servers=az_vn_dns,
    location=resource_group.location,
    name=az_prefix+"vn"+az_suffix,
    resource_group_name=resource_group.name)

# Create some Azure VN Subnets
subnet01 = network.Subnet(az_prefix + "sn01" + az_suffix,
    address_prefix=az_vn_address[0],
    virtual_network_name=az_prefix + "vn" + az_suffix,
    resource_group_name=resource_group.name,
    name=az_prefix + "sn01" + az_suffix)


subnet02 = network.Subnet(az_prefix + "sn02" + az_suffix,
    address_prefix=az_vn_address[1],
    virtual_network_name=az_prefix + "vn" + az_suffix,
    resource_group_name=resource_group.name,
    name=az_prefix + "sn02" + az_suffix)


subnet03 = network.Subnet(az_prefix + "sn03" + az_suffix,
    address_prefix=az_vn_address[2],
    virtual_network_name=az_prefix + "vn" + az_suffix,
    resource_group_name=resource_group.name,
    name=az_prefix + "sn03" + az_suffix)
```

Al hacer ```pulumi up``` de nuevo, podremos ver que ya tenemos una estructura de red mínima:

![azure-networking](https://storage.googleapis.com/tangelov-data/images/0022-05.png)

### Desplegando una máquina virtual
Ya tenemos una carcasa básica y usable que podríamos usar para desplegar cualquier tipo de infraestructura. Nuestro siguiente paso es desplegar los recursos necesarios para desplegar una máquina virtual y poder conectarnos a ella. Para conseguirlo necesitamos:

* Un _Network Security Group_ que permita el tráfico SSH a través de internet.
* Una IP pública.
* Una tarjeta de red a la que le podamos asociar una máquina virtual y una IP pública.
* Y por supuesto... una máquina virtual.

Primero vamos a crear todos los recursos de red que nos faltan. Por lo que añadimos el siguiente código al conjunto:

```python
# Creation of Security Groups and rules
basic_nsg = network.NetworkSecurityGroup(az_prefix + "sgbasic" + az_suffix,
    location = resource_group.location,
    resource_group_name=resource_group.name,
    name=az_prefix + "sn03" + az_suffix)

basic_nsg_ssh_in = network.NetworkSecurityRule(az_prefix + "sgbasicssh" + az_suffix,
    access = "Allow",
    description = "Rule to enable SSH from external",
    destination_address_prefix = "*",
    source_address_prefix = "*",
    protocol = "*",
    priority = "500",
    network_security_group_name = basic_nsg.name,
    direction = "Inbound",
    source_port_range = "*",
    destination_port_range = "22",
    resource_group_name=resource_group.name,
    name = az_prefix + "sgbasicssh" + az_suffix)

basic_nsg_ssh_out = network.NetworkSecurityRule(az_prefix + "sgbasicsshout" + az_suffix,
    access = "Allow",
    description = "Rule to enable SSH from external",
    destination_address_prefix = "*",
    source_address_prefix = "*",
    protocol = "*",
    priority = "500",
    network_security_group_name = basic_nsg.name,
    direction = "Outbound",
    source_port_range = "*",
    destination_port_range = "22",
    resource_group_name=resource_group.name,
    name = az_prefix + "sgbasicsshout" + az_suffix)

# Creation of Public IP
public01 = network.PublicIp(az_prefix + "pip01" + az_suffix,
    name = az_prefix + "pip01" + az_suffix,
    ip_version = "IPv4",
    allocation_method = "Static",
    resource_group_name = resource_group.name,
    location = resource_group.location)

```

Con este código ya tendremos una manera de habilitar el tráfico que vaya al puerto 22 y una IP pública a la que conectarnos. Debido a que no tenemos VPNs contra la nube, necesitamos realizar este paso o de lo contrario no podremos acceder a la nube.

Ahora vamos a proceder a crear la tarjeta de red (NIC), asignarle la IP pública y el grupo de seguridad de red, para luego asociarla a nuestra máquina virtual:

```python
# Creating a Network interface in the first subnet
nic_ubuntu01 = network.NetworkInterface(az_prefix + "nic01" + az_suffix,
    ip_configurations = [
        {
            'name': "ubuntu01ipconfig",
            'subnetId': subnet01.id,
            'privateIpAddressAllocation': "Dynamic",
            'publicIpAddressId': public01.id,
        }
    ],
    dns_servers = az_vn_dns,
    network_security_group_id =  basic_nsg.id,
    resource_group_name = resource_group.name,
    location=resource_group.location,
    name = az_prefix + "nic01" + az_suffix)

# Create of one Azure Virtual machine
ubuntu01 = compute.VirtualMachine(az_prefix + "vm01" + az_suffix,
    name=az_prefix + "vm01" + az_suffix,
    vm_size="Standard_B1s",
    location=resource_group.location,
    resource_group_name=resource_group.name,
    network_interface_ids = [ nic_ubuntu01.id ],
    os_profile = {
        'computerName': 'ubuntu01',
        'adminUsername': "pulumi",
        'adminPassword': "pulumipulumi1$",
        },
    os_profile_linux_config = {
        'disablePasswordAuthentication': 'false',
        },
    storage_os_disk = {
        'createOption': "FromImage",
        'name': "ubuntudisk01",
        },
    storage_image_reference = {
        'publisher': "canonical",
        'offer': "UbuntuServer",
        'sku': "18.04-LTS",
        'version': "latest",
        }
)
```

Podemos ver el conjunto del código [aquí](https://gitlab.com/tangelov/proyectos/blob/cf2b12dedbac6f6f1987483c33cfd9fe2b62ca73/templates/pulumi/basic-azure/__main__.py).


## Dependencias y despliegues "complejos"
Si juntamos todo el código que hemos ido creando e intentamos desplegarlo todo junto desde cero, el despliegue fallaría: algunas subredes intentarían crearse al mismo tiempo que la red a que pertenecen y la creación de la máquina virtual y de su tarjeta de red tendrían el mismo problema. 

Para evitarlo, debemos coger nuestro código y añadirle un orden lógico a la creación de los elementos. En resumen: debemos indicarle a Pulumi qué dependencias tiene cada recurso y lo que tiene que crear antes de ponerse con otro. En nuestro código casi todos los elementos tienen algunas variables o IDs que los relacionan entre si. En este caso:

* Todos los elementos se encuentran dentro de un grupo de recursos. Esta dependencia es gestionada de forma automática por Pulumi, es implícita y no necesitamos especificarla aunque podríamos hacerlo.
* Nuestas subredes pertenecen todas ellas a una única red virtual.
* Nuestra tarjeta de red (NIC) requiere del identificado de una subred y de una IP pública para crearse.

Las dependencias se definen con una serie de opciones (opts) en cada recurso. Por ejemplo el siguiente código añadiría dos dependencias a la creación de nuestra tarjeta de red:

```python
# Creating a Network interface in the first subnet
nic_ubuntu01 = network.NetworkInterface(az_prefix + "nic01" + az_suffix,
    name = az_prefix + "nic01" + az_suffix,
    resource_group_name = resource_group.name,
    opts = pulumi.ResourceOptions(depends_on = [subnet01, public01]),
    ip_configurations = [
        {
            'name': "ubuntu01ipconfig",
            'subnetId': subnet01.id,
            'privateIpAddressAllocation': "Dynamic",
            'publicIpAddressId': public01.id,
        }
    ],
    dns_servers = az_vn_dns,
    network_security_group_id =  basic_nsg.id,
    location=resource_group.location)
```

Una vez hemos puesto todas las dependencias necesarias, nuestro código quedaría [así](https://gitlab.com/tangelov/proyectos/blob/4922da919f3f64e647032f09976738a4a5603d30/templates/pulumi/basic-azure/__main__.py) y podríamos realizar un despliegue tal y cómo se ve en el gif siguiente:

![pulumi-full](https://storage.googleapis.com/tangelov-data/images/0022-06.gif)

> __Nota del Autor__: Cuando se escribió este post, Pulumi estaba en su versión 1.0. Es posible que a medida que evolucione el desarrollo de la versión 2.0 que ha sido anunciada en noviembre, el código deje de ser compatible.


## Diferencias con Terraform
Cuando un compañero me recomendó esta solución me llamó mucho la atención, puesto que uno de los problemas actuales de Terraform es la falta de unos condicionales y bucles decentes (aunque están en ello). Los condicionales y los bucles causan problemas en los lenguajes declarativos y me daba curiosidad cómo solucionaba eso Pulumi. Lo que me he encontrado es una gran herramienta que está literalmente construida sobre Terraform. Sin embargo, hay diferencias importantes entre ellas:

Primero vamos a lo bueno de Pulumi:

* Pulumi permite utilizar Go, Python3 o Javascript, no necesitas aprender un lenguaje propio. Esto puede ahorrar tiempo y acercar a los desarrolladores más puros hacia la infraestructura. Al soportar bucles y condicionales de forma completa podríamos por ejemplo generar una estructura de red que generase unas reglas de firewall y rutas diferentes en función del nombre que tuviera una subred, crear y asignar IPs públicas en las que consideremos como públicas, etc. He hecho algunas pruebas con bucles [aquí](https://gitlab.com/tangelov/proyectos/blob/b4342e026e830498cf2393c5b213d4d241492c50/templates/pulumi/basic-azure/__main__.py), pero querría profundizar más usando herencias y creando clases propias.

* Ofrecen un "Pulumi Cloud" permite ofrecer una capa de abstracción encima de los principales proveedores de cloud pública, haciendo que dicho código sea portable sin tener que cambiarlo en función del proveedor (en estos momentos sólo funciona con AWS)

* Pulumi soporta gestión de secretos de forma nativa.

* Ofrecen un seguimiento a los cambios que se realizan en la infraestructura de forma nativa dentro de su plataforma:

![trazabilidad-pulumi](https://storage.googleapis.com/tangelov-data/images/0022-07.gif)

Ahora vamos a lo no tan bueno:

* Me he encontrado con algunas inconsistencias en el tiempo que he estado probando y preparando este post. Por ejemplo, me he encontrado con que algunas dependencias implícitas en Terraform, era necesario declararlas. También me pasó que algunas subredes fallaban en la creación de forma aleatoria y temporal. No estoy seguro de si pudo ser algunos problemas puntuales con la API de Azure o de la herramienta.

* Para usar Pulumi tienes que saber algún lenguaje de programación. Si alguien no sabe dicho lenguaje no podrá entender el código (aunque no me parece difícil... ¡y tiene bucles en condiciones!)

* Pulumi no permite importar recursos ya creados. Esto limita mucho el evolucionar una infraestructura ya creada y te fuerza a comenzar a utilizar proyectos nuevos o a dejar la infraestructura previa fuera del código de Pulumi. Aunque existe [una herramienta](https://github.com/pulumi/tf2pulumi) para ello, he visto que tiene limitaciones importantes.

* Pulumi no facilita que se pueda usar guardar el estado de tu infraestructura fuera de su nube. Aunque en teoría es posible según su documentación, entiendo perfectamente que se quieran guardar duplicados del estado de la infraestructura (lo que en Terraform sería duplicar los archivos de estado o _tfstates_)


Y eso es todo por hoy. Me he retrasado un poco con este post por motivos personales, pero espero que guste. Un saludo y gracias.


## Documentación

* [Hashicorp Configuration Language (ENG)](https://github.com/hashicorp/hcl)

* [Página oficial de Pulumi (ENG)](https://www.pulumi.com/docs/index.html)

* [Conceptos básicos de Pulumi (ENG)](https://www.pulumi.com/docs/intro/concepts/)

* [Configuración de Python en Pulumi (ENG)](https://www.pulumi.com/docs/intro/languages/python/)

* [API Reference de Python3 en Pulumi para Azure (ENG)](https://www.pulumi.com/registry/packages/azure-native/api-docs/)

* [Pulumi as Infraestructure as Code software (ENG)](https://medium.com/hara-engineering/pulumi-as-infrastructure-as-code-software-720d62987e9f).

Revisado a 01/04/2023
