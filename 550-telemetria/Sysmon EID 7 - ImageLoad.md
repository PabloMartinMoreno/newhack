---
tipo: telemetria
plataforma: [windows]
producto: Sysmon
identificador: "EID 7"
por-defecto: false
coste: alto
aliases:
  - carga de DLL
  - ImageLoad
tags:
  - plataforma/windows
---

# Sysmon EID 7 - ImageLoad

## Qué lo genera

Cada vez que un proceso carga un módulo — una DLL o un ejecutable mapeado en memoria.

Es el artefacto **más caro y el más revelador** de Sysmon. Caro porque un solo proceso carga decenas o cientos de módulos al arrancar; revelador porque muchas técnicas dejan su rastro exactamente acá y en ningún otro lado.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `Image` | Proceso que carga | Quién |
| `ImageLoaded` | Ruta del módulo | Qué |
| `Signed` | Si está firmado | **El primer filtro** |
| `Signature` | Quién firma | Distingue Microsoft de terceros |
| `SignatureStatus` | Válida, expirada, revocada | Una firma inválida es señal fuerte |
| `Hashes` | Para reputación | — |
| `OriginalFileName` | Nombre real del módulo | Delata renombrado |

Las dos preguntas que rinden: **un módulo sin firmar cargado por un binario firmado del sistema**, y **un módulo cargado desde una ruta que no es la de sistema**. Las dos juntas son la firma de la carga lateral de bibliotecas, que es de las técnicas más usadas para ejecutar código dentro de un proceso confiable.

## Coste de recolección

Muy alto, el mayor de todos. Sin filtros esta fuente sola puede superar en volumen a todo el resto de Sysmon junto.

Se domina al revés que las demás: en vez de excluir lo ruidoso, se **incluye solo lo interesante** — módulos sin firmar, cargados desde rutas de usuario o temporales, o los módulos concretos asociados a técnicas conocidas. Es la fuente donde la configuración importa más.

## Cómo se activa

Sección correspondiente de la configuración de Sysmon, **casi siempre con lista de inclusión** y no de exclusión. Muchas plantillas la traen apagada.

## Limitaciones

- **Volumen.** Es su limitación dominante y condiciona todo lo demás.
- **La firma no implica confianza.** Un módulo firmado y legítimo cargado por el proceso equivocado, o un binario vulnerable firmado que carga lo que se le ponga al lado, siguen siendo el vector.
- **No ve código que nunca se carga como módulo** — un ejecutable reflexivo en memoria puede no generar este evento.
- **La verificación de firma tiene coste** y puede afectar el rendimiento del equipo si la configuración es agresiva.

## Quién lo emite / quién lo consume

Rojo: pendiente — ver [[MOC - Telemetría de Windows]]
Azul: pendiente
