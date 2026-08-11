---
tipo: tradecraft
clase: "[[CWE-611 - XML External Entity]]"
eje: canal
implementacion: "Entidades de parámetro y DTD externa que exfiltran el archivo a un servidor propio"
opsec: ruidoso
telemetria: ["[[Conexión saliente del servidor de aplicación]]", "[[Consulta DNS saliente]]"]
requisitos: [dtd-habilitada, dtd-externa-permitida, egress-de-red]
coste: medio
alternativas: ["[[XXE - canal por error]]", "[[XXE - canal directo]]"]
probado: nunca
contexto: [php8-linux]
aliases:
  - blind XXE
  - XXE OOB
  - XXE ciego
tags:
  - dominio/web
---

# XXE - canal fuera de banda

## Cuándo lo elijo

Cuando el XML se procesa pero nada vuelve: ni el valor reflejado, ni un error útil. Es el caso normal en APIs que responden `200 OK` sin cuerpo, en SOAP con respuestas fijas y en procesadores de documentos que trabajan en segundo plano.

También es la vía obligada cuando el procesamiento es **asíncrono**. Si el documento se encola y se parsea después, no hay respuesta que observar; la conexión saliente llega igual cuando el trabajo se procesa.

Es la variante que hace que un XXE ciego valga tanto como uno directo, y por eso conviene intentarla antes de dar por perdido un parser que "no devuelve nada".

## Por qué funciona

Se apoya en dos piezas que hay que entender juntas.

**Las entidades de parámetro se pueden anidar.** Una entidad de parámetro puede contener la declaración de otra entidad, cuyo valor a su vez incluya el contenido de un archivo. El resultado es una entidad cuya *URL* lleva el archivo adentro: cuando el parser intenta resolverla, hace una petición al atacante con el dato en el camino.

**La declaración anidada tiene que vivir en una DTD externa.** La especificación no permite construir esa entidad dentro del subconjunto interno del propio documento. Por eso el payload se parte en dos: el documento declara una entidad de parámetro que apunta a una DTD en el servidor del atacante, y esa DTD trae la maquinaria de exfiltración.

Esa partición es lo que explica el requisito extra respecto de [[XXE - canal directo]]: no alcanza con que el DTD esté habilitado, hace falta que además se permita **DTD externa** y que haya egress.

## Cómo falla

- **La DTD externa está bloqueada** aunque el DTD esté habilitado. Es una configuración intermedia frecuente, y deja al canal por error como única salida.
- **Egress bloqueado** — sin salida no hay canal. Se cae a [[XXE - canal por error]].
- **DNS resuelve pero HTTP no sale** — se puede exfiltrar por el nombre de dominio, con el límite de longitud y de alfabeto que eso impone.
- **El archivo tiene caracteres que rompen la URL** — saltos de línea, `&`, `%`. Obliga a leer en base64 con un wrapper, y en PHP eso además resuelve el problema de tamaño.
- **Caché de DNS** — cada exfiltración necesita un subdominio único o la segunda no genera tráfico.
- **Es la variante más ruidosa**: una conexión saliente hacia un dominio externo desde un parser XML no tiene explicación legítima en casi ningún despliegue.
- **Infraestructura atribuible** — hace falta un dominio y un servidor propios que reciban tanto la DTD como los datos.

## Coste

Medio: dos conexiones salientes por exfiltración —una por la DTD, otra por el dato— y un servidor propio sirviendo la DTD. A cambio devuelve el archivo entero en una petición, en vez de un bit por vez.

## Huella esperada

- [[Conexión saliente del servidor de aplicación]] **dos veces seguidas** hacia el mismo dominio externo: primero la descarga de la DTD, después la exfiltración. Ese par consecutivo es la firma más específica del dominio.
- [[Consulta DNS saliente]] hacia un dominio sin historial, con subdominio de alta entropía si el dato viaja por DNS.
- El proceso que abre la conexión es el de la aplicación, no un navegador ni un cliente HTTP explícito. Correlacionar con el `POST` de XML entrante cierra la causa.

Los payloads completos, con el documento y la DTD, están en [[XXE payloads - matriz de referencia]] § Fuera de banda.
