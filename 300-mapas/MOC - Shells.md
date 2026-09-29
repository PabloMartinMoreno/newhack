---
tipo: moc
dominio: post-explotacion
aliases:
  - MOC shells
  - MOC shells y payloads
  - Shells
tags:
  - dominio/post-explotacion
---

# MOC - Shells

> [!abstract] Dominio transversal de post-explotación
> Abrir y estabilizar un punto de apoyo interactivo tras cualquier ejecución de código — venga de web ([[MOC - Command injection]], [[MOC - File upload]]), de deserialización, de SSTI, o de una credencial a un servicio remoto. La definición paraguas está en [[T1059 - Command and Scripting Interpreter]]. Acá vive **la decisión**; la sintaxis, en las matrices.

Dos decisiones ortogonales: **cómo conecta** la shell (dirección) y **de dónde sale** el payload (origen). La herramienta y el one-liner concretos son sintaxis y viven en las matrices.

| Eje | Valores |
|---|---|
| Dirección de conexión | reverse · bind · sin socket (webshell) |
| Origen del payload | one-liner nativo (LOLBin) · binario generado (msfvenom) |
| Estructura del generado | staged · stageless |
| Interactividad | dumb shell · TTY completo (sintaxis → matriz) |
| Plataforma | Windows · Linux (sintaxis → matriz) |

## Árbol de decisión — dirección de la conexión

```
¿Cómo conecto la shell?
├─ ¿Hay egress hacia mí (443/80)?
│  └─ Sí  → [[Shell - conexión reversa]]     ← default: el egress filtra menos que el ingress
└─ No
   ├─ ¿Alcanzo un puerto entrante del objetivo? (típico ya en la red interna)
   │  └─ Sí  → [[Shell - conexión bind]]
   └─ No — no hay socket posible
      └─ ¿El objetivo ejecuta un archivo mío por HTTP? → [[Webshell]]
```

La reversa es el nodo por defecto y el bind su reverso exacto: se baja al bind solo cuando el egress está cerrado pero el ingress local no. Sin ningún socket, la salida sin conexión es el webshell —comando por petición— o seguir por el canal directo del RCE sin abrir sesión.

> [!tip] Antes de abrir cualquier socket
> Enumerar, leer config y sacar credenciales se hace por el canal directo del RCE, sin dejar la conexión que todo EDR busca. **La shell interactiva es el paso que convierte una vulnerabilidad en un incidente visible** — ver [[Command injection - a shell interactiva]]. Abrirla es una decisión, no un reflejo.

## Árbol de decisión — origen del payload

```
¿Qué payload uso?
├─ ¿Alcanza un one-liner nativo? (hay bash/python/php/powershell)
│  └─ Sí  → [[Reverse y bind shells - matriz de referencia]]  ← default: no toca disco, sin firma de herramienta
└─ No — necesito un formato (.exe/.dll/.war/.apk) o Meterpreter
   └─ [[Payload generado con msfvenom]]
      ├─ ¿egress de un solo tiro, o el tamaño no importa? → stageless (nombre con `_`)
      └─ ¿espacio limitado y egress estable?            → staged   (nombre con `/`)
```

El one-liner nativo es el default por las mismas razones que la reversa gana en dirección: menos huella, cero dependencia externa, nada en disco. El binario de msfvenom es la excepción para cuando la primitiva de entrega ejecuta un archivo, falta intérprete, o se quiere Meterpreter — y arrastra la firma de [[metasploit]], que todo AV conoce.

## Cheatsheets — entrada directa a los payloads

- [[Reverse y bind shells - matriz de referencia]] — one-liners por lenguaje y plataforma, listeners, y cuál elegir según lo que hay
- [[Estabilización de shell - matriz de referencia]] — promover una dumb shell a TTY completo
- [[msfvenom - matriz de referencia]] — payloads por plataforma/formato, staged vs stageless, encoders, multi/handler
- [[Webshells - matriz de referencia]] — el payload sin socket, cuando no hay egress ni puerto entrante

## Orden de aprendizaje

Secuencia por dependencia conceptual. Este es el temario del módulo.

1. [[T1059 - Command and Scripting Interpreter]] — qué es una shell sobre un intérprete
2. [[Shell - conexión reversa]] — el caso por defecto, fija el modelo mental
3. [[Reverse y bind shells - matriz de referencia]] — los one-liners y cuál según el objetivo
4. [[Estabilización de shell - matriz de referencia]] — hacer usable la sesión: el paso que casi todos saltan y después sufren
5. [[Shell - conexión bind]] — el reverso, para cuando el egress está cerrado
6. [[Webshell]] — el fallback sin socket
7. [[Payload generado con msfvenom]] → [[msfvenom - matriz de referencia]] — cuando el one-liner no alcanza; staged vs stageless

## Relación con otros dominios

- [[MOC - Command injection]] — la puerta más común hacia una shell; [[Command injection - a shell interactiva]] es el criterio específico de cuándo subir de comando a sesión.
- [[MOC - File upload]] y [[MOC - File inclusion]] — llegan al mismo destino por otra puerta. Los tres terminan en [[Webshell]], el nodo compartido.
- [[MOC - Transferencia de archivos]] — hermano en post-explotación: una vez con shell, traer herramientas ([[Traer herramientas al objetivo]]) y sacar datos. `nc.exe` y los binarios de msfvenom se suben por ahí.

## Huecos conocidos

- [x] Dirección: reverse, bind y webshell (este último ya existía) — cubiertas
- [x] Origen del payload: nativo (matriz) y generado (msfvenom + entidad) — cubiertos
- [x] Estabilización a TTY — matriz propia
- [ ] Pivoting y C2 — vecinos de post-explotación sin abrir; entran cuando existan como dominio.
