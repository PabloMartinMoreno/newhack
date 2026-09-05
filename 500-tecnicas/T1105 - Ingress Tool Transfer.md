---
tipo: tecnica
taxonomia: attack
identificador: T1105
tacticas: [command-and-control]
aliases:
  - T1105
  - Ingress Tool Transfer
tags:
  - dominio/post-explotacion
---

# T1105 - Ingress Tool Transfer

## Qué es

Traer al host comprometido herramientas, binarios o scripts que no estaban ahí: el enumerador, el volcador de credenciales, el implante. El movimiento es **hacia adentro** — del box del atacante o de internet al objetivo.

## Por qué existe / qué la habilita

Después de la ejecución de código, casi nada útil vive ya en el objetivo. La cadena real necesita subir el arsenal. Lo habilita cualquier primitiva de descarga o escritura: una utilidad del sistema con capacidad de red (certutil, bitsadmin, curl, wget), un intérprete (PowerShell, Python) o un recurso montado (SMB servido desde el box del atacante).

## Ejes que la descomponen

El criterio no está en la técnica sino en el canal disponible. Ejes en [[MOC - Transferencia de archivos]]; el catálogo de comandos en [[Transferencia de archivos - matriz de referencia]].

| Eje | Valores |
|---|---|
| Restricción del canal | salida a internet · solo desde el box del atacante · egress filtrado |
| Recurso en el objetivo | utilidad del sistema (LOLBin) · intérprete · recurso montado |
| Sistema | Windows · Linux |

## Referencias canónicas

- MITRE ATT&CK: [T1105](https://attack.mitre.org/techniques/T1105/)
