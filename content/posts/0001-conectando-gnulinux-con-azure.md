---
title: "Conectando GNU/Linux con Azure"
slug: conectando-gnulinux-con-azure
authors:
  - tangelov
date: 2018-02-18T09:30:00+02:00
tags:  ["azure", "cloud"]
categories: ["cloud"]
draft: false
---

Hace tiempo el mundo Linux y el mundo Windows estaban prácticamente separados. Las prácticas habituales de Microsoft de usar estándares propios ajenos al resto de la industria provocaban muchos recelos y quejas dentro de la comunidad.

Sin embargo, aunque siga provocando recelos, los tiempos han cambiado y a día de hoy es posible trabajar desde/con Linux sobre una gran parte de los productos y servicios de Microsoft. Por citar algunos ejemplos:

* SQL Server o .NET se encuentran disponibles para entornos Linux.

* Powershell y .NET son ahora plataformas de código abierto.

* Microsoft ha empezado a contribuir al código del kernel de Linux.

* La nube de microsoft, Azure, contiene miles de máquinas virtuales ejecutando Linux.

Con el mundo _cloud_ pegando cada vez más fuerte y siendo Microsoft uno de los principales proveedores de nube pública del mundo, en este pequeño tutorial vamos a mostrar cómo conectar nuestra máquina Linux contra Azure para poder hacer despliegues, backups, etc.

<!--more-->

## Azure CLI
En primer lugar, debemos conectar la CLI de Azure, para gestionar la mayoría de servicios de la nube. Prefiero usar la CLI de Azure en lugar de Powershell por su portabilidad entre sistemas.

```bash
# Añadimos el repositorio de Azure-CLI para sistemas Debian o Ubuntu (El ejemplo está basado en Ubuntu 21.04)
echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ jammy main" | \
    sudo tee /etc/apt/sources.list.d/azure-cli.list

# Añadimos la clave GPG del repositorio e instalamos la CLI
curl -L https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

sudo apt-get install apt-transport-https
sudo apt-get update && sudo apt-get install azure-cli
```

Para ejecutar la CLI tan sólo tenemos que usar el comando __az__

### Configuración
Ya tenemos nuestro PC preparado para conectarse a Azure sin usar el portal, pero necesitamos autenticarnos ante Azure para poder trabajar.

```bash
# Primer ejecutamos az configure para deshabilitar la telemetría. También podemos ejecutar el formato de la salida y el log donde se guarde el histórico.
az configure

# Ahora vamos a proceder a loguearnos en nuestra cuenta de Azure
az login
```

Nos mostrará un mensaje como el siguiente

```bash
A web browser has been opened at https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize. Please continue the login in the web browser. If no web browser is available or if the web browser fails to open, use device code flow with `az login --use-device-code`.
```

Deberemos abrir el navegador, introducir nuestro usuario y contraseña y listo. Ya estaremos autenticados con nuestra cuenta dentro de Azure.

Si nuestro servidor no tiene interfaz gráfica o navegador web, podemos utiliza el comando ```bash az login --use-device-code```:

![Autenticación en Microsoft Azure](https://storage.googleapis.com/tangelov-data/images/0001-00.png)

Por ejemplo este comando nos mostrará todas las subscripciones de Azure a las que tenemos acceso y nos indicará cual es la seleccionada por defecto.

```bash
# Explicación del comando:
# az account list nos lista todas las subscripciones con todos sus datos
# --query [*].[name,state,isDefault] filtra sólo los campos que deseamos
# --out table nos muestra el resultado en formato tabla.

az account list --query "[*].[name,state,isDefault]" --out table
```

![az account list](https://storage.googleapis.com/tangelov-data/images/0001-01.png)


Nuestra configuración se encuentra en una carpeta dentro de nuestro $HOME llamada _.azure_:

```bash
/home/tangelov/.azure
├── accessTokens.json
├── az.json
├── az.sess
├── azureProfile.json
├── clouds.config
├── commands
├── config
├── logs
│   └── telemetry.log
├── telemetry
└── telemetry.txt
```

## AzCopy
Otro programa de gran utilidad para trabajar con almacenamiento de Azure es _AzCopy_ por lo que vamos a proceder también a su instalación.

> En versiones anteriores (anteriores a la 3.X), AzCopy necesitaba la instalación de .NET Core para su funcionamiento. Para las versiones actuales no es necesaria, pero si fuese necesario podemos hacerlo [aquí](https://learn.microsoft.com/es-es/dotnet/core/install/linux-ubuntu#2204). Los instaladores soportan RHEL, Ubuntu, Debian, Fedora y Opensuse entre otros.

AzCopy es en la actualidad un binario que tan sólo tenemos que descargar:

```bash
# Descargamos e instalamos azcopy
wget -O azcopy.tar.gz https://aka.ms/downloadazcopy-v10-linux
tar -xf azcopy.tar.gz

# Movemos el ejecutable a una carpeta dentro del PATH
cd azcopy_linux_*
mv azcopy $HOME/.local/bin/azcopy

# Limpiamos la instalación
cd ..
rm azcopy.tar.gz
rm -rf azcopy_linux_*
```


## Documentación:

* [Install Azure CLI 2.0 (ENG)](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
* [Transfer data with AzCopy on Linux (ENG)](https://docs.microsoft.com/en-gb/azure/storage/common/storage-use-azcopy-v10)
* [Installation .NET Core on Linux (ENG)](https://docs.microsoft.com/es-es/dotnet/core/install/linux-package-manager-ubuntu-1904)

Revisado a 01/01/2023.
