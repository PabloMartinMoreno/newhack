---
tipo: deteccion
tecnicas: ["[[CWE-89 - SQL Injection]]", "[[CWE-78 - OS Command Injection]]", "[[CWE-611 - XML External Entity]]"]
telemetria: ["[[Consulta DNS saliente]]"]
forma: agregado
ventana: "10m"
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - exfiltración por DNS
tags:
  - dominio/web
---

# Exfiltración por subdominios de alta entropía

## Qué detecta

Consultas DNS desde el servidor de aplicación hacia un dominio sin historial, con etiquetas largas y de alta entropía.

Cubre de una sola vez todos los canales fuera de banda del vault: [[SQLi - canal fuera de banda]], [[Command injection - canal fuera de banda]], [[XXE - canal fuera de banda]] y [[RFI - inclusión remota]]. Es la detección con mejor relación entre esfuerzo y cobertura del lado web, porque los cuatro dominios convergen en el mismo artefacto.

Lo que la hace posible es una restricción del propio canal: el atacante **necesita un subdominio único por consulta** o la caché de DNS se come la segunda. Esa obligación técnica es lo que produce la señal.

## Lógica

```
dns
| where timestamp > ago(10m)
| where origen_ip in (servidores_de_aplicacion)
| extend etiqueta = split(qname, '.')[0], dominio_base = strcat_array(array_slice(split(qname,'.'), -2, 2), '.')
| extend entropia = shannon_entropy(tostring(etiqueta))
| where strlen(tostring(etiqueta)) > 20 and entropia > 3.5
| summarize consultas = count(), unicos = dcount(qname) by origen_ip, dominio_base
| where unicos > 5
| where dominio_base !in (dominios_conocidos)
```

Dos condiciones hacen el trabajo: **entropía alta** —el dato exfiltrado va codificado, y el base64 tiene mucha más entropía que una palabra— y **muchos subdominios únicos bajo un mismo dominio base**, que es el patrón del troceo.

La lista blanca de dominios conocidos es imprescindible. Sin ella, esta regla es inutilizable.

## Falsos positivos conocidos

- **Redes de distribución de contenido, antivirus y telemetría de productos** usan subdominios generados con alta entropía por diseño. Son el falso positivo dominante y se resuelven con la lista blanca, que hay que construir sobre la línea base.
- **Comprobaciones de listas de reputación**, que codifican el dato consultado en el nombre — exactamente el mismo patrón que un canal de exfiltración, porque es el mismo mecanismo usado legítimamente.
- **Servicios de rastreo y de correo** con identificadores únicos por mensaje.
- **Kubernetes y descubrimiento de servicios**, que consultan nombres largos de forma constante.

## Evasiones conocidas

- **Bajar la entropía** codificando en algo que parezca lenguaje natural, a costa de capacidad. Barato de hacer y casi ninguna herramienta lo hace.
- **Pocas consultas** — si el dato entra en una, la condición de cardinalidad no se cumple. Es el caso de una confirmación de vulnerabilidad, que esta regla no ve.
- **Etiquetas cortas** repartidas en más consultas, que evaden el filtro de longitud.
- **Dominio con historial**: si el atacante usa un dominio ya presente en la lista blanca —comprometido, o de un servicio legítimo de interacción—, la regla no dispara.
- **HTTP saliente en vez de DNS**, cuando el egress lo permite. Ahí la detección que corresponde es la de [[Conexión saliente del servidor de aplicación]].

## Cómo se prueba

Disparador: [[SQLi - canal fuera de banda]] o [[Command injection - canal fuera de banda]] con un dominio propio en laboratorio.

Forma `agregado`: hace falta una exfiltración troceada real, no una consulta de confirmación. Y la lista blanca hay que construirla antes — es más trabajo que la regla misma.
