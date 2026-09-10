---
tipo: meta
aliases:
  - SNMP - matriz
  - snmp cheatsheet
tags:
  - meta/referencia
  - dominio/red
---

# SNMP - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puertos: 161/udp** (consultas) y **162/udp** (traps). En v1/v2c la autenticación es solo una **community string en texto plano**; v3 agrega usuario y cifrado. SNMP es **UDP** → nmap necesita `-sU`. Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST` es el objetivo; `COMM` la community string (por defecto `public` = lectura, `private` = escritura).

## Community string — encontrarla

Sin community válida no hay nada. Primero probar las de siempre (`public`, `private`, `community`, `manager`) y después forzar.

| Herramienta | Comando |
|---|---|
| onesixtyone (brute) | `onesixtyone -c communities.txt HOST` |
| nmap | `nmap -sU -p161 --script snmp-brute HOST` |
| hydra | `hydra -P communities.txt HOST snmp` |

Wordlist típica: `/usr/share/seclists/Discovery/SNMP/snmp.txt`.

## Enumerar

| Tarea | Comando |
|---|---|
| Walk completo (v2c) | `snmpwalk -v2c -c COMM HOST` |
| Walk de un OID | `snmpwalk -v2c -c COMM HOST 1.3.6.1.2.1.25.4.2.1.2` |
| Un valor puntual | `snmpget -v2c -c COMM HOST <OID>` |
| Enum formateado | `snmp-check HOST -c COMM` |
| Bulk rápido | `braa COMM@HOST:.1.3.6.*` |
| Scripts nmap | `nmap -sU -p161 --script 'snmp-*' HOST` |

`snmp-check` es el más cómodo: saca sistema, procesos, software, usuarios y puertos ya ordenado.

## OIDs jugosos

| OID | Qué da |
|---|---|
| `1.3.6.1.2.1.1` | Sistema: descripción, uptime, contacto, nombre |
| `1.3.6.1.2.1.25.4.2.1.2` | Procesos en ejecución |
| `1.3.6.1.2.1.25.4.2.1.4` | Rutas de los procesos |
| `1.3.6.1.2.1.25.4.2.1.5` | **Parámetros de la línea de comando** — acá aparecen contraseñas pasadas por argumento |
| `1.3.6.1.2.1.25.6.3.1.2` | Software instalado |
| `1.3.6.1.4.1.77.1.2.25` | Usuarios (Windows) |
| `1.3.6.1.2.1.6.13.1.3` | Puertos TCP locales |
| `1.3.6.1.2.1.25.1.6.0` | Cantidad de procesos |

El de mayor retorno es `25.4.2.1.5`: muchos servicios reciben la contraseña como argumento y SNMP la muestra en claro.

## Escritura (community RW)
Si la community de escritura (`private` y compañía) es válida, se puede **modificar** la configuración vía SNMP.

| Tarea | Comando |
|---|---|
| Escribir un valor | `snmpset -v2c -c COMM HOST <OID> <tipo> <valor>` |

Poco común, pero con RW se puede llegar a cambiar rutas, tablas o —según el MIB— ejecutar (extend/`NET-SNMP-EXTEND-MIB`).

## Configuración (con acceso al host)

| Archivo | Qué tiene |
|---|---|
| `/etc/snmp/snmpd.conf` | Config del demonio: communities, ACL, vistas, `extend` |
| `/var/lib/snmp/` | Datos persistentes del agente |


### Configuraciones peligrosas

| Config | Por qué importa |
|---|---|
| `rocommunity public` sin restricción de origen | Cualquiera lee toda la MIB |
| `rwcommunity <algo>` | Escritura remota → cambios de config, potencial RCE por `extend` |
| `com2sec ... default ...` | Acepta desde cualquier IP en vez de una red concreta |
| `extend`/`exec` en el `.conf` | Ejecuta comandos del SO; con RW o community adivinable, es RCE |


## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `Timeout: No Response` | community mala, o filtrado UDP | probar otra community; confirmar 161/udp con `nmap -sU` |
| walk cortísimo | la community solo ve una vista limitada | probar otras communities (RW ve más) |
| nmap dice 161 `open|filtered` | UDP no confirma sin respuesta | mandar una consulta real (`snmpwalk`) para decidir |
| `snmpset` falla con RO | usaste la community de lectura | necesitás la de escritura (`rwcommunity`) |

