---
tipo: tradecraft
clase: "[[CWE-1321 - Prototype Pollution]]"
eje: gadget
implementacion: "Contaminar desde la URL una propiedad que una biblioteca del navegador lee, hasta llegar a ejecución de JavaScript"
opsec: ruidoso
telemetria: ["[[Informe de violación de CSP]]", "[[Log de acceso del servidor web]]"]
requisitos: [parseo-de-query-string-vulnerable, gadget-en-una-biblioteca-cargada]
coste: medio
alternativas: ["[[XSS - DOM-based]]", "[[Prototype pollution - propiedad que gobierna una decisión]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - client-side prototype pollution
  - bypass de sanitizador
tags:
  - dominio/web
---

# Prototype pollution - gadget del lado del cliente

## Cuándo lo elijo

Cuando la contaminación ocurre en el navegador —típicamente porque la aplicación parsea la query string o el fragmento con una función vulnerable— y hay bibliotecas cargadas que leen opciones con valor por defecto.

El resultado es ejecución de JavaScript en el origen, o sea XSS por otro camino. Por eso las alternativas de esta nota son las de XSS, y por eso conviene compararla con [[XSS - DOM-based]] antes de invertir: si hay un sink directo, aquella es mucho más barata.

Lo que justifica esta rama es que **sobrevive donde el XSS clásico no**: el payload no contiene ninguna etiqueta ni ningún nombre de manejador, así que ningún sanitizador orientado a HTML lo ve pasar.

## Por qué funciona

El navegador tiene el mismo `Object.prototype` compartido que Node, y las bibliotecas del lado del cliente están llenas de objetos de opciones incompletos. Tres familias de gadget:

- **Bibliotecas que construyen HTML a partir de opciones.** jQuery y varias de interfaz leen propiedades opcionales que terminan concatenadas en el DOM. Contaminar una de esas inserta el atributo o el elemento que se quiera.
- **Sanitizadores configurables.** Es el caso más elegante del dominio: se contamina la configuración del sanitizador para que **acepte** lo que normalmente bloquea, y después se manda un payload de XSS común. La biblioteca sigue funcionando bien; lo que cambió es qué considera seguro.
- **Cargadores de recursos.** Propiedades que gobiernan de dónde se carga un script o una plantilla. Contaminadas, la aplicación misma trae y ejecuta código del atacante — y lo hace desde su propio origen, así que la política de contenido lo permite.

La tercera es la que más rinde contra una política de seguridad de contenido estricta: no hay evaluación dinámica de cadenas ni script en línea, hay una carga de script que la propia aplicación decide hacer.

La contaminación entra por la URL, y eso trae una ventaja operativa que conviene explotar: **el enlace es autocontenido**. No hace falta alojar nada ni pedirle a la víctima más que abrirlo, a diferencia de lo que necesita [[CSRF - token ausente o no ligado]].

## Cómo falla

Falla cuando el parseo de la query string es el nativo —`URLSearchParams` no contamina— o cuando la aplicación usa una versión parcheada de la biblioteca de parseo. Las funciones vulnerables concretas están en [[Prototype pollution - matriz de identificación]].

Falla cuando no hay ninguna biblioteca con gadget conocido cargada. Es un resultado frecuente en aplicaciones modernas con pocas dependencias del lado del cliente.

Y falla contra `Object.freeze(Object.prototype)` del lado del cliente, que casi nadie aplica pero cierra el problema.

## Coste

Medio. Confirmar la contaminación es una petición —se carga la página con el payload y se mira `Object.prototype` en la consola—. Encontrar el gadget depende de qué bibliotecas haya, y ahí hay herramienta que lo automatiza, así que es menos caro que el equivalente del lado del servidor.

Lo que encarece es la demostración limpia: hay que producir un enlace que funcione de una sola vez, y algunos gadget necesitan que la contaminación ocurra antes de que la biblioteca se inicialice, lo que obliga a que viaje en la parte de la URL que se procesa primero.

## Huella esperada

**El servidor casi no ve nada**, y esa es la diferencia importante con la rama del lado del servidor. La contaminación y la ejecución ocurren en el navegador de la víctima.

Lo único que queda del lado del servidor es la carga reflejada en la URL, si viaja por la query string: `__proto__[x]=y` en [[Log de acceso del servidor web]]. Es texto reconocible y lo cubre [[Payload de inyección en parámetros de la URL]] —la única detección de firma del vault—, que acá rinde mejor que en cualquier otro dominio porque la cadena no aparece en tráfico legítimo.

Si la contaminación viaja en el **fragmento**, el servidor no ve absolutamente nada: el fragmento no se manda. Ese caso solo lo ve [[Informe de violación de CSP]], y únicamente si el gadget termina violando la política — lo que no pasa con el gadget de carga de recursos, que es justo el que se elige contra una política estricta.

Es la misma limitación que tienen [[XSS - DOM-based]] y [[SSTI - del lado del cliente]], y por la misma razón: el ataque no cruza el servidor.
