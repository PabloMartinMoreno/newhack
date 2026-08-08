---
tipo: telemetria
plataforma: [windows]
producto: Sysmon
identificador: "EID 13"
por-defecto: false
coste: alto
aliases:
  - escritura de registro
  - RegistryValueSet
tags:
  - plataforma/windows
---

# Sysmon EID 13 - RegistryValueSet

## Qué lo genera

Escritura de un valor en el registro de Windows, con el proceso que la hizo. Los eventos hermanos cubren creación y borrado de claves (EID 12) y renombrado (EID 14).

El registro es donde Windows guarda **qué se ejecuta solo**, así que es el lugar natural de la persistencia. Y también donde vive la configuración de seguridad, así que es donde se la desactiva.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `Image` | Proceso que escribió | Quién |
| `TargetObject` | Ruta completa de la clave y el valor | Dónde — el campo central |
| `Details` | El valor escrito | **Suele traer la ruta del binario que va a ejecutar** |
| `EventType` | `SetValue` | Distingue del borrado |

`Details` es lo que hace útil a esta fuente: no solo dice que se tocó una clave de arranque automático, dice **qué se puso ahí**.

## Dónde mirar

Las tres familias que concentran casi todo el valor:

- **Arranque automático** — las claves de ejecución al inicio, servicios, tareas, y los muchos lugares menos obvios que Windows tiene para lo mismo.
- **Desactivación de defensas** — configuración del antivirus, del registro de eventos, de las políticas de ejecución de scripts. Un cambio ahí precede al resto del ataque.
- **Configuración de credenciales** — opciones que cambian cómo se almacenan o se cachean credenciales, para que haya más que robar.

## Coste de recolección

Alto sin filtros: el registro se escribe constantemente y la mayor parte es de sistema. Se domina con una **lista de inclusión** de las rutas que importan, que además está bien documentada por la comunidad.

## Cómo se activa

Sección correspondiente de la configuración de Sysmon, prácticamente siempre con lista de inclusión.

## Limitaciones

- **Las rutas se abrevian** en el campo de destino, con nombres de sección cortos en vez de los completos. Hay que normalizar antes de comparar, o las reglas no coinciden.
- **Volumen alto** si se registra de más.
- **La persistencia tiene muchísimos lugares posibles.** Cubrir los conocidos deja fuera los raros, y aparecen nuevos.
- **No ve lecturas**, solo escrituras. Un atacante que consulta configuración para orientarse no aparece.
- **Un cambio legítimo y uno malicioso se ven igual** salvo por el proceso que lo hizo y el valor escrito.

## Quién lo emite / quién lo consume

Rojo: pendiente — ver [[MOC - Telemetría de Windows]]
Azul: pendiente
