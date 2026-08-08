---
tipo: deteccion
tecnicas: ["[[CWE-915 - Improperly Controlled Modification of Dynamically-Determined Object Attributes]]", "[[CWE-862 - Missing Authorization]]"]
telemetria: ["[[Log de auditoría de la aplicación]]"]
forma: invariante
ventana: "por objeto"
estado: idea
fidelidad: alta
logica: kql
validada: 
aliases:
  - escalada silenciosa
tags:
  - dominio/web
---

# Cambio de privilegio fuera del flujo administrativo

## Qué detecta

Un atributo que gobierna privilegios —rol, permisos, estado de verificación, pertenencia a grupo— que cambia de valor **sin que el cambio provenga de la función administrativa que debería producirlo**.

Es la única detección posible para [[Control de acceso - mass assignment]], y su forma es `invariante` por una razón concreta: en el evento no hay nada anómalo. La petición es una actualización de perfil propio, con la sesión propia, sobre el objeto propio. Actor y dueño coinciden, así que [[Acceso a un objeto de otro usuario]] tampoco la ve.

La afirmación que se verifica es sobre el estado, no sobre la petición: *el rol de una cuenta solo cambia por la función de administración de roles*. Cualquier otra ruta que lo modifique es un fallo.

## Lógica

```
auditoria
| where campos_modificados has_any ('role', 'is_admin', 'permissions',
                                    'verified', 'group_id', 'scopes', 'tenant_id')
| where endpoint !in (endpoints_administrativos_autorizados)
| project timestamp, actor_id, objeto_id, endpoint, campo, valor_anterior, valor_nuevo
```

Variante de mayor fidelidad todavía, que no depende de conocer la lista de endpoints: **el actor y el objeto son el mismo**, y el campo modificado es de privilegio. Nadie se asciende a sí mismo por diseño.

```
| where actor_id == objeto_dueño_id and campo in ('role', 'is_admin', 'permissions')
```

Complemento para [[Control de acceso - escalada vertical]], que sí deja rastro en el rol efectivo:

```
auditoria
| where accion_es_administrativa == true
| where actor_rol !in ('admin', 'soporte')
```

## El requisito previo

> [!important] Depende del campo que menos se instrumenta
> [[Log de auditoría de la aplicación]] tiene que registrar **qué campos cambiaron**, no solo que hubo una actualización. Sin eso, el registro dice "el usuario A actualizó su perfil" — que es literalmente lo que pasó, y no dice nada.
>
> Junto con el dueño del objeto, son los dos campos de los que depende toda la cara azul de [[MOC - Broken access control]]. Se reportan como requisito de instrumentación, antes que cualquier regla.

## Falsos positivos conocidos

- **Migraciones y scripts de mantenimiento** que actualizan roles en masa. Se excluyen por actor, no por endpoint.
- **Aprovisionamiento automático** desde un proveedor de identidad o desde recursos humanos: cambia roles legítimamente y no pasa por la interfaz administrativa.
- **Flujos de autoservicio legítimos** — verificar el correo cambia un campo de estado por diseño. Hay que distinguir los campos que el usuario **puede** cambiar de los que no, que es la misma lista blanca que faltaba del lado de la aplicación.
- **Cambios administrativos por vía de API**, si la lista de endpoints autorizados está incompleta.

## Evasiones conocidas

- **Campos de privilegio no contemplados en la lista.** La regla es una lista negra de nombres de campo, con el problema de siempre: el campo que no está es el que importa. Se mitiga alertando por **cualquier** cambio de campo no editable por el usuario, que es una lista blanca y es la forma correcta.
- **Cambio indirecto** — modificar la pertenencia a un grupo que a su vez confiere el rol. Si el registro no sigue esa indirección, no se ve.
- **La aplicación no audita las escrituras** en absoluto, que es el caso común.

## Cómo se prueba

Disparador: [[Control de acceso - mass assignment]] contra un laboratorio, agregando un campo de rol a una actualización de perfil.

Es forma `invariante` y un caso la valida — **si el registro de auditoría incluye los campos modificados**. Verificar eso antes es lo que decide si la regla es escribible o si el trabajo es instrumentar primero.
