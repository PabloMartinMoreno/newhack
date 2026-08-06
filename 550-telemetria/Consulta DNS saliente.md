---
tipo: telemetria
plataforma: [linux, windows]
producto: DNS resolver / Zeek dns.log
identificador: "dns.log"
por-defecto: false
coste: medio
aliases:
  - dns.log
  - egress DNS
tags:
  - dominio/web
---

# Consulta DNS saliente

## Qué lo genera

Cualquier resolución de nombre que sale del servidor víctima hacia un dominio controlado por el atacante. Es el canal de los ataques fuera de banda: la base de datos resuelve `algo.atacante.com` y el subdominio lleva los datos robados.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| Query | Nombre completo consultado | El dato exfiltrado viaja en el subdominio |
| Cliente | IP que originó la consulta | Delata que fue el server de BD, no un usuario |
| Tipo | A, TXT, etc. | — |
| Timestamp | Momento | Correlación con la petición HTTP que la disparó |

## Coste de recolección

Medio. El volumen de DNS es alto, pero un servidor de base de datos que resuelve un dominio externo raro es una anomalía barata de detectar si se recolecta.

## Cómo se activa

No viene por defecto. Requiere un sensor de red (Zeek, un resolver con logging) o telemetría del propio resolver corporativo apuntada al SIEM.

## Limitaciones

- Si el server usa un resolver externo sin logging, el evento no existe.
- DNS sobre HTTPS lo vuelve invisible al sensor de red.
- No dice qué payload lo generó: hay que correlacionar con el log de aplicación.

## Quién lo emite / quién lo consume

Rojo: [[SQLi - canal fuera de banda]]
Azul: pendiente — ver [[Consultas del vault]] § Huecos defensivos propios
