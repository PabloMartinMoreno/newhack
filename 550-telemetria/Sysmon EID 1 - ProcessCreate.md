---
tipo: telemetria
plataforma: [windows]
producto: Sysmon
identificador: "EID 1"
por-defecto: false
coste: alto
aliases:
  - creación de proceso Sysmon
  - ProcessCreate
tags:
  - plataforma/windows
---

# Sysmon EID 1 - ProcessCreate

## Qué lo genera

Cada proceso que nace. Es **el artefacto fundacional del lado azul en Windows**: la mayoría de las detecciones de endpoint empiezan mirando quién ejecutó qué, con qué argumentos y colgando de quién.

Su equivalente conceptual del lado web es [[Proceso hijo del servidor web]], y la lógica es la misma: la anomalía casi nunca está en el binario sino en **la relación padre-hijo** y en la línea de comandos.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `Image` | Ruta del ejecutable | Qué corrió |
| `CommandLine` | Argumentos completos | Donde vive casi toda la señal |
| `ParentImage` | Quién lo lanzó | **El campo que más discrimina** |
| `ParentCommandLine` | Con qué argumentos | Reconstruye la cadena |
| `User` | Contexto de seguridad | Distingue servicio de usuario |
| `Hashes` | MD5, SHA256, IMPHASH | Reputación y correlación |
| `ProcessGuid` | Identificador único | Une eventos del mismo proceso entre EID distintos |
| `OriginalFileName` | Nombre del binario según su recurso | **Delata el renombrado** |
| `IntegrityLevel` | Nivel de integridad | Detecta elevación |
| `CurrentDirectory` | Desde dónde corrió | Contexto |

`OriginalFileName` es el más subestimado: sobrevive a que el atacante renombre `mimikatz.exe` a `svchost.exe`, porque lo lee del recurso incrustado y no del nombre en disco.

`ProcessGuid` es lo que permite unir este evento con [[Sysmon EID 3 - NetworkConnect]] y [[Sysmon EID 11 - FileCreate]] del mismo proceso. Sin él, cada evento es un hecho suelto.

## Coste de recolección

Alto y muy dependiente de la configuración. Un equipo genera miles de creaciones por día, la mayoría de tareas programadas y de agentes. Una configuración sin filtros llena el SIEM y una demasiado filtrada deja huecos.

## Cómo se activa

No viene por defecto: Sysmon es una descarga aparte que se instala como servicio, con un archivo de configuración XML que decide qué se registra. **La configuración es el producto** — la calidad de esta fuente depende casi por entero de ella.

La alternativa nativa es [[Windows 4688 - Process creation]], que no necesita instalar nada y trae bastante menos.

## Limitaciones

- **No ve lo que no crea proceso.** Inyección en un proceso existente, código en memoria, o un intérprete que ejecuta dentro de sí mismo. Ver [[Sysmon EID 8 - CreateRemoteThread]].
- **La línea de comandos se puede ofuscar.** Sigue registrada, pero las firmas literales sobre ella se rompen fácil.
- **El padre puede mentir.** Con manipulación del proceso padre en la creación, un proceso puede declarar un progenitor que no lo lanzó — y ese campo es justo el que más se usa para discriminar.
- **La configuración decide todo.** Un filtro mal puesto excluye exactamente la carpeta que el atacante usa.
- **Es local.** Si el equipo no manda sus registros, la evidencia se pierde con el equipo.

## Quién lo emite / quién lo consume

Rojo: [[LSASS - volcado vía comsvcs.dll MiniDump]]
Azul: pendiente — ver [[MOC - Telemetría de Windows]]
