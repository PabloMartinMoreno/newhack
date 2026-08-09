---
tipo: telemetria
plataforma: [windows]
producto: Windows Security
identificador: "4624"
por-defecto: true
coste: alto
aliases:
  - inicio de sesión exitoso
  - 4624
tags:
  - plataforma/windows
---

# Windows 4624 - Successful logon

## Qué lo genera

Un inicio de sesión exitoso. Es el artefacto central del movimiento lateral: **cada salto de una máquina a otra deja uno de estos** en el destino.

Está activado por defecto, que lo vuelve la fuente de Windows con mejor relación entre disponibilidad y valor.

## El campo que hay que aprender primero

`LogonType` cambia por completo el significado del evento. Sin leerlo, todos los accesos parecen iguales:

| Tipo | Qué fue | Por qué importa |
|---|---|---|
| 2 | Interactivo, en el teclado | Presencia física o consola virtual |
| 3 | Red | **El del movimiento lateral**: recursos compartidos, ejecución remota |
| 4 | Tarea programada | Persistencia |
| 5 | Servicio | Un servicio arrancando con sus credenciales |
| 7 | Desbloqueo | — |
| 8 | Red con credenciales en claro | Raro y digno de mirar |
| 9 | Credenciales nuevas | **Ejecutar como otro usuario solo para la red** — típico de suplantación de credenciales robadas |
| 10 | Interactivo remoto | Escritorio remoto |
| 11 | Interactivo con caché | Sin contacto con el controlador de dominio |

El 3 y el 10 son los que más aparecen en una investigación de movimiento lateral. El 9 es de los más informativos y de los menos conocidos.

## Otros campos relevantes

| Campo | Para qué sirve |
|---|---|
| `TargetUserName` | Quién entró |
| `IpAddress` / `WorkstationName` | Desde dónde |
| `AuthenticationPackageName` | Kerberos o NTLM — **NTLM donde debería haber Kerberos es señal** |
| `LogonProcessName` | Qué componente autenticó |
| `TargetLogonId` | Une este acceso con lo que se hizo después |
| `ImpersonationLevel` | Nivel de suplantación |

`TargetLogonId` es el equivalente del identificador de proceso para sesiones: es lo que permite atar un acceso con la actividad posterior. Sin él, saber que alguien entró no sirve para saber qué hizo.

## Coste de recolección

Alto. Un controlador de dominio genera muchísimos por minuto, la mayoría de tipo 3 y perfectamente rutinarios. El volumen es el problema central de esta fuente.

## Cómo se activa

Viene por defecto en la mayoría de las configuraciones. Lo que hay que verificar es la **retención** y que se esté centralizando: en el equipo solo, se pierde con el equipo.

## Limitaciones

- **Volumen enorme**, sobre todo en controladores de dominio.
- **Sin contexto de qué se hizo después.** El acceso no dice nada de la actividad; hay que unir por identificador de sesión.
- **El origen puede estar vacío o ser incorrecto** en accesos locales o a través de ciertos servicios.
- **Un acceso legítimo y uno con credenciales robadas se ven idénticos.** No hay campo que los distinga: la diferencia está en el patrón —origen inusual, horario, combinación de cuenta y equipo que nunca ocurrió—, que es de forma `agregado`. Ver [[La detección vive en el agregado, no en el evento]].

## Quién lo emite / quién lo consume

Rojo: [[Enumeración LDAP del directorio]] · [[Pass-the-hash]] · [[Pass-the-ticket]] · [[Golden ticket]]
Azul: pendiente
