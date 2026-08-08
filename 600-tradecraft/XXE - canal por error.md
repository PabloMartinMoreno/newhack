---
tipo: tradecraft
clase: "[[CWE-611 - XML External Entity]]"
eje: canal
implementacion: "Forzar un error del parser cuyo mensaje contenga el archivo leído"
opsec: ruidoso
telemetria: ["[[Log de errores del servidor web]]", "[[Log de acceso del servidor web]]"]
requisitos: [dtd-habilitada, errores-detallados-al-cliente]
coste: medio
alternativas: ["[[XXE - canal fuera de banda]]", "[[XXE - canal directo]]"]
probado: 2026-08-06
contexto: [php8-linux]
aliases:
  - error-based XXE
  - XXE por error
tags:
  - dominio/web
---

# XXE - canal por error

## Cuándo lo elijo

Cuando no hay reflejo y **no hay egress**. Es la rama que salva el caso donde [[XXE - canal fuera de banda]] no funciona porque la red está cerrada, que es cada vez más común en despliegues serios.

Su requisito propio es distinto del de los otros canales y conviene verificarlo primero: la aplicación tiene que **devolver errores detallados al cliente**. Un `500` genérico no sirve. Se comprueba mandando un XML mal formado a propósito y viendo si vuelve una traza o solo una página de error.

También aparece como efecto lateral: a veces se está probando el canal directo, el campo se valida por formato, y el error de validación termina citando el contenido del archivo. Ahí el canal se encuentra sin buscarlo.

## Por qué funciona

Se usa el mismo anidamiento de entidades de parámetro que en el canal fuera de banda, pero en vez de construir una URL hacia el atacante, se construye una **ruta local que no existe** con el contenido del archivo incrustado adentro.

El parser intenta abrir esa ruta, falla, y escribe un mensaje de error que incluye la ruta completa — o sea, el archivo. El canal de datos es el mensaje de error, exactamente igual que en [[SQLi - canal basado en errores]].

La DTD externa sigue siendo necesaria por la misma razón de siempre: la declaración anidada no se puede hacer dentro del documento. Si la DTD externa está bloqueada y no hay egress, este canal tampoco funciona, y el dominio queda cerrado salvo por [[XXE - XInclude]].

## Cómo falla

- **Errores genéricos al cliente** — es la configuración correcta en producción y anula el canal por completo. El dato llega al [[Log de errores del servidor web]] y no al atacante.
- **El mensaje se trunca** — muchos parsers cortan la ruta citada. Se recupera un fragmento por petición y hay que ir moviendo el desplazamiento de lectura, lo que multiplica el coste.
- **No hay egress para servir la DTD** — el mismo problema que en fuera de banda. Hay una salida parcial: en algunos entornos se puede referenciar una DTD que ya existe en el sistema de archivos local y redefinir una de sus entidades.
- **Saltos de línea en el archivo** — muchos mensajes de error muestran solo la primera línea. Leer en base64 lo resuelve, a costa de decodificar después.
- **El parser no cita la ruta** — algunos escriben un error genérico sin incluir el recurso que fallaron en abrir. Sin la ruta en el mensaje no hay canal.

## Coste

Medio: una o varias peticiones por archivo según cuánto trunque el mensaje. Más barato que fuera de banda en infraestructura —no hace falta servidor receptor si la DTD se puede servir de otro modo— y más caro en cantidad de peticiones.

## Huella esperada

Es la variante que **más rastro deja en el servidor y menos en la red**, y esa asimetría la vuelve particularmente detectable para quien mire el lugar correcto.

- [[Log de errores del servidor web]] con excepciones del parser XML citando rutas inexistentes que **contienen el contenido de archivos del sistema**. Es un indicador casi sin falsos positivos: ninguna operación legítima produce un error así.
- Ráfaga de errores del mismo tipo en poco tiempo, cada uno con una ruta ligeramente distinta.
- [[Log de acceso del servidor web]] muestra los `POST` correspondientes, todos devolviendo `500`. La correlación entre la ráfaga de errores y la ráfaga de `500` cierra el caso.
- Si la DTD se sirve desde fuera, además hay conexión saliente y aplica lo de [[XXE - canal fuera de banda]].

Los payloads están en [[XXE payloads - matriz de referencia]] § Por error.
