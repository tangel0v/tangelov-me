---
title: "Gestión de certificados con cfssl"
slug: cfssl
authors:
  - tangelov
date: 2024-04-30T05:00:00+02:00
tags:  ["devops", "certificates", "cloud"]
categories: ["devops"]
draft: false
---

La seguridad es un pilar fundamental a la hora de gestionar infraestructura con organización y resiliencia, aunque a veces los proyectos se olvidan un poco de ella dependiendo del presupuesto y del tiempo disponible en el equipo.

A la hora de seguir una mínima política de seguridad, uno de sus pilares fundamentales es el cifrado de datos. Éste protege los datos generados por nuestra aplicación de forma segura: asegura la confidencialidad de datos en tránsito entre el usuario y la aplicación y los datos almacenados de accesos no autorizados.

Existen múltiples formas de cifrar información, pero la mayoría de ellas están basadas en algún sistema de intercambio de claves, que cifran y descifran el contenido según la necesidad. Si la información está almacenada, decimos que está _en reposo_ (en un disco duro) y si está siendo enviada a un destino, decimos que está _en tránsito_.

En este post, vamos a centrarnos en el cifrado en tŕansito, el que permite conectarnos a una página web de forma segura y cuyas _claves_ son llamadas comúnmente _certificados_.

Estos certificados tienen dos funciones: primero, garantizan que la comunicación entre usuario y servidor sea segura y segundo, identifican al servidor o a la aplicación frente al usuario, como si de un documento de identidad se tratase.

Al igual que en la vida real, ¿Qué pasa si nos roban esta identificación? Podrían crear un servidor trucado para robar información, dinero o cualquier dato vital y generarnos un daño reputacional enorme.

Para reducir la exposición ante estos problemas y garantizar que _uno es quien dice ser_, los certificados públicos tienen una duración de uno o dos años y después son rotados, pero si reducimos esta ventana de tiempo, también reducimos el tiempo que nuestra identidad puede ser suplantada.

El momento de rotación de un certificado es siempre crítico. Si no se ejecuta de forma correcta, puedes dejar sin acceso a los usuarios de sus aplicaciones favoritas, cortar un servicio de VPN o dejar sin acceso a la WiFi a una compañía completa. Por todo ello, me alegro de que existan herramientas tan potentes como __cfssl__.


## Introducción: cómo funcionan los certificados
Antes de entrar en detalle, vamos a repasar el funcionamiento básico de los certificados para que cualquier lector pueda entender el resto del contenido del post de una forma sencilla.

Cada certificado es parte de una cadena de confianza emitida por una _entidad certificadora_. Esta entidad es un ente que verifica y garantiza que eres quien dices ser. Si es pública, se encuentra preinstalada en todos nuestros ordenadores y navegadores por defecto.

Podríamos decir que cada certificado consta de dos partes:
- Una parte pública, que verifica la identidad (el dominio y el propietario) y que es utilizada para iniciar la comunicación segura.
- Una parte privada, a la cual sólo tiene acceso el propietario de la identidad (usualmente el servidor) y que le permite, a grosso modo, descifrar los datos.

El proceso de comunicación a través de TLS es el siguiente:

![how-certificates-work](https://storage.googleapis.com/tangelov-data/images/0056-00.png)

0. Antes de iniciar la comunicación, el certificado raíz de la CA tiene que estar desplegado en nuestros servidores y navegadores y nuestro certificado y su llave tienen que estar instalados en el destino, así cómo estar firmados con la llave privada de la CA (garantizando así su autenticidad).

1. El cliente le comunica al servidor que desea comenzar a utilizar una comunicación cifrada utilizando TLS.

2. El servidor le devuelve su certificado y la clave pública.

3. El cliente comprueba la veracidad del certificado y su cadena de confianza (basándose 
en la CA) y crea una clave simétrica cifrada basándose en la información recibida.

4. El servidor descifra la clave y la utiliza para intercambiar información de forma segura con el cliente.

5. Gracias al uso de estas claves simétricas, la conexión deja de viajar en texto plano y sólo el cliente y el servidor pueden conocer su contenido.

> Los sistemas de cifrado más comunes utilizan claves simétricas o asimétricas. En el primer caso, sólo utilizamos una clave para cifrar y descifrar la información, mientras que en el segundo, sólo quien posea la llave pública puede hacerlo.

Pese a que este modelo existe desde mediados de los noventa, no era muy usado hasta hace poco. A principios de 2017, sólo el 50% del tráfico total de Internet estaba cifrado. Detrás de esta lenta adopción, estaba su coste: inicialmente, necesitábamos que cada dominio tuviera su propio certificado y pagar por él a las entidades certificadoras. Esto lo hacía prohibitivo para cualquier página web que fuese muy pequeña o que no generase ingresos. 

Gracias a iniciativas como Let's Encrypt, realizada por la EFF(_Electronic Frontier Foundation_), que permitía crear certificados sin coste alguno y a la utilización de SaaS o de los proveedores de nube pública (que permiten tener certificados con mucho menos coste), hoy la inmensa mayoría de páginas web son accesibles a través de HTTPS.


## Creación de una CA y un certificado paso a paso
Hasta este momento, siempre hemos hablado sobre el funcionamiento de cualquier página web que sea accesible a través de Internet. Sin embargo, si nuestra página web es privada y no es accesible a través de Internet, siempre podemos utilizar lo que llamamos una CA privada.

En teoría, no hay una gran diferencia entre una CA privada y una pública: ambas permiten generar certificados y garantizar que cierta página es quien dice ser, pero en la práctica, nos vamos a encontrar con grandes limitaciones.

Cuando utilizamos una CA privada, nadie sabe quienes somos, ni si somos de confianza y nadie va a confiar por defecto en ninguno de nuestros certificados. Nuestro certificado raíz no está preinstalado en ningún servidor o navegador y cualquier comunicación que iniciemos, va a comenzar con un símbolo de advertencia en nuestro navegador.

![browser-warning](https://storage.googleapis.com/tangelov-data/images/0056-01.png)


> Esto es algo conocido para cualquier lector que viva en España, puesto que parte de la administración pública utiliza certificados emitidos por la Fábrica Nacional de Moneda y Timbre y su certificado raíz no era reconocido como válido hasta hace poco, obligándonos a verificarlo de forma manual.


Ahora vamos a ver el proceso para crear de forma manual una entidad certificadora privada y un certificado utilizando _openssl_ (suele estar instalado por defecto en la mayoría de distribuciones Linux). El proceso es el siguiente:

![ca-certificate-process](https://storage.googleapis.com/tangelov-data/images/0056-02.png)

Primero tenemos que generar una llave privada para nuestra CA. Para hacerlo tan sólo tenemos que indicarle el tamaño en bits de la clave y después, crear el certificado raíz de nuestra CA:

```bash
# Generamos la llave privada de nuestra CA
openssl genrsa -out ca.key 4096

# Ahora utilizamos dicha llave para generar el certificado raíz de nuestra CA
openssl req -x509 -sha256 -nodes -extensions v3_ca -key ca.key -subj "/C=ES/ST=Madrid/O=Tangelov/CN=tangelov.local" -days 1825 -out ca.crt
```

Una vez que tenemos nuestro CA raíz, podemos utilizarla para crear una _"subCA"_ también llamada, _CA intermedia_. No es obligatoria, pero aporta más seguridad al conjunto. Si la llave privada de un certificado cae en malas manos, siempre podemos revocar el certificado utilizando la CA, pero si la CA es quien ha sido robada, no tenemos forma de notificar directamente a los usuarios afectados.

Si utilizamos una CA intermedia, podemos utilizar la CA raíz para revocarla y que automáticamente toda la cadena deje de ser válida.

> Es habitual que la CA raíz esté a buen recaudo, en algún sistema de almacenamiento desconectado de Internet y que sólo se conecte para renovar la CA Intermedia.

Para crear nuestra CA intermedia, seguimos un proceso ligeramente diferente: creamos una llave privada y un CSR ([Certificate Signing Request](https://es.wikipedia.org/wiki/Certificate_Signing_Request)). Este CSR es un mensaje que enviamos a la CA para que verifique que la CA es correcta y verifique su identidad. Para poder ejecutarlo, tenemos que tener acceso a las claves pública y privada de la CA raíz:

```bash
# Generamos una nueva clave privada con 4096 bits de longitud
openssl genrsa -out ca_intermediate.key 4096

# Generamos con esta nueva clave privada un CSR
openssl req -new -sha256 -nodes -key ca_intermediate.key -subj "/C=ES/ST=Madrid/O=Tangelov/CN=intermediate.tangelov.local" -out intermediate.csr

# Una vez tenemos nuestro CSR, verificamos su autenticidad con la CA raíz y su clave privada y generamos el certificado de la CA intermedia.
openssl x509 -req -extensions v3_ca -in intermediate.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out ca_intermediate.crt -days 730 -sha256 -extfile /etc/ssl/openssl.cnf
```

Por último, vamos a crear un certificado para un servidor bajo un dominio que se llame _debug.tangelov.local_. El procedimiento es muy similar al de crear una CA intermedia: creamos la llave privada, con ella creamos el CSR y por último creamos el certificado. Esta vez utilizamos la clave privada de la CA intermedia para firmarlo.

```bash
# Generamos la clave privada de nuestro certificado
openssl genrsa -out debug.key 4096

# Generamos un nuevo CSR para nuestro certificado
openssl req -new -sha256 -nodes -key debug.key -subj "/C=ES/ST=Madrid/O=Tangelov/CN=debug.tangelov.local" -out debug.csr

# Generamos el certificado, firmando dicho certificado con las claves de la CA Intermedia
openssl x509 -req -in debug.csr -CA ca_intermediate.crt -CAkey ca_intermediate.key -CAcreateserial -out debug.crt -days 365 -sha256
```

Recibiremos un mensaje similar a éste:

```bash
Certificate request self-signature ok
subject=C = ES, ST = Madrid, O = Tangelov, CN = debug.tangelov.local
```

Ahora podemos verificar toda la cadena de confianza de los certificados con los siguientes comandos:

```bash
# Verificamos que la CA raíz es capaz de validar a la CA intermedia
openssl verify -CAfile ca.crt ca_intermediate.crt
ca_intermediate.crt: OK

# Verificamos que la CA intermedia es capaz de validar el certificado final. Tenemos que indicarle que la cadena no es completa para que no de error
openssl verify -CAfile ca_intermediate.crt debug.crt
C = ES, ST = Madrid, O = Tangelov, CN = intermediate.tangelov.local
error 2 at 1 depth lookup: unable to get issuer certificate
error debug.crt: verification failed

openssl verify -CAfile ca_intermediate.crt -partial_chain debug.crt
debug.crt: OK

# También podemos verificar el certificado final utilizando ambas CAs de forma encadenada
openssl verify -CAfile <(cat ca.crt ca_intermediate.crt) debug.crt  
debug.crt: OK
```

## CFSSL
Como podemos ver, la creación de una CA y sus certificados es un proceso bastante artesanal, así que para simplificar el proceso, la gente de CloudFlare desarrolló en Go una herramienta llamada _cfssl_. Según sus propias palabras es _la navaja suiza de la creación de certificados_ y permite firmar, verificar y empaquetar cualquier certificado TLS ya sea a través de su CLI o de su API web.

Llevo unos meses haciendo pruebas en local con Nomad, un orquestador de aplicaciones desarrollado por Hashicorp y como quiero utilizarlo de forma segura, necesito utilizar certificados, aunque sea un servicio privado.

Nomad puede crear certificados utilizando una herramienta propia, pero sus funcionalidades son bastante limitadas y no se ajustan a lo que necesitaba. Frustrado con el proceso de securización descubrí _cfssl_ y fue un flechazo instantáneo (en parte gracias a Mike Polinowski, que utiliza un setup similar.)

CFSSL son un conjunto de herramientas que permiten gestionar la creación y el rotado de CAs y certificados utilizando plantillas, pero antes de nada, debemos instalarlo. Para este tutorial en concreto, necesitamos instalar _cfssl_ y _cfssljson_:

```bash
# Primero descargamos el binario de cfssljson
curl -L  https://github.com/cloudflare/cfssl/releases/download/v1.6.5/cfssljson_1.6.5_linux_amd64 -o cfssljson
chmod +x cfssljson

# Después descargamos el binario de cfssl
curl -L https://github.com/cloudflare/cfssl/releases/download/v1.6.5/cfssl_1.6.5_linux_amd64 -o cfssl
chmod +x cfssl
```

Una vez tenemos los programas en nuestro ordenador, necesitamos crear un fichero de configuración en formato JSON como el siguiente:

```json
{
  "signing": {
    "default": {
      "expiry": "8760h"
    },
    "profiles": {
      "intermediate_ca": {
        "usages": [
          "signing",
          "digital signature",
          "key encipherment",
          "cert sign",
          "crl sign",
          "server auth",
          "client auth"
        ],
        "expiry": "8760h",
        "ca_constraint": {
          "is_ca": true,
          "max_path_len": 0, 
          "max_path_len_zero": true
        }
      },
      "peer": {
        "usages": [
          "signing",
          "digital signature",
          "key encipherment", 
          "client auth",
          "server auth"
        ],
        "expiry": "8760h"
      },
      "server": {
        "usages": [
          "signing",
          "digital signing",
          "key encipherment",
          "server auth"
        ],
        "expiry": "8760h"
      },
      "client": {
        "usages": [
          "signing",
          "digital signature",
          "key encipherment", 
          "client auth"
        ],
        "expiry": "8760h"
      }
    }
  }
}
```

En este fichero estamos definiendo una serie de perfiles que después podremos seleccionar para crear distintos tipos de certificados o CAs:
- Primero definimos la parte de firmado de cada certificado y le asignamos un valor por defecto. En este caso son 8760 horas, o lo que es lo mismo, 365 días.
- Después definimos perfiles, en función del tipo de certificado que queramos crear:
  - _intermediate\_ca_: lo utilizaremos para crear nuestra CA Intermedia y le indicamos todos los usos que puede tener el certificado (firmar, cifrar y autenticar tanto servidores como clientes), el tiempo de validez y si es una CA.
  - También creamos los perfiles _peer_, _server_ y _cliente_, con distintos propósitos y donde la parte de CA ha desaparecido por completo.

Para este pequeño ejercicio vamos a asumir que todos los ficheros utilizados por cfssl se encuentran en la misma carpeta. Tenedlo en cuenta a la hora de replicarlo en vuestros PCs.

Tras crear el fichero de configuración general, ahora vamos a crear nuevas plantillas, una para nuestra CA, otra para la CA intermedia y otra para el certificado que queramos crear:

```bash
{
  "CN": "sec.private-cluster.local",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": 
  [
    {
      "C": "ES",
      "L": "Madriz",
      "O": "Automation",
      "OU": "Automation",
      "ST": "Spain"
    }
  ]
}
```

En este primera plantilla definimos el nombre completo que queramos que tenga la CA raíz de nuestra cadena de confianza (en este caso _sec.private-cluster.local_), que su clave tenga una longitud de 2048 bits y su localización a nivel geográfico y organizativo.

Ahora ejecutamos el siguiente comando y tendremos nuestra CA:

```bash
# Si nuestro fichero es ca.json y el fichero de configuración es cfssl.json (tiene que estar en la misma carpeta), ejecutamos el siguiente comando:
cfssl gencert -initca ca.json | cfssljson -bare ca

# Recibiremos un mensaje similar a este:
2024/04/28 22:21:51 [INFO] generating a new CA key and certificate from CSR
2024/04/28 22:21:51 [INFO] generate received request
2024/04/28 22:21:51 [INFO] received CSR
2024/04/28 22:21:51 [INFO] generating key: rsa-2048
2024/04/28 22:21:52 [INFO] encoded CSR
2024/04/28 22:21:52 [INFO] signed certificate with serial number 262383398683474357910768963128213764652725417965
```

Una vez tenemos nuestra Root CA, podemos crear nuestra CA intermedia:

```json
{
  "CN": "int.private-cluster.local",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names":
  [
    {
      "C": "ES",
      "L": "Madriz",
      "O": "Automation",
      "OU": "Automation",
      "ST": "Spain"
    }
  ],
  "ca": {
    "expiry": "42720h"
  }
}
```

En la segunda plantilla, hemos cambiado el nombre del dominio y la política de caducidad de la CA para que dure unos 180 días. Al igual que utilizando openssl, necesitamos crear nuestra nueva CA intermedia y firmarla con la clave privada de la Root CA:

```bash
# Si nuestro fichero es intermediate.json y el fichero de configuración es cfssl.json (tiene que estar en la misma carpeta), ejecutamos los siguientes comandos:

# Para crear la CA
cfssl gencert -initca intermediate.json | cfssljson -bare intermediate

# Recibiremos un mensaje similar a este:
2024/04/28 22:35:25 [INFO] generating a new CA key and certificate from CSR
2024/04/28 22:35:25 [INFO] generate received request
2024/04/28 22:35:25 [INFO] received CSR
2024/04/28 22:35:25 [INFO] generating key: rsa-2048
2024/04/28 22:35:25 [INFO] encoded CSR
2024/04/28 22:35:25 [INFO] signed certificate with serial number 128526431067155544000865004664616427874639242518

# Para firmar la CA intermedia con la clave privada de la CA raíz. También le tenemos que indicar que perfil queremos utilizar, cómo es una CA Intermedia, elegimos intermediate_ca
cfssl sign -ca ca.pem -ca-key ca-key.pem -config cfssl.json -profile intermediate_ca intermediate.csr | cfssljson -bare intermediate 

2024/04/28 22:39:16 [INFO] signed certificate with serial number 526840889642145822774673652922863459744150772000
```

Por último, creamos nuestro nuevo certificado con otra plantilla:

```json
{
  "CN": "secret.private-cluster.local",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "ES",
      "L": "Madriz",
      "O": "Automation",
      "OU": "Automation",
      "ST": "Spain"
    }
  ],
  "hosts": [
    "secret.private-cluster.local",
    "www.secret.private-cluster.local"
  ]
}
```

Aquí le indicamos el nombre principal y los nombres secundarios que queremos que proteger con nuestro certificado. Para generarlo tan sólo tenemos que invocar cfssl junto con la CA intermedia que acabamos de crear:

```bash
# Guardamos la plantilla anterior con el nombre cert.json
cfssl gencert -ca intermediate.pem -ca-key intermediate-key.pem -config cfssl.json -profile=peer cert.json | cfssljson -bare cert

2024/04/28 23:07:06 [INFO] generate received request
2024/04/28 23:07:06 [INFO] received CSR
2024/04/28 23:07:06 [INFO] generating key: rsa-2048
2024/04/28 23:07:06 [INFO] encoded CSR
2024/04/28 23:07:06 [INFO] signed certificate with serial number 178224846067269839327717829569034074777118157823
```

Y si hemos realizado todos los pasos correctamente, tendremos una carpeta con todos nuestros certificados y que podemos validar igual que si estuviesen creados con openssl:

```
openssl verify -CAfile ca.pem intermediate.pem 
intermediate.pem: OK

openssl verify -CAfile intermediate.pem -partial_chain cert.pem
cert.pem: OK

openssl verify -CAfile <(cat ca.pem intermediate.pem) cert.pem
cert.pem: OK
```


## Mi opinión personal
Actualmente me encuentro en un proceso de modernización de todo el stack que utilizo en casa, basado en Nomad, Consul y otras herramientas del stack de Hashicorp. Cuando introduzco nuevas herramientas, siempre mido si éstas merecen la pena, puesto que son nuevas herramientas que aprender y que añaden complejidad al conjunto.

En medio de todo este _caos_, el descubrimiento de _cfssl_ ha sido un hallazgo tremendo. Utilizar Nomad y Consul de forma segura estaba siendo un pequeño dolor de cabeza y _cfssl_ me ha permitido simplificar toda la gestión y rotado de certificados a un nivel que apenas añade carga de trabajo extra.

A día de hoy, con sólo habilitar una o varias flags puedo renovar, una parte de la cadena de CAs, o todos los certificados al completo, de forma transparente y sin esfuerzo, gracias a la integración que he hecho con Ansible. Si alguien está interesado, [aquí](https://gitlab.com/tangelov/configuration/-/raw/main/playbooks/cert-rotation.yml) puede acceder al playbook que utilizo.

Tras unos meses utilizándolo, estoy encantado y aunque sólo utilizo una pequeña parte de su stack, recomiendo su uso para cualquier entorno de desarrollo personal y también para gente que quiera tener comunicaciones cifradas sin que sean necesariamente públicas (para no utilizar Let's Encrypt).

Sin mucho más que decir al respecto, espero que este post os haya resultado interesante y nada, nos vemos pronto. ¡Un saludo!



## Documentación

* [Página web oficial de la Electronic Frontier Foundation (ENG)](https://www.eff.org/es)

* [Página web oficial de CF SSL Toolkit (ENG)](https://cfssl.org/)

* [Repositorio oficial de CFSSL en Github (ENG)](https://github.com/cloudflare/cfssl)

* [Addig Nomad Encryption by Mike Polinowski (ENG)](https://mpolinowski.github.io/docs/DevOps/Hashicorp/2022-05-18-hashicorp-dojo-nomad-adding-encryption/2022-05-18/)

- Como importar CAs y certificados en [Chrome](https://www.adslzone.net/como-se-hace/chrome/certificado-digital-google-chrome/) y [Firefox](https://www.adslzone.net/como-se-hace/firefox/instalar-certificados/)

- Como importar CAs en el sistema operativo: [Windows](https://knowledge.digicert.com/solution/how-to-import-intermediate-and-root-certificates-using-mmc), [Mac](https://blog.1byte.com/guide/how-to-import-export-certificates-on-mac-os-via-keychain/) y [Linux](https://www.baeldung.com/linux/ca-certificate-management) (ENG)

Revisado a 30-04-2024
