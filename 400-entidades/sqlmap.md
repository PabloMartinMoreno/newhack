---
tipo: entidad
clase-entidad: herramienta
tecnicas: ["[[CWE-89 - SQL Injection]]"]
aliases: []
tags:
  - dominio/web
---

# sqlmap

## Qué es

Automatización de detección y explotación de SQLi. Prueba contextos, detecta motor y elige canal de extracción solo.

## Qué técnicas implementa

- [[SQLi - canal UNION]] · [[SQLi - canal basado en errores]] · [[SQLi - canal booleano ciego]] · [[SQLi - canal temporal ciego]] · [[SQLi - canal fuera de banda]]
- Impacto: lectura/escritura de archivos, shell de SO según motor y privilegios.

## Cuándo NO usarla

Cuando hay WAF con firmas: los payloads por defecto son de los más firmados que existen. Cuando el objetivo es sigilo: el volumen de peticiones es enorme y el `User-Agent` y el orden de pruebas son característicos.

En engagement con evasión requerida, la decisión se toma manualmente siguiendo [[MOC - SQL injection]] y sqlmap se usa, si acaso, con la inyección ya confirmada y acotada.

## Estado

Mantenida y activa.

> [!tip] Por qué esta nota es corta
> El vault **no se organiza por herramienta**. El conocimiento vive en las notas de técnica; esta nota solo mapea qué cubre sqlmap y cuándo estorba. Si sqlmap desaparece mañana, no se pierde nada más que este archivo.
