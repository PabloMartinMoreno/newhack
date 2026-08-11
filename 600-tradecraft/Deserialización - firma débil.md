---
tipo: tradecraft
clase: "[[CWE-502 - Deserialization of Untrusted Data]]"
eje: obstaculo
implementacion: "Recuperar o eludir la clave que firma el blob para poder reemplazarlo"
opsec: limpio
telemetria: ["[[Log de errores del servidor web]]", "[[Log de acceso del servidor web]]"]
requisitos: [blob-firmado, clave-recuperable]
coste: alto
alternativas: ["[[Deserialización - manipulación de objeto]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - clave de firma filtrada
  - secreto de framework
tags:
  - dominio/web
---

# Deserialización - firma débil

## Cuándo lo elijo

Cuando el blob está firmado y por eso las otras dos ramas están cerradas. Es el obstáculo del dominio, y la nota existe porque **la firma es la mitigación que de verdad se encuentra en producción**: los marcos de trabajo modernos firman sus cookies de sesión por defecto, así que casi todo objeto serializado que se ve en la vida real viene con firma.

La pregunta deja de ser "¿qué pongo en el objeto?" y pasa a ser "¿puedo firmar yo?". Y esa se responde en un solo lugar: **la clave del marco de trabajo**.

Antes de invertir acá conviene descartar lo barato: que la firma **no se verifique realmente**. Es más común de lo que parece — se firma al emitir y nadie comprueba al recibir. Cuesta una petición: se cambia un byte del blob y se mira si el servidor protesta.

## Por qué funciona

Porque la seguridad del esquema entero se reduce a un secreto único, de larga vida y ampliamente compartido dentro de la organización. Ese secreto tiene una tendencia bien documentada a filtrarse:

**Valores por defecto y de ejemplo.** Claves de la documentación, de plantillas de despliegue o de imágenes de contenedor que nadie rotó.

**Repositorios.** El archivo de configuración con el secreto, en un repositorio público o en el historial de uno privado que se abrió después. Es la vía más productiva y no es técnica.

**Otra vulnerabilidad.** [[Path traversal]], [[LFI - inclusión local]] o [[XXE - canal directo]] leyendo el archivo de configuración. Acá el dominio se encadena: una lectura de archivos que parecía de impacto medio se convierte en ejecución.

**Fuerza bruta fuera de línea.** Si la clave es corta o de diccionario, se recupera probando contra la firma sin tocar el servidor. Mismo mecanismo que en [[Sesión - falsificación de JWT]] § secreto débil, y los mismos límites.

## Cómo falla

- **Clave larga, aleatoria y rotada** — la mitigación, y hace inviable la fuerza bruta.
- **La clave no se filtró en ningún lado** — el caso normal si la higiene de secretos es decente.
- **La firma cubre más que el blob** — si incluye un identificador de sesión o de usuario, reproducirla exige más que la clave.
- **Lista blanca de clases además de firma.** La defensa correcta es en profundidad: aunque el atacante consiga firmar, no puede instanciar lo que quiera.
- **Rotación** — la clave recuperada deja de servir, y el acceso se pierde sin aviso.

## Coste

Alto y muy variable. Encontrar la clave filtrada puede ser una búsqueda de cinco minutos en un repositorio o no ocurrir nunca. La fuerza bruta fuera de línea es barata en riesgo y cara en cómputo, y solo vale contra secretos elegidos a mano.

Es la rama con mayor varianza del dominio: o sale enseguida o no sale.

## Huella esperada

`opsec: limpio` en la explotación y con dos ventanas de detección:

- **La búsqueda de la clave es fuera de línea.** La fuerza bruta no genera ni una petición al objetivo. Si la clave vino de un repositorio, tampoco.
- **Los intentos fallidos sí se ven.** Un blob con firma inválida genera excepción en [[Log de errores del servidor web]], y **nadie manda una firma inválida por accidente**. Es un indicador de alta fidelidad, y es la única señal de la fase de prueba.
- Una vez con la clave correcta, la petición es indistinguible de una legítima: firma válida, objeto válido. Lo que queda es la detección del **efecto** — [[Cambio de privilegio fuera del flujo administrativo]] si se manipuló el objeto, o [[Intérprete de comandos como hijo del servidor web]] si se ejecutó una cadena.
- Si la clave salió de leer un archivo de configuración, la huella real es la de esa lectura, no la de acá.

Los secretos por marco de trabajo y dónde viven están en [[Deserialización - matriz de identificación]] § Firma.
