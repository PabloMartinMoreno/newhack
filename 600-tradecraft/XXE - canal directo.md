---
tipo: tradecraft
clase: "[[CWE-611 - XML External Entity]]"
eje: canal
implementacion: "Entidad general externa cuyo valor se refleja en la respuesta"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Conexión saliente del servidor de aplicación]]", "[[Registro del WAF]]"]
requisitos: [dtd-habilitada, valor-reflejado]
coste: bajo
alternativas: ["[[XXE - canal fuera de banda]]", "[[XXE - canal por error]]"]
probado: 2026-08-06
contexto: [php8-linux]
aliases:
  - XXE clásico
  - in-band XXE
tags:
  - dominio/web
---

# XXE - canal directo

## Cuándo lo elijo

Siempre primero. Es el caso feliz del árbol de [[MOC - XXE]]: la aplicación devuelve, en algún lado de la respuesta, un valor que vino del XML. Un nombre de producto, un identificador, un mensaje de confirmación que repite lo enviado — cualquier eco sirve como canal.

La prueba es barata: se reemplaza un campo cualquiera del XML por una entidad y se mira si el contenido del archivo aparece donde antes aparecía el campo. Dos peticiones y se sabe.

Si nada se refleja, el árbol baja a [[XXE - canal por error]] y después a [[XXE - canal fuera de banda]].

## Por qué funciona

El parser sustituye la entidad **antes** de que la aplicación vea el documento. Para el código de la app, el campo simplemente contiene el texto del archivo: no hay nada que distinguir, porque la sustitución ocurrió una capa más abajo. Toda la validación que la aplicación haga sobre el contenido llega tarde.

Es la misma asimetría que en el resto de las inyecciones: quien interpreta y quien valida no son el mismo componente, y el que interpreta va primero.

## Cómo falla

- **El DTD está deshabilitado** — la mitigación correcta, y cada vez más el valor por defecto. El documento se rechaza entero o la entidad queda sin resolver.
- **No se puede declarar `DOCTYPE`** — porque la app inserta la entrada dentro de un XML propio. No cierra el dominio: es exactamente el caso de [[XXE - XInclude]].
- **El archivo rompe el XML.** Si el contenido tiene `<`, `&` o secuencias que el parser interpreta, el documento queda mal formado y falla. Se resuelve leyendo en base64 con un wrapper, no cambiando de canal — ver [[XXE evasión - matriz de referencia]].
- **El valor se refleja truncado o escapado** — hay canal, pero de pocos bytes o con el contenido alterado.
- **El campo se valida por formato** — si espera un número y recibe el contenido de `/etc/passwd`, la app rechaza el documento después de haberlo leído. A veces el error mismo revela el contenido, lo que empuja a [[XXE - canal por error]].
- **Rutas que no existen o sin permiso** — el parser corre con el usuario del servidor, no con root. Muchos archivos interesantes no son legibles.

## Coste

El más bajo del dominio: una petición por archivo, contenido completo. Es también el más fácil de demostrar en un informe, porque la evidencia es la respuesta misma.

## Huella esperada

- [[Log de acceso del servidor web]] con un `POST` de `Content-Type` XML hacia un endpoint que normalmente recibe otra cosa. **El cuerpo no queda registrado**, que es el punto ciego central: el payload viaja donde el log de acceso no mira.
- [[Conexión saliente del servidor de aplicación]] solo si la entidad apunta a una URL. Si es `file://`, no hay tráfico de red en absoluto y esta variante es invisible para toda telemetría de red.
- Respuestas anormalmente grandes desde un endpoint que devuelve confirmaciones cortas.

Ese punto ciego —lectura local sin red y sin proceso hijo— hace que la detección real dependa de inspeccionar el cuerpo de la petición, cosa que ninguna de las fuentes por defecto hace.

Los payloads por canal están en [[XXE payloads - matriz de referencia]]; dónde aparece la superficie, en [[XXE formatos - matriz de referencia]].
