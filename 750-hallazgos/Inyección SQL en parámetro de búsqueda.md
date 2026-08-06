---
tipo: hallazgo
severidad: critica
cvss: 9.8
vector-cvss: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
clase: "[[CWE-89 - SQL Injection]]"
esfuerzo-remediacion: medio
visibilidad: privada
creado: 2026-08-05
aliases: []
tags: []
---

# Inyección SQL en parámetro de búsqueda

> [!info] Texto reutilizable
> Redactado para pegar en un informe. **Cero datos de cliente**: los hostnames, parámetros y capturas concretas se agregan en el vault de engagements al momento de armar el informe.

## Descripción

La aplicación construye consultas SQL concatenando directamente valores provistos por el usuario, sin separar el canal de datos del de instrucciones. Un atacante no autenticado puede alterar la estructura de la consulta ejecutada por el motor de base de datos.

## Impacto

Permite la lectura completa de la información almacenada en la base de datos, incluyendo credenciales y datos personales. Según los privilegios de la cuenta de base de datos utilizada por la aplicación, también habilita la modificación o eliminación de registros, la lectura de archivos del sistema operativo y, en configuraciones permisivas, la ejecución de comandos en el servidor.

Al ser explotable sin autenticación y de forma remota, la severidad es crítica independientemente de la sensibilidad puntual de los datos expuestos.

## Evidencia

Se verificó la alteración de la lógica de la consulta mediante una condición controlada, comprobando dos respuestas distinguibles entre una condición verdadera y una falsa. Se confirmó la extracción de metadatos del motor sin acceder a información de producción más allá de lo necesario para demostrar el impacto.

## Remediación

1. **Consultas parametrizadas** en todos los accesos a la base de datos. Es la única mitigación que ataca la causa: separa código de datos. El escapado manual y las listas negras operan sobre un canal que sigue mezclado.
2. **Mínimo privilegio** para la cuenta de base de datos de la aplicación: sin permisos de escritura sobre el esquema, sin acceso a archivos, sin funciones administrativas.
3. **Validación de entrada** por lista blanca de formato, como defensa en profundidad. Nunca como control principal.
4. **WAF** solo como control compensatorio temporal mientras se corrige el código.

## Referencias

- [[CWE-89 - SQL Injection]] · WSTG-INPV-05
- OWASP SQL Injection Prevention Cheat Sheet
