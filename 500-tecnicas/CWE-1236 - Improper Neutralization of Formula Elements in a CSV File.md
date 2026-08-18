---
tipo: tecnica
taxonomia: cwe
identificador: CWE-1236
wstg: WSTG-CLNT-14
tacticas: []
aliases:
  - CWE-1236
  - CSV injection
  - formula injection
  - inyección de fórmulas
tags:
  - dominio/web
---

# CWE-1236 - Improper Neutralization of Formula Elements in a CSV File

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - CSV injection]]; los payloads, en [[CSV - matriz de referencia]].

## Qué es

La aplicación exporta datos del usuario a un archivo CSV o de planilla —un informe, un listado de usuarios, un registro de actividad—. Si un campo empieza con un carácter que las hojas de cálculo interpretan como fórmula —`=`, `+`, `-`, `@`, tabulación o retorno de carro—, al abrir el archivo en Excel, LibreOffice Calc o Google Sheets, la aplicación **evalúa ese campo como una fórmula**. El atacante puso el campo; la fórmula ejecuta en la máquina de quien abre el export.

Es una inyección diferida y desplazada: el atacante escribe la carga en un campo cualquiera de la aplicación web —su nombre, un comentario, una dirección—, y la carga se ejecuta después, en **otro programa y en la máquina de otra persona**, cuando alguien exporta y abre el archivo.

## Por qué la víctima no es quien esperás

El que abre el CSV exportado casi nunca es un usuario común: es un **administrador o analista** que descarga el informe de usuarios, el listado de pedidos, el registro de soporte. Así que la fórmula ejecuta en el contexto de alguien con más privilegios que el atacante, en una máquina interna. Es lo que hace al dominio más peligroso de lo que sugiere su nombre inocuo.

## Qué se consigue

| Fórmula | Resultado |
|---|---|
| `HYPERLINK`, `WEBSERVICE`, `IMPORTXML` | Exfiltrar otras celdas —datos de otros usuarios— a un servidor del atacante |
| `HYPERLINK` a un dominio de phishing | Enlace de confianza dentro del informe interno |
| DDE / `cmd` | Ejecución de comandos en la máquina del analista, si DDE está habilitado |

La exfiltración es la más fiable: una fórmula puede leer el resto de la planilla —los datos de todos los usuarios del informe— y mandarlos por una petición de red que la propia hoja de cálculo dispara. La ejecución de comandos depende de configuraciones que los programas modernos deshabilitan por defecto, pero sigue viva en entornos viejos.

## Por qué la mitigación es del lado de la exportación

No se filtra la entrada web —un nombre puede legítimamente empezar con `+`—: la mitigación es **al exportar**.

- **Prefijar** con una comilla simple `'` cualquier celda que empiece con un carácter de fórmula, o con un espacio: la hoja de cálculo lo trata como texto.
- **Entrecomillar** el valor y escapar según el formato.
- No exportar a un formato que ejecute fórmulas cuando alcanza con texto plano.

Es una de las pocas clases donde la defensa está en un punto —la exportación— distinto de donde entra el dato —el formulario web—, y por eso se pasa por alto: el que valida la entrada no piensa en el export.

## Referencias canónicas

- [CWE-1236](https://cwe.mitre.org/data/definitions/1236.html)
- WSTG-CLNT-14
- OWASP — CSV Injection
