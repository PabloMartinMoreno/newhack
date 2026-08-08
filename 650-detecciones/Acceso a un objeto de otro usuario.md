---
tipo: deteccion
tecnicas: ["[[CWE-639 - Authorization Bypass Through User-Controlled Key]]"]
telemetria: ["[[Log de auditoría de la aplicación]]"]
forma: correlacion
ventana: 
estado: idea
fidelidad: alta
logica: kql
validada: 
aliases:
  - detección de IDOR
tags:
  - dominio/web
---

# Acceso a un objeto de otro usuario

## Qué detecta

Un evento de auditoría donde **el actor no es el dueño del objeto** ni tiene un rol que lo justifique.

Es la única detección posible para [[Control de acceso - IDOR]], y la razón es estructural: la petición es válida, la sesión legítima y la respuesta `200`. No hay nada técnicamente anómalo. La anomalía es una **relación entre dos campos**, y por eso la forma es `correlacion`: no hay regla sobre un evento que pueda expresarla.

## Lógica

```
auditoria
| where accion in ('leer', 'modificar', 'borrar')
| where actor_id != objeto_dueño_id
| where actor_rol !in ('admin', 'soporte')
| project timestamp, actor_id, actor_rol, objeto_tipo, objeto_id, objeto_dueño_id, accion
```

Es una comparación de dos campos, y toda la dificultad está en que **esos dos campos existan en el registro**. Ver la sección de abajo.

Segunda regla, de forma `agregado`, para separar la enumeración masiva del acceso puntual:

```
auditoria
| where timestamp > ago(10m)
| where actor_id != objeto_dueño_id
| summarize objetos = dcount(objeto_id) by actor_id
| where objetos > 20
```

La primera encuentra el hecho; la segunda encuentra la extracción. Un atacante real dispara la primera y evita la segunda.

## El requisito previo, que es el problema real

> [!important] Esta regla no se puede escribir en la mayoría de las aplicaciones
> [[Log de auditoría de la aplicación]] casi siempre registra **actor y acción**, y casi nunca **el dueño del objeto**. Sin ese campo, el registro dice "el usuario A leyó el documento 4021" — que es cierto, inútil y exactamente lo que pasó.
>
> La recomendación defensiva de mayor retorno de todo el dominio web no es esta regla: es **instrumentar el campo del que depende**. Conviene reportarlo como requisito, no como detalle de implementación.

## Falsos positivos conocidos

- **Objetos compartidos legítimamente.** Es el falso positivo dominante y no se resuelve con una exclusión: exige que el registro incluya el **permiso efectivo**, no solo el dueño. En aplicaciones con compartición rica, esta regla no es viable sin ese tercer campo.
- **Administración y soporte** accediendo por su trabajo. Se excluyen por rol — y conviene mantenerlos en una regla aparte, porque un administrador leyendo mil registros de clientes también es algo que hay que ver.
- **Objetos de la organización** que no tienen dueño individual.
- **Procesos automáticos** que operan sobre objetos de todos.

## Evasiones conocidas

- **Acceso puntual.** Un atacante que lee un objeto y para no dispara la regla de volumen, y la de correlación depende por completo de que el campo exista.
- **[[Control de acceso - mass assignment]]** la evade entera: la operación es sobre el objeto **propio**, con la sesión propia. Actor y dueño coinciden. Se detecta por el campo modificado, no por la relación.
- **Objetos sin dueño modelado** — si el objeto no tiene propietario en el esquema, no hay nada que comparar.

## Cómo se prueba

Disparador: [[Control de acceso - IDOR]] con dos cuentas de laboratorio.

Antes de probar la regla hay que verificar el requisito: **si el registro de auditoría no tiene el dueño del objeto, la prueba falla por falta de datos y no por la regla**. Ese es el resultado más probable en una aplicación que no fue instrumentada a propósito.
