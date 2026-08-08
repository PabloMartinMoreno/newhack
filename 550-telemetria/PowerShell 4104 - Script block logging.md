---
tipo: telemetria
plataforma: [windows]
producto: PowerShell
identificador: "4104"
por-defecto: false
coste: alto
aliases:
  - script block logging
  - 4104
tags:
  - plataforma/windows
---

# PowerShell 4104 - Script block logging

## Qué lo genera

El contenido de cada bloque de código que PowerShell compila antes de ejecutarlo.

Es el artefacto más valioso de Windows para código, y lo que lo hace especial es **cuándo** se registra: **después de deofuscar**. PowerShell tiene que resolver la ofuscación para poder ejecutar, y el registro captura lo que quedó — así que el comando codificado en base64, concatenado y con mayúsculas alternadas se guarda ya limpio y legible.

Es el contraejemplo perfecto de [[Detectar el efecto sobrevive a la evasión]]: acá la firma sobre contenido **sí funciona**, porque la fuente ve el contenido después de todo lo que el atacante hizo para esconderlo.

## Campos relevantes

| Campo | Para qué sirve |
|---|---|
| `ScriptBlockText` | **El código, deofuscado** |
| `ScriptBlockId` | Une los fragmentos de un script largo |
| `MessageNumber` / `MessageTotal` | Numeración de los fragmentos |
| `Path` | Archivo, si vino de uno |

Los scripts largos se parten en varios eventos. **Reconstruirlos antes de buscar** es imprescindible: una firma sobre el evento suelto se pierde cuando la cadena buscada cae justo en el corte.

## Coste de recolección

Alto, y muy dependiente del entorno. En organizaciones que administran con PowerShell —que son casi todas— el volumen legítimo es enorme, y el texto completo de cada bloque es pesado de almacenar.

## Cómo se activa

Por directiva de grupo. No viene por defecto.

El evento hermano de transcripción guarda además la salida, no solo el código, y es complementario.

## Limitaciones

- **Degradación de versión.** Forzar una versión vieja del motor evita el registro entero, porque esa versión no lo implementa. Es la evasión clásica y se detecta mirando qué motor se cargó.
- **No cubre otros intérpretes.** Los muchos binarios firmados del sistema que ejecutan código sin PowerShell no dejan nada acá.
- **Ejecución desde memoria fuera del motor.** Código que corre en el proceso sin pasar por el compilador de PowerShell no genera este evento.
- **Volumen y peso.** El texto completo es caro.
- **Los administradores hacen cosas que parecen ataques.** Los scripts legítimos de administración usan las mismas construcciones que las herramientas ofensivas — descarga y ejecución, acceso remoto, manipulación de credenciales. Sin conocer los scripts propios, todo dispara.
- **La deofuscación no es total.** Lo que se construye dinámicamente en tiempo de ejecución puede seguir apareciendo ensamblado por partes.

## Quién lo emite / quién lo consume

Rojo: pendiente — ver [[MOC - Telemetría de Windows]]
Azul: pendiente
