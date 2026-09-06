---
tipo: teoria
habilita: ["[[Relay de NTLM]]", "[[Traer herramientas al objetivo]]"]
relacionadas: ["[[SMB - dialectos y firma]]", "[[MOC - AD enumeración]]"]
aliases:
  - sesión nula
  - null session
  - IPC$
tags: []
---

# SMB - sesión nula e IPC$

## Qué dice la especificación

Un servidor SMB expone recursos compartidos. Uno es especial: **IPC$** (Inter-Process Communication), que no contiene archivos sino las **canalizaciones con nombre** (named pipes) por las que hablan los servicios remotos —el administrador de servicios, el registro, LSARPC, SAMR—. Conectarse a IPC$ no es leer archivos: es abrir el canal de RPC sobre SMB.

La **sesión nula** (null session) es una conexión a IPC$ **sin usuario ni contraseña** — autenticación anónima. En su origen SMB la permitía para que servicios se descubrieran entre sí. A través de ella, y según la política del servidor, se pueden consultar por RPC: lista de usuarios y grupos, política de contraseñas, recursos compartidos, y la traducción de SID a nombre.

Windows moderno restringe la sesión nula por defecto (`RestrictAnonymous`, `RestrictAnonymousSAM`), pero sigue apareciendo en servidores viejos, dispositivos y configuraciones heredadas.

## Dónde el estándar deja lugar

En **cuánto** deja consultar el anónimo, que es enteramente política del servidor:

- Un servidor puede permitir listar usuarios y grupos por la sesión nula, o solo lo mínimo, o nada. Las tres son configuraciones válidas.
- La traducción SID↔nombre por la sesión nula habilita el **RID cycling**: aunque no se pueda listar usuarios, se pueden pedir uno por uno por su RID (500, 501, 1000, 1001…) y reconstruir la lista. La defensa contra "listar" no cubre "adivinar el RID y traducir".

## Qué habilita

- **La enumeración previa a tener credenciales.** Con la sesión nula se sacan usuarios (para spray o AS-REP), la política de contraseñas (para no bloquear cuentas) y los shares. Es la vía alternativa a la enumeración con credencial de [[MOC - AD enumeración]] — el árbol de ese MOC la lista como rama "sin credencial"; su sintaxis (enum4linux, rpcclient, `--rid-brute`) vive en su matriz.
- **La ejecución remota rueda sobre IPC$.** Los métodos tipo psexec/smbexec crean un servicio o escriben en una pipe a través de IPC$; el relay que termina en SMB ([[Relay de NTLM]]) usa esa misma canalización para ejecutar en el destino. Y traer herramientas por un recurso montado ([[Traer herramientas al objetivo]]) usa el mismo canal de sesión SMB.

## Cómo se ve en la práctica

La conexión a IPC$ aparece como un acceso a recurso compartido; la sesión nula, como un logon anónimo. En Windows, el acceso a shares se ve en `5145` (con el nombre del recurso), y el logon en [[Windows 4624 - Successful logon]] tipo 3 —con la cuenta `ANONYMOUS LOGON` cuando es sesión nula—. El detalle de qué pipe RPC se abrió no está en esos eventos: es visible en captura de red.

## Fuente

- MS-SRVS, MS-SAMR (Microsoft Open Specifications).
