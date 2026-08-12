---
tipo: tradecraft
clase: "[[CWE-611 - XML External Entity]]"
eje: fase-del-flujo
implementacion: "Inyectar una entidad externa en la respuesta SAML antes de que se verifique la firma"
opsec: ruidoso
telemetria: ["[[Conexión saliente del servidor de aplicación]]", "[[Consulta DNS saliente]]", "[[Log de errores del servidor web]]"]
requisitos: [parser-que-resuelve-entidades-antes-de-validar]
coste: medio
alternativas: ["[[SAML - envoltura de firma XML]]", "[[XXE - canal fuera de banda]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - SAML XXE
  - entidad externa en SAML
tags:
  - dominio/web
---

# SAML - XXE en el parser de la aserción

## Cuándo lo elijo

Cuando el objetivo es el proveedor de servicio como servidor, no la sesión: una respuesta SAML es un documento XML que alguien tiene que parsear, y si ese parser resuelve entidades externas, hay XXE **antes** de que la firma entre en juego.

Es la rama que cambia de objetivo dentro del dominio: no busca autenticarse como la víctima sino leer archivos del servidor, alcanzar la red interna o provocar SSRF. Se elige cuando las ramas de firma no rindieron y el interés pasa de la cuenta al servidor, o directamente cuando el reconocimiento apunta al proveedor de servicio.

## Por qué funciona

El orden de operaciones es el que abre la puerta. Para verificar la firma, el proveedor de servicio primero tiene que **parsear el XML**, y el parseo ocurre antes de que se sepa si la firma es válida. Si el parser está configurado para resolver entidades —que es el valor por defecto de muchas bibliotecas de XML—, una entidad externa metida en la respuesta se resuelve aunque la firma después resulte inválida.

O sea que ni siquiera hace falta una firma válida: el daño está hecho en el parseo, aguas arriba de toda la lógica de SAML.

A partir de ahí es XXE ordinario y se sigue por [[MOC - XXE]]:

- Lectura de archivos locales con `file://` — canal directo si el error refleja contenido.
- Canal fuera de banda cuando no hay reflejo, con la entidad apuntando a un servidor propio — [[XXE - canal fuera de banda]].
- SSRF hacia la red interna o los metadatos de instancia, que en un proveedor de servicio corporativo suele estar bien conectado.

Lo específico de SAML es **dónde** se inyecta: la respuesta va codificada en base64 —y a veces desinflada— dentro del parámetro `SAMLResponse`, así que la entidad se mete en el XML antes de recodificar. La mecánica de decodificar y rearmar está en [[SAML - matriz de identificación]].

Es el mismo puente que ya había abierto [[File upload - XXE por archivo]]: un formato que se parsea como XML arrastra toda la superficie de XXE, y la `clase:` de esta nota es `CWE-611` y no una de SAML por la misma razón — la vulnerabilidad es que el parser resuelve entidades, SAML es el vector.

## Cómo falla

Falla contra un parser configurado para no resolver entidades externas ni DTD, que es la mitigación correcta de XXE y la que las bibliotecas de SAML mantenidas aplican por defecto desde hace años.

Falla cuando el proveedor de servicio valida la firma **antes** de parsear el contenido interno, aunque eso es raro porque el parseo es lo que produce la estructura sobre la que se valida.

Y falla parcialmente en el canal directo cuando los errores están suprimidos: ahí queda solo el canal fuera de banda, con su coste de montar un servidor propio.

## Coste

Medio. Confirmar si el parser resuelve entidades es una petición con una entidad de prueba que apunte a un servidor propio y ver si llega la consulta. Si llega, el resto es el coste de [[MOC - XXE]], que depende de si el canal es ciego.

El trabajo específico de SAML —decodificar el `SAMLResponse`, inyectar, recodificar, reajustar el desinflado— es fiddly pero mecánico, y la herramienta de SAML del proxy lo hace.

## Huella esperada

Es la rama ruidosa del dominio, y la única con huella propia sólida, porque a diferencia de las ramas de firma **el servidor hace algo observable**: resuelve una entidad, y eso es una conexión saliente.

- [[Conexión saliente del servidor de aplicación]] ve la petición si la entidad apunta afuera o a la red interna. Es el mismo artefacto que cubre el SSRF, y lo detecta [[Barrido de puertos internos desde el servidor de aplicación]] o [[Petición al servicio de metadatos de instancia]] según el destino.
- Con canal ciego queda [[Consulta DNS saliente]], que suele salir aunque el egress HTTP esté cerrado.
- El reconocimiento fallido —entidades mal formadas, DTD rechazadas— cae en [[Log de errores del servidor web]] como excepciones del parser.

El caso sin huella es el mismo que en [[MOC - XXE]]: una lectura local con `file://` que no refleja nada no emite conexión ni proceso. Ahí el dominio hereda el hueco de fuente de XXE, no uno propio.

A diferencia de las tres ramas de firma —silenciosas por naturaleza—, esta se detecta con las reglas que ya existen para SSRF y XXE, sin nada nuevo. Es la única cara azul aprovechable del dominio, y está entera del lado de la red, no del de la autenticación.
