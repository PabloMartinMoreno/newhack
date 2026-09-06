---
tipo: tradecraft
clase: "[[T1048 - Exfiltration Over Alternative Protocol]]"
eje: exfiltracion
implementacion: "Codificar los datos en un protocolo que el perímetro no filtra (DNS/ICMP) cuando la salida directa está cerrada"
opsec: requiere-bypass
telemetria: ["[[Consulta DNS saliente]]"]
requisitos: [resolucion-dns-recursiva-o-icmp-saliente]
coste: alto
alternativas: ["[[Exfiltración por canal abierto]]"]
probado: nunca
contexto: [win11-defender, ubuntu22-auditd]
aliases:
  - exfiltración encubierta
  - DNS tunneling
tags:
  - dominio/post-explotacion
---

# Exfiltración por canal encubierto

## Cuándo lo elijo

Cuando la salida directa está filtrada pero el host todavía **resuelve DNS** —casi siempre— o deja salir ICMP. Es la **última opción**: lenta, con firma, y con overhead de codificación. Se elige solo cuando [[Exfiltración por canal abierto]] no tiene por dónde.

DNS antes que ICMP: la resolución recursiva llega a mi servidor autoritativo aunque el host no tenga ninguna otra salida, mientras que ICMP saliente se filtra más seguido.

## Por qué funciona

El host no necesita salida directa: le basta con **resolver nombres**. Su resolutor reenvía la consulta por la cadena recursiva hasta mi servidor autoritativo del dominio (el mecanismo, en [[DNS - resolución recursiva]]), y los datos viajan codificados (base32) en las etiquetas del subdominio. ICMP es el mismo truco en el payload del echo. El perímetro deja pasar los dos porque romperían la red si los bloqueara del todo.

## Cómo falla

- **Resolución solo por un servidor interno sin recursión externa**: la consulta nunca llega a mi autoritativo.
- **Detección de entropía y volumen** de subdominios — es el caso raro donde la firma **sí** rinde, porque los subdominios de alta entropía no aparecen en tráfico legítimo. La cubre [[Exfiltración por subdominios de alta entropía]].
- Límites de longitud de etiqueta y de mensaje que obligan a fragmentar, multiplicando el volumen y la firma.

## Coste

Alto. Codificación, fragmentación en muchas consultas y lentitud de órdenes de magnitud frente al canal abierto. Sacar unos pocos MB puede llevar horas y miles de consultas. Sintaxis y herramientas en [[Exfiltración - matriz de referencia]].

## Huella esperada

- Volumen y entropía anómalos de subdominios hacia un mismo dominio, en [[Consulta DNS saliente]] — la firma que cubre [[Exfiltración por subdominios de alta entropía]]. Es la excepción del vault: acá la firma funciona.
- ICMP con payloads grandes y frecuentes: sin telemetría propia modelada — hueco de `550-telemetria/`, no de la detección.
