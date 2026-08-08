---
tipo: deteccion
tecnicas: ["[[CWE-434 - Unrestricted File Upload]]", "[[CWE-78 - OS Command Injection]]"]
telemetria: ["[[Escritura de archivo en la raíz web]]", "[[Log de acceso del servidor web]]"]
forma: correlacion
ventana: 
estado: idea
fidelidad: alta
logica: kql
validada: 
aliases:
  - primer acceso a una webshell
tags:
  - dominio/web
---

# Archivo creado y solicitado a los segundos

## Qué detecta

Un archivo creado en la raíz web y pedido por HTTP inmediatamente después, desde el mismo origen que causó su creación.

Es la firma de la **puesta en uso** de una webshell, y su fuerza no está en ninguno de los dos eventos: está en la relación entre ellos. Crear un archivo puede ser un despliegue; pedirlo puede ser un usuario; **crearlo y pedirlo a los cuatro segundos, desde la misma IP que hizo el POST anterior, no es ninguna de las dos cosas**.

Complementa a [[Archivo ejecutable nuevo en la raíz web]] cubriendo lo que aquella deja pasar: un archivo con extensión no listada, o escrito en un directorio de subidas excluido, sigue delatándose cuando alguien lo usa.

## Lógica

```
escrituras_webroot
| project archivo = TargetFilename, creado = timestamp, proceso = Image
| join kind=inner (
    accesos
    | project uri_path, pedido = timestamp, client_ip, status, method
  ) on $left.archivo == $right.uri_path_resuelto
| where pedido between (creado .. creado + 5m)
| summarize primer_acceso = min(pedido), accesos = count() by archivo, creado, client_ip
| where primer_acceso - creado < 5m
```

Refuerzo que cierra la cadena entera y convierte la alerta en un caso ya investigado: buscar en [[Log de acceso del servidor web]] la petición **anterior** a la creación desde la misma IP. Esa es la explotación —la subida, la inyección— y con ella el informe queda completo: cómo entró, qué escribió, cuándo lo usó.

Segunda condición de alto valor: **el archivo nunca fue pedido antes de existir**. Un recurso legítimo desplegado suele recibir tráfico difuso; una webshell recibe su primera petición desde la IP que la puso, y a veces es la única que la pide nunca.

## Falsos positivos conocidos

- **Despliegue seguido de comprobación de salud**, que pide el archivo recién publicado. Es el falso positivo dominante y se descarta por proceso creador y por origen: la comprobación viene de un monitor conocido.
- **Subida legítima de contenido** que el usuario visualiza enseguida — una imagen de perfil, un documento adjunto. Se descarta por extensión: lo que interesa es lo ejecutable.
- **Caché compilada** pedida inmediatamente después de generarse, que es su comportamiento normal.
- **Generadores de sitios estáticos** que publican y verifican.

## Evasiones conocidas

- **Esperar.** Si el atacante deja pasar horas entre escribir la webshell y usarla, la correlación temporal se rompe. Es la evasión obvia, cuesta nada y funciona — la ventana de cinco minutos define exactamente cuánto hay que esperar.
- **Pedirla desde otro origen**, lo que rompe la correlación por IP pero no la temporal.
- **No usarla** — dejarla como acceso de reserva. Ahí queda [[Archivo ejecutable nuevo en la raíz web]] como única detección.
- **Escribir fuera de la raíz** y llegar por inclusión: no hay petición HTTP directa al archivo.

Esta regla atrapa la operación apurada, que es la mayoría. Un atacante paciente la evade.

## Cómo se prueba

Disparador: [[File upload + LFI]] o [[Webshell]] escrita por [[Command injection - canal ciego]], y pedirla enseguida.

Es forma `correlacion` y un caso la valida. Lo que hace falta verificar antes es que **ambas fuentes compartan una clave que se pueda unir**: la ruta del archivo en disco tiene que poder resolverse a la ruta URI, y eso depende de la configuración del servidor. Si no se puede mapear, la regla no se escribe.
