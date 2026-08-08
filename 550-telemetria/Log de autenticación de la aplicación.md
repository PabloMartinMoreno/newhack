---
tipo: telemetria
plataforma: [linux, windows]
producto: la aplicación / proveedor de identidad / WAF
identificador: "evento de acceso"
por-defecto: false
coste: bajo
aliases:
  - log de login
  - eventos de autenticación
  - authentication log
tags:
  - dominio/web
---

# Log de autenticación de la aplicación

## Qué lo genera

Cada intento de acceso, exitoso o fallido, y cada evento del ciclo de vida de la credencial: cambio de contraseña, alta o baja de segundo factor, uso de código de respaldo, petición y consumo de un restablecimiento.

Es el artefacto de [[MOC - Autenticación]] y, a diferencia de [[Log de auditoría de la aplicación]], suele existir: casi todos los marcos de trabajo y todos los proveedores de identidad lo emiten. El problema no es que falte, es que **casi nadie lo agrega**.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| Cuenta | A quién se intentó acceder | Base de todo |
| Resultado | Éxito, fallo, y **el motivo** | "Usuario inexistente" y "contraseña incorrecta" son señales distintas |
| Origen | IP, ASN, país, huella de cliente | El eje donde se ve el spraying |
| Factor verificado | Primero, segundo, ambos | Detecta accesos que saltaron el MFA |
| Marca de tiempo | Cuándo | Tasa y distribución |
| Agente de usuario | Cliente | Un cliente automatizado no se parece a un navegador |
| Camino de acceso | Web, API, móvil, protocolo heredado | **Revela el camino sin MFA** |

Las filas de motivo, factor y camino son las que casi nunca se registran, y son justo las que separan un historial de una detección.

## Coste de recolección

Bajo en volumen. Su problema es de **agregación**, no de coste: los eventos individuales son inocuos y la señal solo aparece al mirarlos juntos. Un fallo de acceso no es nada; mil fallos de una IP contra mil cuentas distintas es un ataque, y ninguna regla que mire un evento por vez lo va a ver.

## Cómo se activa

- **Proveedor de identidad** — ya lo tiene y lo expone; es la fuente más completa y la más fácil de conseguir.
- **Marco de trabajo de la aplicación** — suele emitir eventos de acceso que hay que enganchar y enviar.
- **WAF o balanceador** — ve las peticiones al endpoint de acceso pero no el resultado, que es la mitad que importa.

## Limitaciones

- **Sin el motivo del fallo no se distingue enumeración de adivinanza.** Es el campo más barato de agregar y el que más cambia.
- **Los caminos alternativos suelen registrar en otro lado, o en ninguno.** Una API heredada sin MFA puede además no emitir eventos, que es la peor combinación posible.
- **Detrás de un proxy sin propagación del origen, todo viene de la misma IP** y el eje de origen desaparece.
- **[[Autenticación - credential stuffing]] acierta a la primera**: no genera fallos. Para esa variante hay que mirar los **éxitos** anómalos —origen nuevo, muchas cuentas distintas desde una IP— y no los rechazos.
- **La retención suele ser corta** y estos ataques se descubren tarde.

## Quién lo emite / quién lo consume

Rojo: [[Autenticación - enumeración de usuarios]] · [[Autenticación - password spraying]] · [[Autenticación - credential stuffing]] · [[Autenticación - bypass de segundo factor]] · [[Autenticación - abuso de recuperación de contraseña]]
Azul: [[Accesos exitosos contra muchas cuentas desde un origen]] · [[Actividad de sesión posterior a su cierre]] · [[Fallos de acceso contra cuentas inexistentes]] · [[Misma sesión desde dos orígenes]]
