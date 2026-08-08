---
tipo: telemetria
plataforma: [windows]
producto: Windows Security
identificador: "4662"
por-defecto: false
coste: alto
aliases:
  - operación sobre objeto de directorio
  - 4662
tags:
  - plataforma/windows
---

# Windows 4662 - Directory object operation

## Qué lo genera

Una operación sobre un objeto de Active Directory: leer una propiedad, escribirla, modificar permisos.

Es la fuente de la **replicación abusiva** —conocida como DCSync—, que es la técnica por la que un atacante con permisos suficientes le pide al controlador de dominio una copia de los hashes de contraseña de todo el dominio, sin tocar el disco de ninguna máquina.

## Por qué es especial

Casi todas las técnicas contra Active Directory se detectan por su efecto en algún endpoint. Esta no toca ningún endpoint: **usa el protocolo de replicación como estaba previsto**, hablando con el controlador como si fuera otro controlador. No hay proceso que nazca, ni archivo que se escriba, ni conexión rara.

Lo único observable es la operación de directorio en sí, y solo si está auditada.

## Campos relevantes

| Campo | Para qué sirve |
|---|---|
| `SubjectUserName` | Quién hizo la operación |
| `ObjectName` | Sobre qué objeto |
| `Properties` | **Qué propiedad o derecho extendido** — el campo central |
| `AccessMask` | Qué tipo de acceso |
| `ObjectType` | Clase del objeto |

Toda la detección vive en `Properties`: los derechos extendidos de replicación de cambios aparecen ahí como identificadores. Cuando esos derechos los invoca algo que **no es una cuenta de controlador de dominio**, no hay explicación legítima.

## Coste de recolección

Muy alto si se audita de más — un controlador hace incontables operaciones de directorio por segundo. Es de las fuentes que más fácil ahogan un SIEM.

Se domina auditando **selectivamente**: solo los objetos y los derechos que importan, no todo el directorio.

## Cómo se activa

Dos pasos, y el segundo es el que se olvida:

1. Habilitar la auditoría de acceso al servicio de directorio por directiva.
2. **Configurar la lista de auditoría en los objetos concretos** que se quieren vigilar, empezando por la raíz del dominio.

Sin el paso 2 la directiva está encendida y no se registra nada útil. Es el error de configuración clásico de esta fuente, y hace creer que hay cobertura donde no la hay — ver [[Ausencia de alertas no es ausencia de ataque]].

## Limitaciones

- **No viene por defecto** y su configuración es la más laboriosa de las fuentes de Windows.
- **Volumen** si se audita ampliamente.
- **Los identificadores de derechos son opacos.** Hay que traducirlos para que el evento se pueda leer, y ninguna herramienta lo hace sola.
- **Una cuenta de controlador legítima genera lo mismo.** La distinción es quién lo pidió, no qué se pidió.
- **Solo en controladores de dominio**, y hay que recolectar de todos.

## Quién lo emite / quién lo consume

Rojo: pendiente — [[MOC - Active Directory]] está sin desarrollar
Azul: pendiente — ver [[MOC - Telemetría de Windows]]
