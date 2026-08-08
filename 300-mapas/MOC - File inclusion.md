---
tipo: moc
dominio: web
aliases:
  - MOC LFI
  - MOC RFI
  - File inclusion
tags:
  - dominio/web
---

# MOC - File inclusion

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-98 - File Inclusion]]. Acá vive **la decisión**. Se encadena con [[MOC - File upload]].

Intersección de ejes ortogonales. Una nota por valor de eje.

| Eje | Valores |
|---|---|
| Tipo | path traversal (lee) · LFI (incluye/ejecuta) · RFI (incluye remoto) |
| Wrapper PHP | `php://filter` · `php://input` · `data://` · `expect://` · `zip://` · `phar://` |
| Vía a RCE | log poisoning · session · `/proc/self/environ` · filter chains · wrapper |
| Obstáculo | filtro de `../` · extensión forzada · null byte · `allow_url_include` off |

## Árbol de decisión — qué puedo hacer

```
¿La app incluye/ejecuta la ruta, o solo la lee?
├─ Solo lee (file_get_contents, readfile) → path traversal → [[Path traversal - matriz de referencia]]
└─ Incluye/ejecuta (include, require)
   ├─ ¿Puedo apuntar a una URL remota?  → RFI → [[RFI - inclusión remota]]  (allow_url_include=On)
   └─ Solo local                        → LFI → [[LFI - inclusión local]]
      └─ ¿Quiero solo leer, o ejecutar?
         ├─ leer   → wrappers de lectura → [[LFI wrappers - matriz de referencia]]
         └─ ejecutar → [[LFI - de lectura a RCE]] → [[LFI a RCE - matriz de referencia]]
```

## Árbol de decisión — obstáculos

```
¿Qué te bloquea?
├─ Filtran ../           → encoding / anidado / absoluto → [[Path traversal - matriz de referencia]] § bypass
├─ Fuerzan extensión     → wrapper php://filter / null byte (PHP<5.3) → [[LFI wrappers - matriz de referencia]]
└─ allow_url_include Off → no hay RFI: quedás en LFI → RCE local
```

## Cheatsheets — entrada directa a los payloads

| Matriz | Cubre |
|---|---|
| [[Path traversal - matriz de referencia]] | `../`, encodings, null byte, path absoluto, bypass de filtros |
| [[LFI wrappers - matriz de referencia]] | `php://filter` (lectura + filter chains RCE), `data://`, `php://input`, `expect://`, `zip://`, `phar://` |
| [[LFI a RCE - matriz de referencia]] | log/session/environ poisoning, `/proc/self/fd`, phpinfo race |

## Orden de aprendizaje

1. [[CWE-98 - File Inclusion]] — qué es y la diferencia leer vs ejecutar
2. [[Path traversal - matriz de referencia]] — leer archivos, la base
3. [[LFI - inclusión local]] — cuando include ejecuta lo que lee
4. [[LFI wrappers - matriz de referencia]] — leer fuente con `php://filter`, ejecutar con wrappers
5. [[LFI - de lectura a RCE]] → [[LFI a RCE - matriz de referencia]] — las vías de escalada
6. [[RFI - inclusión remota]] — el caso fácil, cuando `allow_url_include` está On
7. El combo con upload: [[MOC - File upload]]

## Relación con otros dominios

- [[MOC - File upload]] — el combo [[File upload + LFI]] es el nodo que une ambos.
- [[MOC - SSRF]] — **[[RFI - inclusión remota]] es un SSRF** cuyo resultado, además de traerse, se ejecuta. La diferencia está en qué hace la app con la respuesta, no en la petición. Si `allow_url_include` está Off pero la app igual trae la URL, sigue habiendo SSRF aunque no haya RFI: ahí el dominio cambia, no el hallazgo.

## Cara azul

| Tipo | Telemetría | Firma |
|---|---|---|
| Traversal / LFI | [[Log de acceso del servidor web]] | `../`, `%2e%2e`, `php://filter`, `/etc/passwd`, `/proc/self` en parámetros |
| RFI | [[Log de acceso del servidor web]] | Parámetro con `http://`/`ftp://` externo; + [[Consulta DNS saliente]] al incluir |

## Huecos conocidos

- [x] Los tres tipos + wrappers + vías a RCE
- [x] `phar://` deserialization — [[LFI - phar deserialization]]. La `clase:` de esa nota es [[CWE-502 - Deserialization of Untrusted Data]], no `CWE-98`: acá el wrapper es el **vector**, la vulnerabilidad es la deserialización. Este MOC la sigue indexando porque se llega por acá
- [ ] El dominio de deserialización en sí — `CWE-502` existe como nota paraguas y no tiene MOC propio todavía
- [x] Combo LFI + upload — [[File upload + LFI]]
