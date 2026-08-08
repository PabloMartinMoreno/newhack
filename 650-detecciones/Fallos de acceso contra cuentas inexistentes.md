---
tipo: deteccion
tecnicas: ["[[CWE-204 - Observable Response Discrepancy]]", "[[CWE-307 - Improper Restriction of Excessive Authentication Attempts]]"]
telemetria: ["[[Log de autenticación de la aplicación]]"]
forma: agregado
ventana: "5m"
estado: idea
fidelidad: alta
logica: kql
validada: 
aliases:
  - detección de enumeración
tags:
  - dominio/web
---

# Fallos de acceso contra cuentas inexistentes

## Qué detecta

Una proporción anómala de intentos de acceso contra cuentas que **no existen**, desde un mismo origen y en una ventana corta.

Es la firma de [[Autenticación - enumeración de usuarios]], y lo que la separa de un ataque de credenciales es exactamente ese detalle: en la enumeración la mayoría de los objetivos **no existen**; en el spraying, casi todos existen. Un contador de fallos no distingue las dos cosas; la proporción sí.

Depende por completo de que el registro guarde el **motivo** del fallo. Es el campo más barato de agregar del vault y el que más cambia lo que se puede detectar.

## Lógica

```
autenticacion
| where timestamp > ago(5m)
| where resultado == 'fallo'
| summarize
    total = count(),
    inexistentes = countif(motivo == 'usuario_no_encontrado'),
    cuentas = dcount(cuenta)
  by origen_ip
| where total > 20 and cuentas > 15 and inexistentes * 1.0 / total > 0.5
```

Regla hermana, misma ventana, para [[Autenticación - password spraying]] — cambia una condición y detecta lo contrario:

```
| where cuentas > 50 and inexistentes * 1.0 / total < 0.2
    and intentos_por_cuenta <= 2
```

Un fallo por cuenta sobre muchas cuentas **que existen** es rociado. Ninguna cuenta llega al umbral de bloqueo y el agregado es inconfundible: es el ejemplo canónico de por qué contar por cuenta no sirve.

Y una tercera, la más importante de las tres: **la tasa global de fallos de la aplicación**, sin agrupar por origen. Un spraying distribuido evade las dos anteriores y sigue moviendo ese número.

## Falsos positivos conocidos

- **Un cliente móvil o una integración con credenciales viejas** reintentando en bucle: muchos fallos, **una** cuenta. El filtro de cardinalidad los descarta.
- **Migraciones de usuarios**, donde mucha gente intenta con la cuenta del sistema anterior — genera un pico de "usuario no encontrado" perfectamente legítimo.
- **Escáneres autorizados** y pruebas de carga.
- **Un formulario de acceso público en internet** recibe intentos de fondo permanentemente. Eso sube la línea base y hay que medirla, no suponerla.

## Evasiones conocidas

- **Bajar el ritmo** por debajo del umbral. La ventana define cuán lento hay que ir, y a un atacante paciente le sobra tiempo.
- **Distribuir el origen**, que anula las dos primeras reglas. Solo queda la tasa global, y por eso está.
- **Enumerar por otro endpoint** — registro, recuperación o una API — que puede no emitir eventos de autenticación en absoluto. Es la evasión más práctica y la que más veces funciona: ver [[Autenticación - matriz de referencia]] § Enumeración.
- **Oráculo por tiempo** en lugar de por mensaje: si la aplicación responde igual y solo difiere la latencia, puede que ni siquiera registre un fallo. Es el caso donde la enumeración es invisible para esta fuente.
- **[[Autenticación - credential stuffing]]** la evade por diseño: acierta a la primera y no genera fallos. Tiene detección propia.

## Cómo se prueba

Disparadores: [[Autenticación - enumeración de usuarios]] y [[Autenticación - password spraying]] en laboratorio.

Forma `agregado`: hace falta volumen y línea base. Y hace falta verificar el requisito primero — **si el registro no guarda el motivo del fallo, la primera regla no se puede escribir** y hay que caer en el conteo simple, que confunde enumeración con spraying.
