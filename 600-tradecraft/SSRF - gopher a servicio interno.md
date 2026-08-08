---
tipo: tradecraft
clase: "[[CWE-918 - Server-Side Request Forgery]]"
eje: esquema
implementacion: "Cambiar de esquema para hablar protocolos de texto arbitrarios contra un servicio interno"
opsec: ruidoso
telemetria: ["[[Conexión saliente del servidor de aplicación]]", "[[Escritura de archivo en la raíz web]]"]
requisitos: [esquema-no-http-permitido, servicio-interno-sin-autenticacion]
coste: medio
alternativas: ["[[SSRF - escaneo de la red interna]]", "[[Command injection - canal directo]]"]
probado: 2026-08-06
contexto: [php8-linux]
aliases:
  - gopher SSRF
  - SSRF a RCE
tags:
  - dominio/web
---

# SSRF - gopher a servicio interno

## Cuándo lo elijo

Cuando hay un servicio interno alcanzable que habla un protocolo de texto sin autenticación, y el objetivo pasa de leer a **ejecutar**. Es la rama del árbol de [[MOC - SSRF]] que convierte un SSRF en RCE, y la única que lo hace sin depender de otra vulnerabilidad.

Es también la razón por la que un SSRF ciego puede ser crítico: escribir en Redis o mandar un correo no necesita ver la respuesta. El comando surte efecto igual.

Antes de intentarlo hay que confirmar dos cosas, y la primera falla seguido: que el esquema esté permitido por el cliente HTTP, y que exista un servicio que valga la pena. La segunda parte está en [[SSRF destinos - matriz de referencia]]; para la primera, ver "Cómo falla".

## Por qué funciona

`gopher` permite especificar **bytes arbitrarios** dentro de la URL, incluidos saltos de línea codificados. Como la mayoría de los protocolos internos son texto plano terminado en salto de línea —Redis, SMTP, memcached, FastCGI—, una URL bien construida es indistinguible de un cliente legítimo de ese protocolo.

Lo que hace explotable a esos servicios no es un fallo suyo: es que **no autentican por diseño**, porque asumen que la red los protege. Redis escribe archivos arbitrarios con su propia configuración; FastCGI ejecuta código; SMTP manda correo con el remitente que se le pida. Todas son funciones documentadas, invocadas por quien no debería poder invocarlas.

El SSRF aporta la única pieza que faltaba: alcance de red.

## Cómo falla

- **`gopher` no está disponible, y cada vez menos.** Es el motivo principal de fracaso hoy. `libcurl` lo trae deshabilitado por defecto desde finales de 2022, y en muchos lenguajes el manejador nunca existió o se quitó hace años. **Este es el campo `probado:` de esta nota haciendo su trabajo: la técnica es de las que más caduca.** Antes de invertir tiempo, confirmar que el esquema responde distinto de uno inventado.
- **Solo se permiten `http` y `https`** — la mitigación correcta, y la más frecuente.
- **La URL se normaliza o se codifica** — cualquier reescritura que toque los saltos de línea codificados rompe el payload entero. Es frágil por construcción.
- **El servicio interno sí autentica** — Redis con contraseña, SMTP con credenciales. Cierra la vía sin más.
- **La carga es larga y algo la trunca** — un límite de longitud de URL en un proxy intermedio corta el payload por la mitad y el comando llega incompleto.
- **`dict://` como alternativa es mucho más limitado** — sirve para leer banners y mandar un comando suelto, no para una secuencia.

## Coste

Medio en construcción —el payload hay que armarlo con cuidado y se rompe fácil—, bajo en ejecución. La parte cara es el reconocimiento previo: descubrir qué servicio interno hay y en qué puerto, que es trabajo de [[SSRF - escaneo de la red interna]].

## Huella esperada

- [[Conexión saliente del servidor de aplicación]] hacia un puerto de servicio interno desde el proceso de la aplicación web. Si la app no usa Redis, una conexión al 6379 desde ella no tiene explicación.
- **El servicio interno registra la operación como legítima**, porque lo es: un `CONFIG SET` de Redis o un correo enviado aparecen como actividad normal. La anomalía está en el origen, no en el evento — y solo se ve correlacionando ambos lados.
- Si el objetivo era escribir en disco vía Redis, el archivo resultante y su primera lectura por HTTP son el rastro más duro que queda.
- Una URL con `gopher://` o con muchos `%0d%0a` en [[Log de acceso del servidor web]] es una firma casi sin falsos positivos — cuando el payload viaja por GET.

Los esquemas por lenguaje y los payloads por servicio están en [[SSRF esquemas - matriz de referencia]].
