---
tipo: telemetria
plataforma: [windows]
producto: Windows Security
identificador: "4688"
por-defecto: false
coste: alto
aliases:
  - creación de proceso nativa
  - 4688
tags:
  - plataforma/windows
---

# Windows 4688 - Process creation

## Qué lo genera

Creación de un proceso, registrada por el propio Windows sin instalar nada.

Es la alternativa nativa a [[Sysmon EID 1 - ProcessCreate]], y la comparación entre ambos es la primera lección práctica de telemetría en Windows: **la fuente que ya está y la fuente que hay que instalar no dan lo mismo**.

## Campos relevantes

| Campo | Qué trae |
|---|---|
| `NewProcessName` | Ruta del ejecutable |
| `ProcessCommandLine` | Argumentos — **solo si se habilitó aparte** |
| `CreatorProcessName` | Proceso padre |
| `SubjectUserName` | Quién lo lanzó |
| `TokenElevationType` | Si corre elevado |
| `MandatoryLabel` | Nivel de integridad |

## Qué le falta frente a Sysmon

| | 4688 | Sysmon EID 1 |
|---|---|---|
| Línea de comandos | requiere directiva aparte | siempre |
| Hashes | no | sí |
| Identificador único de proceso | no | sí |
| Nombre original del binario | no | sí |
| Línea de comandos del padre | no | sí |
| Filtrado configurable | no | sí, completo |

La falta de identificador único es la más limitante en la práctica: **sin él no se pueden unir los eventos de un mismo proceso** entre fuentes distintas, y hay que correlacionar por identificador numérico de proceso, que Windows reutiliza.

## Coste de recolección

Alto, y sin posibilidad de filtrar: se registra todo o nada. Es la otra diferencia grande con Sysmon, que filtra en el origen. Acá el filtrado ocurre después, en el destino, con el volumen ya pagado.

## Cómo se activa

Dos cosas separadas, y la segunda se olvida siempre:

1. Habilitar la auditoría de creación de procesos por directiva.
2. Habilitar **la inclusión de la línea de comandos**, que es una directiva distinta.

Con el paso 1 solo, se registra que corrió `powershell.exe` y no con qué argumentos — que es donde vive toda la señal. Es el error de configuración más común en Windows, y conviene verificarlo antes de dar la fuente por buena.

## Limitaciones

- Todo lo de la tabla de arriba.
- **Sin filtrado en origen**, el volumen es fijo.
- **La línea de comandos puede contener secretos** de operaciones legítimas, y al registrarla se copian al SIEM. Es una consideración real de privacidad y de exposición.
- Mismos puntos ciegos que Sysmon para lo que no crea proceso.

## Cuándo alcanza

Cuando no se puede instalar Sysmon — equipos de terceros, servidores con cambio congelado, entornos con restricciones. Es peor y **es infinitamente mejor que nada**, sobre todo con la línea de comandos habilitada.

## Quién lo emite / quién lo consume

Rojo: pendiente — ver [[MOC - Telemetría de Windows]]
Azul: pendiente
