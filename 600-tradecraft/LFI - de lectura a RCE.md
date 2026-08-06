---
tipo: tradecraft
clase: "[[CWE-98 - File Inclusion]]"
eje: via-a-rce
implementacion: "Envenenar un archivo que el server escribe, después incluirlo"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [lfi-que-ejecuta, archivo-envenenable]
coste: medio
alternativas: ["[[LFI wrappers - matriz de referencia]]"]
probado: 2026-08-06
contexto: [php8]
aliases:
  - LFI a RCE
  - LFI to RCE
tags:
  - dominio/web
---

# LFI - de lectura a RCE

## Cuándo lo elijo

Cuando ya tengo [[LFI - inclusión local]] que ejecuta y quiero pasar de leer archivos a **correr código**. Esta nota es la decisión de **qué vía** de escalada elegir; los payloads están en [[LFI a RCE - matriz de referencia]].

La idea común de casi todas las vías: hacer que el server **escriba** PHP mío en algún archivo que yo pueda predecir, y después incluir ese archivo.

## Cómo elijo la vía

```
¿Solo tengo php://filter, sin poder escribir nada?  → filter chains (wrappers)
¿Puedo influir un log que se escribe?               → log poisoning (User-Agent, auth.log…)
¿La app guarda algo mío en la sesión?               → session poisoning
¿Puedo subir un archivo aunque no se ejecute?       → zip:// / phar:// + [[MOC - File upload]]
¿Hay un phpinfo() accesible?                         → phpinfo LFI race
```

Orden de preferencia por fiabilidad: **filter chains** (no depende de nada externo) → **log poisoning** (necesita ubicar el log y que sea legible) → **session** → el resto.

## Por qué funciona

`include` ejecuta lo que lee. Cualquier archivo bajo control del atacante —parcial o total— que termine incluido, ejecuta. Los logs guardan headers que yo controlo; las sesiones guardan datos que yo mando; los wrappers generan el PHP sin tocar el disco.

## Cómo falla

- **No ubico el log / no es legible** — rutas distintas por distro, permisos.
- **`open_basedir`** que impide leer `/var/log` o `/tmp`.
- **La sesión no guarda nada mío** o el path de sesiones no es estándar.
- **Filter chains bloqueadas** por WAF que detecta la cadena larga de `php://filter`.

## Coste

Medio: encontrar el archivo envenenable y la ruta correcta lleva prueba y error. Una vez identificado, la ejecución es directa.

## Huella esperada

- El payload PHP queda **escrito** en el log/sesión incluido — evidencia persistente, no solo en el access.log de la petición.
- La petición de inclusión con la ruta al log/sesión.

Payloads en [[LFI a RCE - matriz de referencia]].
