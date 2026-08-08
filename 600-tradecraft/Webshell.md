---
tipo: tradecraft
clase: "[[CWE-434 - Unrestricted File Upload]]"
eje: payload
implementacion: "Archivo con código que el server ejecuta, para comandos o reverse shell"
opsec: quemado
telemetria: ["[[Log de acceso del servidor web]]", "[[Escritura de archivo en la raíz web]]"]
requisitos: [ejecucion-del-archivo-subido]
coste: bajo
alternativas: []
probado: 2026-08-06
contexto: [php8]
aliases:
  - web shell
  - webshell
tags:
  - dominio/web
---

# Webshell

## Cuándo lo elijo

Cuando logré que el server ejecute un archivo mío y quiero ejecutar comandos. Un webshell es el payload; la decisión es **webshell interactivo vs reverse shell**.

- **Reverse shell**: casi siempre mejor. Da una sesión real, sobrevive a la navegación, permite pivotear. Requiere egress hacia el atacante.
- **Webshell (comando por request)**: cuando no hay egress para la reversa, o para una prueba de concepto puntual. Cada comando es una petición HTTP.

## Por qué funciona

El server interpreta el archivo según su handler (PHP, JSP, ASP). Un archivo con `system($_GET['c'])` ejecuta lo que le pases en el parámetro con los privilegios del proceso web (`www-data` típicamente). Desde ahí se lanza una reverse shell para tener sesión.

## Cómo falla

- **El archivo no se ejecuta** donde cayó — se pasa a [[File upload + LFI]].
- **`disable_functions`** que bloquea `system`/`exec`/`shell_exec` — buscar la función que quede, o usar técnicas de bypass de disable_functions.
- **Sin egress** — no hay reverse shell; queda el webshell por HTTP.
- **AV/EDR web** que detecta y borra el webshell en disco.

## Coste

Bajo en técnica. El costo es de **OPSEC**: un webshell en disco es evidencia forense directa y lo levanta cualquier escaneo.

## Cómo falla como OPSEC

`opsec: quemado` como artefacto persistente: dejar un `.php` con `system($_GET)` en el webroot es de lo más ruidoso que hay. En engagement real: reverse shell en memoria, borrar el archivo subido apenas ejecuta, y registrar en el informe qué se dejó. Ver el aviso en [[Webshells - matriz de referencia]].

## Huella esperada

- El archivo subido en disco.
- Cada comando por webshell = un `GET`/`POST` con el comando en el [[Log de acceso del servidor web]].
- La reverse shell = una conexión saliente desde la IP del web server a la del atacante — anomalía de red fuerte.
- Un proceso `sh`/`bash` hijo del web server — el evento de host equivalente a lo que en Windows vería [[Sysmon EID 10 - ProcessAccess]] para otras cadenas.

Payloads en [[Webshells - matriz de referencia]].
