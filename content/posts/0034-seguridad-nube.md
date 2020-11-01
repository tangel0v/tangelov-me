---
title: "Contraseñas y nube pública: una necesidad real"
authors:
  - tangelov
date: 2020-08-07T20:00:00+02:00
tags:  ["security"]
categories: ["cloud"]
draft: false
---

La digitalización de la sociedad es un proceso que ha aumentado tanto el consumo de servicios web como los ataques informáticos contra sus usuarios y los propios servicios. A mediados de 2020, alguien accedió a las herramientas de gestión internas de Twitter y pudo publicar mensajes en cuentas verificadas de gente famosa para que le enviaran Bitcoins. El ataque era un robo, pero las consecuencias del ataque podían haber sido mucho más graves.

¿Os imaginais que se hubiera publicado amenazas de muerte desde la cuenta de un presidente de un Estado hacia otro presidente? ¿O si desde la cuenta de un gran empresario se diese información errónea para manipular la Bolsa de un país?

Evidentemente, nosotros como usuarios no tenemos tanto poder, pero si alguien accediese a nuestras cuentas de AWS o GCP, podríamos tener problemas o _gastos indeseados_.

<!--more-->

## Introducción
Siempre he estado bastante concienciado sobre la necesidad de utilizar los ordenadores de forma segura. Sufrí en mi juventud el gusano Sasser y tuve que borrar alguna cuenta de correo por las toneladas de SPAM que acabó recibiendo.

El aumento de ataques informáticos ha hecho que la seguridad informática haya mejorando a la par. A día de hoy, cualquier organización _seria_ tiene mecanismos de vigilancia y defensa para que vulnerar sus sistemas sea algo más difícil. Sin embargo, como los bugs siempre van a existir, éste no es un problema que vaya a desaparecer.

Existe una tendencia clara en la industria: se deben cifrar todos los datos (en tránsito y en reposo), utilizar políticas de contraseñas para garantizar una calidad mínima de las mismas y que se cambien periódicamente. Las grnades empresas de Internet como Google, Amazon o Facebook se toman muy en serio todas estas cuestiones.

Hay un vector que es más difícil de proteger: el usuario. Una seguridad técnica muy potente puede no servir para nada si luego un administrador cae en un ataque de ingeniería social y un intruso logra acceder a sus cuentas. 

La ingeniería social es una técnica que se basa en estudiar a los usuarios de un servicio (_administradores_ o no) para diseñar ataques explícitamente contra ellos. Por ejemplo, pueden utilizar _phishing_ para robar las credenciales de su cuenta personal y probar dicha contraseña en cuentas profesionales u obtener datos personales (nombre de su pareja, año de nacimiento, etc) para crear diccionarios y ver si acceden con ellos.


## Autenticación en dos pasos
Debido a estos problemas, el modelo de seguridad ha evolucionado. A día de hoy, se considera que las contraseñas no son por si solas un método fiable para securizar un servicio. Para ello es necesario utilizar la llamada _autenticación en dos pasos_ (2FA).

La autenticación en dos pasos consiste en identificar a un usuario a través de dos preguntas: la primera pregunta se basa en algo que _sabes_, como un usuario y una contraseña y la segunda, en algo que _tienes_.

No es un método muy novedoso, pero funciona. Hace años que muchas cuentas bancarias requieren introducir datos extra como un SMS en nuestro móvil o introducir una contraseña extra.

La implementación 2FA más conocida es el uso de códigos de un sólo uso o _TOTP_. Este tipo de autenticación generan claves aprovechando el momento justo de la petición para generar un código de un sólo uso. Existen muchas formas de generar este tipo de códigos, desde gestores de contraseñas para PC como Keepass o aplicaciones para teléfonos móviles como Google Authenticator, FreeOTP, etc.

Quizás la implementación más conocida sea el uso de códigos de un solo uso (TOTP). Las autenticaciones mediante TOTP utilizan el tiempo del momento de la petición para generar un código de un sólo uso. Podemos generarlos con gestores de contraseñas como Keepass o con generadores como Google Authenticator, FreeOTP, etc.

Sin embargo, el sistema 2FA que más me gusta son las llaves o tokens hardware.


### Yubico y Yubikey
Yubico es una empresa sueco-estadounidense que desarrolla llaves hardware y que podemos utilizar como el segundo factor de la autenticación de un servicio. Su nombre comercial es _Yubikey_.

> Existen alternativas a la hora de adquirir llaves hardware. Nitrokey es una empresa alemana que tiene productos similares y algunos son incluso hardware y software libre. Si hay algún interesado, [aquí](https://www.nitrokey.com/#comparison) puede acceder a sus productos.

Las Yubikeys tienen integración con [multitud de servicios y herramientas](https://www.yubico.com/setup/compatible-services/) y soportan diferentes formas de autenticación y protocolos. Por ejemplo, la Serie 5 de Yubikey soporta lo siguiente:

* Múltiples protocolos: FIDO2/WebAauthn, U2F, Smart card, OpenPGP y OTP.

* Distintos sistemas de conexión: USB-A, USB-C, NFC.

Existen diferentes modelos con sus propias características: a la hora de seleccionar cual es el adecuado debemos pensar que necesidades tenemos y el uso que les vamos a dar (si la vamos a usar sólo en el PC o también en el móvil). 

Las llaves hardware funcionan como la llave de nuestra casa y por ello tenemos que hacernos con dos unidades. Si perdemos una, perdemos el acceso al servicio y aunque en ocasiones hay formas para recuperar el acceso, no todos lo soportan y podemos perder nuestra cuenta __para siempre__.

Tras recibir las llaves, tan sólo tenemos que configurarlas a nuestro gusto. Para el caso que nos atañe, Yubico ha desarollado una herramienta gráfica llamada _Yubikey Manager_, que nos guía y facilita el proceso. Podemos descargar la aplicación [aquí](https://www.yubico.com/products/services-software/download/yubikey-manager/). Si usamos Linux, la descargamos y la ejecutamos para ver una ventana similar a ésta:

![yubikey-manager](https://storage.googleapis.com/tangelov-data/images/0034-00.png)

El programa ofrece tres menús diferentes:

* __Home__: muestra un breve resumen de la llave que hemos insertado (su versión de Firmware y su número de serie).

* __Applications__: permite configurar los diferentes métodos de autenticación que soporta la llave (OTP, FIDO2 y PIV).

* __Interfaces__: nos permite habilitar o bloquear los tipos de autenticación soportados por nuestra llave y a través de que interfaz (USB o NFC) escuchan.

![yubikey-manager-interfaces](https://storage.googleapis.com/tangelov-data/images/0034-01.png)

Ya podemos empezar a configurar servicios y aplicaciones :) .

### Gestores de contraseñas
Estas llaves pueden utilizarse con multitud de servicios y aplicaciones, siendo uno de ellos nuestro sistema de gestión de contraseñas. Estos sistemas facilitan el almacenamiento de diferentes contraseñas difíciles y aunque existen multitud de opciones distintas, éstos son algunos de los más conocidos:

* __1Password__: Es una plataforma web que nos permite almacenar nuestras contraseñas en la nube y autocompletar los formularios con ellas. Soporta los navegadores web más utilizados, Android, iOS y los principales SSOO de escritorio. Tiene un coste mensual de 2,50 dólares.

* __LastPass__: Otra plataforma web de características muy similares a las de 1Password. A pesar de haber tenido algunas vulnerabilidades en el pasado, sigue siendo muy usada y ofrece tanto un tier gratuito como una versión de pago (3 euros al mes). La versión premium ofrece muchas más capacidades que otros servicios.

* __Bitwarden__: Es una plataforma web, de código abierto, que podemos contratar como servicio o instalarlo en nuestro propio servidor. En su versión SaaS, ofrece unas características similares a las de LastPass a un coste inferior (1 euro al mes).

* __KeePass__: Es una herramienta offline, de código abierto, que nos permite una flexibilidad total a la hora de gestionar nuestras contraseñas. Su integración con los navegadores web y los teléfonos móviles está menos depurada que las alternativas anteriores.

Puesto que la gestión de mis contraseñas es algo crítico para mi, evito la utilización de servicios web y prefiero guardar la base de datos en mis servidores. Para ello, utilizo una versión comunitaria de KeePass llamada _KeepassXC_. Vamos a configurarla siguiendo su [documentación oficial](https://keepassxc.org/docs/#faq-yubikey-2fa), aunque voy a simplificar los pasos.

Primero debemos configurar en nuestra llave un sistema de OTP basado en HMC-SHA1 Challenge Response (soportado por KeepassXC). Para ello, accedemos a _Challenge-response_ en Yubikey Manager a través de _Applications_/_OTP_:

![yubikey-manager-otp](https://storage.googleapis.com/tangelov-data/images/0034-02.png)

Después tendremos que generar una clave secreta de hasta 40 carácteres en formato hexadecimal. La herramienta permtite generar dicha clave de forma aleatoria pero recomiendo generarlo a través de una cadena de texto que utilizamos como semilla. Lo hacemos con el siguiente comando ```bash echo -n "HolaTangelovers" | od -A n -t x1 | sed 's/ *//g' ``` . Ahora lo copiamos en el campo _Secret key_ y le damos a _Finish_:

![yubikey-manager-secret-key](https://storage.googleapis.com/tangelov-data/images/0034-03.png)

> No olvideis borrar del historial de la terminal dicho comando puesto que si vulneraran vuestro portátil, un atacante podría crear una llave exactamente igual a la nuestra. Tampoco olvideis configurar __dos__ llaves, con la misma contraseña.

Tras configurar la llave, ahora vamos a configurar KeepassXC. En la aplicación, nos vamos a _Base de Datos_, _Seguridad_ y marcamos _Agregar protección adicional_:

![keepass-yubikey](https://storage.googleapis.com/tangelov-data/images/0034-04.png)

Dos campos aparecerán en el tutorial y allí podremos elegir entre la creación de un fichero de claves o un Desafío/respuesta Yubikey, que es el que debemos seleccionar. Si la llave está conectada a nuestro PC, la herramienta la detectará automáticamente.

![keepass-yubikey-02](https://storage.googleapis.com/tangelov-data/images/0034-05.png)

Tras configurar la base de datos, si la cerramos e intentamos abrirla sin usar la llave, recibiremos el siguiente error.

![keepass-yubikey-03](https://storage.googleapis.com/tangelov-data/images/0034-06.png)

Si por el contrario, conectamos la llave y probamos a abrir la base de datos, el resultado será satisfactorio y podremos acceder a sus secretos:

![keepass-yubikey-04](https://storage.googleapis.com/tangelov-data/images/0034-07.png)

> __Nota__: A día de hoy, no existe ningún cliente de Android que soporte el sistema de 2FA con Yubikey que implementa KeepassXC, por lo que si vamos a acceder a la base de datos a través de nuestro teléfono móvil, no debemos realizar esta configuración.


## 2FA y Cloud Computing
Lo ideal sería configurar los sistemas de 2FA en todos los servicios que sea posible, pero por lo menos lo recomendado es hacerlo en aquellos en los que somos administradores. Es algo especialmente grave en herramientas o servicios que tengan acceso a sistemas de pago como tarjetas de crédito y por ello, en la siguiente parte del post vamos a configurar la autenticación en dos pasos para los principales proveedores de nube pública.

### Google Cloud Platform
El sistema de autenticación de Google Cloud Platform es el mismo que el de cualquiercuenta de Google. Para añadir autenticación en dos pasos, tan sólo accedemos a [esta URL](https://accounts.google.com) y una vez allí, vamos a seguridad y marcamos la _verificación en dos pasos_:

![yubikey-gcp](https://storage.googleapis.com/tangelov-data/images/0034-08.png)

Se lanzará un tutorial para su configuración: primero, tendremos que introducir otra vez nuestra contraseña y después podremos seleccionarl alguno de los métodos de 2FA que soporta (a través de un teléfono o con una llave de seguridad).

![yubikey-gcp-02](https://storage.googleapis.com/tangelov-data/images/0034-09.png)

Es posible que para finalizar el proceso tengamos que pulsar el botón de nuestra llave:

![yubikey-gcp-03](https://storage.googleapis.com/tangelov-data/images/0034-10.png)

Si ahora cerramos nuestra sesión e intentamos volver a loguearnos, tendremos que insertar nuestra llave y al hacerlo, recibiremos el siguiente mensaje:

![yubikey-gcp-04](https://storage.googleapis.com/tangelov-data/images/0034-11.png)

Nuestra cuenta de GCP ya se encuentra correctamente securizada.

### Amazon Web Services
AWS tiene dos tipos de cuenta en su nube: las llamadas cuentas raíz y las cuentas de IAM (Identity and Access Management). Todas permiten crear recursos, pero desde la cuenta raíz podemos crear cuentas hijas y es importante securizarlas correctamente. Amazon recomienda especialmente activar su sistema de autenticación en dos paso para todas las cuentas raíz.

Para comenzar a configurarlo, nos logueamos en nuestra cuenta raíz y entramos en _Mis credenciales de seguridad_:

![yubikey-aws](https://storage.googleapis.com/tangelov-data/images/0034-12.png)

Después seleccionamos _Multi-Factor Authentication (MFA)_ y hacemos click en _Activar MFA_:

![yubikey-aws-02](https://storage.googleapis.com/tangelov-data/images/0034-13.png)

Ahora seleccionamos _Llave de seguridad U2F_ y continuamos:

![yubikey-aws-03](https://storage.googleapis.com/tangelov-data/images/0034-14.png)

Tras finalizar todo el proceso, veremos que tenemos un nuevo registro en la consola web.

![yubikey-aws-04](https://storage.googleapis.com/tangelov-data/images/0034-15.png)

Si ahora tratáramos de volver a acceder, AWS nos pedirá nuestra llave para poder entrar, quedando el servicio bien securizado:

![yubikey-aws-05](https://storage.googleapis.com/tangelov-data/images/0034-16.png)


### Microsoft Azure
Los sistemas de 2FA de Microsoft son los más complejos puesto que varían en función de que tipo de cuenta estemos utilizando y de su plan de pago. En Microsoft Azure existen dos tipos de cuenta, las cuentas de Microsoft o las cuentas de Azure Active Directory.

Las cuentas de Microsoft son aquellas que utilizamos para dar de alta una cuenta en Azure u Office 365. Podemos configurar el 2FA [aquí](https://account.microsoft.com/security), pero a día de hoy, Microsoft no permite el uso de una llave hardware como 2FA en algunos de sus servicios (están soportados Outlook, OneDrive, Skype y la Microsoft Store).

Si permite la utilización de una llave como fuente primaria de autenticación (en lugar de contraseña). Aunque yo no estoy interesado en esa configuración, si alguien está interesado, le dejo un tutorial para hacerlo [aquí](https://www.ghacks.net/2018/11/21/how-to-set-up-a-security-key-for-your-microsoft-account/).

> La configuración de las llaves ha de hacerse desde un ordenador con Windows 10 y a través del navegador Microsoft Edge o de lo contrario no funcionará.

Si queremos usar algún otro método 2FA, sólo tenemos que loguearnos y darle al botón _Verificación en dos pasos_:

![yubikey-microsoft](https://storage.googleapis.com/tangelov-data/images/0034-17.png)

Y continuamos el tutorial en _Configurar la verificación en dos pasos_:

![yubikey-microsoft-02](https://storage.googleapis.com/tangelov-data/images/0034-18.png)

Las cuentas del Azure Active Directory (AAD) son aquellas que generamos dentro del servicio Active Directory de la consola. Por ello, antes de empezar vamos a ir a _Active Directory_ y creamos una cuenta nueva. Después podremos selecionarla y activar el MFA para dicha cuenta:

![yubikey-microsoft-03](https://storage.googleapis.com/tangelov-data/images/0034-19.png)

El siguiente paso es acceder a _Service Settings_ para configurar que tipos de autenticación en dos pasos permitimos:

![yubikey-microsoft-04](https://storage.googleapis.com/tangelov-data/images/0034-20.png)

Si ahora intentáramos loguearnos con dicho usuario, veremos que nos pide completar el proceso con algo más de información y que lanza un proceso de configuración del 2FA.

![yubikey-microsoft-05](https://storage.googleapis.com/tangelov-data/images/0034-21.png)

Estoy utilizando el Tier gratuito de Azure Active Directory, que no ofrece la posibilidad de utilizar llaves como 2FA, pero si una aplicación móvil o un SMS, etc. Si alguien tiene interés en configurarlo, tiene que contratar alguno de los tiers premium de AAD y revisar los siguientes enlaces ([éste](https://techcommunity.microsoft.com/t5/azure-active-directory-identity/hardware-oath-tokens-in-azure-mfa-in-the-cloud-are-now-available/ba-p/276466) y [éste](https://docs.microsoft.com/en-us/azure/active-directory/authentication/concept-mfa-licensing)), donde se explica las diferencias de cada Tier de Azure Active Directory y cómo configurar un token hardware.

Con este paso, ya hemos terminado. Espero que os guste y que no olvideis que la seguridad es muy importante. 


## Documentación

* [Twitter hack: What went wrong and why it matters (ENG)](https://www.bbc.com/news/technology-53428304)

* [Ataques de ingeniería social por INCIBE](https://www.incibe.es/protege-tu-empresa/blog/ingenieria-social-tecnicas-utilizadas-los-ciberdelincuentes-y-protegerse)

* [Time-based One-time Password algorithm (ENG)](https://en.wikipedia.org/wiki/Time-based_One-time_Password_algorithm)

* [Sobre Yubico (ENG)](https://www.yubico.com/about/about-us/)

* [Productos de Yubico (ENG)](https://www.yubico.com/products/)

* Configuración de gestores de contraseñas con Yubiko (ENG): [1Password](https://support.1password.com/security-key/), [LastPass](https://support.logmeininc.com/lastpass/help/yubikey-multifactor-authentication-lp030020), [Bitwarden](https://bitwarden.com/help/article/setup-two-step-login-yubikey/) y [KeePass](https://keepass.info/help/kb/yubikey.html).

* [Página web oficial de KeepassXC (ENG)](https://keepassxc.org/)

* [Configurar una llave de seguridad con una cuenta de Google (ENG)](https://support.google.com/accounts/answer/6103523?co=GENIE.Platform%3DAndroid&hl=en)

* [Configurar una llave de seguridad con cuentas de AWS (ENG)](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa_enable_u2f.html)

* [MFA with Microsoft services (ENG)](https://www.microsoft.com/en-us/security/business/identity/mfa)

* [How to configure Multi-Factor Authentication in Microsoft Azure (ENG)](https://docs.microsoft.com/en-us/azure/active-directory/authentication/concept-mfa-howitworks)

Revisado a 08/08/2020
