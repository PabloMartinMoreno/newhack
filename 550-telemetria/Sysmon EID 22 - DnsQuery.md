---
tipo: telemetria
plataforma: [windows]
producto: Sysmon
identificador: "EID 22"
por-defecto: false
coste: alto
aliases:
  - consulta DNS con proceso
  - DnsQuery
tags:
  - plataforma/windows
---

# Sysmon EID 22 - DnsQuery

## Qué lo genera

Cada consulta DNS que hace un proceso, **con el proceso incluido**.

Ese detalle es todo: [[Consulta DNS saliente]] recolectada en el servidor de nombres dice que el equipo resolvió un dominio raro; esta fuente dice **qué programa lo pidió**. La diferencia entre "alguien en esta máquina resolvió esto" y "este binario resolvió esto" es la diferencia entre una pista y un caso.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `Image` | Proceso que consulta | **El campo que justifica la fuente** |
| `QueryName` | Nombre consultado | El dominio |
| `QueryStatus` | Código de resultado | Un fallo repetido puede ser un dominio caído del atacante |
| `QueryResults` | Lo que devolvió | Las IP resueltas |
| `ProcessGuid` | Identificador del proceso | Une con la creación del proceso |

## Qué se ve acá

- **Exfiltración por DNS** — subdominios largos y de alta entropía, misma idea que [[Exfiltración por subdominios de alta entropía]] del lado web.
- **Mando y control** — consultas periódicas y regulares a un mismo dominio, con la cadencia de una baliza.
- **Un proceso que no debería resolver nada** haciéndolo. Es la señal más fuerte y la que solo esta fuente da.
- **Dominios recién registrados**, cruzando con datos de reputación.

## Coste de recolección

Alto. Un equipo de escritorio hace miles de consultas por hora, casi todas del navegador. Se filtra por proceso, igual que [[Sysmon EID 3 - NetworkConnect]].

## Cómo se activa

Sección correspondiente de la configuración de Sysmon. Requiere una versión razonablemente moderna de Sysmon y de Windows.

## Limitaciones

- **El caché tapa consultas.** Si el nombre ya está resuelto localmente, no hay consulta nueva y no hay evento. Un atacante que reusa el mismo dominio genera menos eventos de los que uno esperaría.
- **DNS cifrado la evade.** Si el proceso resuelve por su cuenta contra un servicio de DNS sobre HTTPS, no pasa por la pila del sistema y esta fuente no lo ve. Los navegadores lo hacen por defecto.
- **Volumen.**
- **No dice si la conexión se hizo**, solo que se resolvió. Se complementa con la conexión de red.

## Quién lo emite / quién lo consume

Rojo: pendiente — ver [[MOC - Telemetría de Windows]]
Azul: pendiente
