---
tipo: moc
dominio: post-explotacion
aliases:
  - MOC transferencia
  - MOC transferencia de archivos
tags:
  - dominio/post-explotacion
---

# MOC - Transferencia de archivos

> [!abstract] Dominio transversal de post-explotación
> Mover archivos hacia y desde un host comprometido. Se usa después de cualquier ejecución de código — tras un RCE web ([[MOC - Command injection]], [[MOC - File upload]]) o dentro de un dominio ([[MOC - AD movimiento lateral]]). La teoría de los canales, en [[MOC - Red]].

La transferencia no se decide por herramienta sino por **dirección** (traer o sacar) y por **qué canal deja el entorno**. La herramienta concreta es sintaxis, y vive en las matrices.

| Eje | Valores |
|---|---|
| Dirección | ingress (traer al objetivo) · exfiltración (sacar del objetivo) |
| Restricción del canal | abierto (HTTP/SMB/FTP) · encubierto (DNS/ICMP) |
| Sistema | Windows · Linux (sintaxis, no decisión → matriz) |

## Árbol de decisión

```
¿Hacia dónde muevo el archivo?
├─ ADENTRO — traer una herramienta  → [[Traer herramientas al objetivo]]
│  ├─ ¿hay salida a internet?      → descarga directa (certutil/curl/wget/IWR)
│  ├─ no, pero alcanzo mi box      → sirvo por SMB/HTTP y traigo
│  └─ egress filtrado              → pivotar, o traer codificado por el canal que quede
└─ AFUERA — sacar datos
   ├─ ¿el perímetro deja salir un protocolo general (443/FTP/SMB)?
   │  └─ Sí  → [[Exfiltración por canal abierto]]   ← primera opción: rápido y simple
   └─ ¿solo resuelve DNS, o deja ICMP?
      └─ [[Exfiltración por canal encubierto]]   ← última opción: lento y con firma
```

La decisión de fondo, en las dos direcciones, es la misma: **usar el canal más abierto que el entorno permita**, y bajar a uno encubierto solo cuando no queda otro. El encubierto cuesta órdenes de magnitud más y deja más firma, no menos.

## Orden de aprendizaje

1. [[Traer herramientas al objetivo]] — ingress; el principio LOLBin y el fallback por SMB
2. [[Exfiltración por canal abierto]] — sacar por el protocolo que ya sale
3. [[Exfiltración por canal encubierto]] — DNS/ICMP cuando el egress está cerrado

## Cara roja

- [[Traer herramientas al objetivo]] · [[Exfiltración por canal abierto]] · [[Exfiltración por canal encubierto]]
- Comandos por sistema: [[Transferencia de archivos - matriz de referencia]] (traer) · [[Exfiltración - matriz de referencia]] (sacar).
- Interacción con un servicio FTP (anónimo, subir/bajar, modo binario): [[FTP - matriz de referencia]].

## Cara azul

| Técnica | Emite | Detección |
|---|---|---|
| [[Traer herramientas al objetivo]] | [[Sysmon EID 1 - ProcessCreate\|Sysmon 1]] | [[Descarga de herramienta por utilidad del sistema]] |
| [[Exfiltración por canal abierto]] | [[Sysmon EID 3 - NetworkConnect\|Sysmon 3]] | efecto, no firma — línea base de destino y volumen |
| [[Exfiltración por canal encubierto]] | [[Consulta DNS saliente\|DNS saliente]] | [[Exfiltración por subdominios de alta entropía]] |

Dos lecciones que este dominio deja:

**El ingress se detecta por firma; la exfiltración abierta, no.** Traer un binario con una utilidad del sistema deja un proceso conocido con una URL en la línea de comando —firma de alto retorno—. Sacar datos por HTTPS es tráfico legítimo en la forma: la única señal es destino y volumen, que necesitan línea base. Ver [[Detectar el efecto sobrevive a la evasión]].

**El canal encubierto es la excepción donde la firma azul rinde.** Los subdominios de alta entropía del túnel DNS no existen en tráfico legítimo, así que una firma sobre ellos tiene pocos falsos positivos — al revés que casi todo el resto del vault.

## Huecos conocidos

- [x] Ingress con su detección (LOLBin), exfil abierta y encubierta, con matrices por sistema
- [x] Exfil por DNS cierra ciclo rojo↔azul con [[Exfiltración por subdominios de alta entropía]]
- [ ] **Exfil abierta sin detección propia** — es tráfico legítimo; solo la delata la línea base de destino/volumen, que el vault no modela (flow logs)
- [ ] **ICMP sin telemetría** — [[Exfiltración por canal encubierto]] por ICMP no tiene artefacto en `550-telemetria/`; hueco de telemetría, no de detección
- [ ] Pivoting y túneles (SOCKS, port-forwarding) — vecino de este dominio, sin abrir. Cuando esté, va como MOC hermano en Post-explotación
