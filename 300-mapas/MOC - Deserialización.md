---
tipo: moc
dominio: web
aliases:
  - MOC deserialización
  - Deserialización
tags:
  - dominio/web
---

# MOC - Deserialización

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-502 - Deserialization of Untrusted Data]]. Identificar el formato, en [[Deserialización - matriz de identificación]]. Acá vive **la decisión**.

Este dominio tiene fama de ser sobre ejecución remota, y esa fama hace perder tiempo. **La rama que más veces resuelve el caso no necesita ninguna cadena de gadgets**: alcanza con editar los campos del objeto. El árbol está ordenado para llegar a eso primero.

| Eje | Valores |
|---|---|
| Impacto | manipulación de objeto · RCE por cadena · SSRF o lectura · DoS |
| Obstáculo | firma HMAC · lista blanca de clases · sin cadena disponible |
| Formato | PHP · Java · Python · Ruby · .NET · JSON con tipado → matriz |
| Vector | cookie · parámetro · cabecera · archivo · operación de sistema de archivos |

El **formato va a matriz y no a eje**, mismo criterio que el motor en [[MOC - SQL injection]] y la shell en [[MOC - Command injection]]: cambia la sintaxis, las cadenas y la herramienta, no cambia ninguna decisión. Lo que decide es si hay gadget, si hay firma, y si alcanza con manipular sin ejecutar.

## Árbol de decisión

```
¿Esto es un blob serializado?     → [[Deserialización - matriz de identificación]] § 1
└─ Sí
   ├─ ¿Está firmado?
   │  ├─ Sí → cambiá un byte: ¿protesta?
   │  │      ├─ No  → la firma no se verifica: seguí como si no la hubiera
   │  │      └─ Sí  → [[Deserialización - firma débil]]
   │  └─ No → seguí
   ├─ ¿El objeto tiene algún campo que gobierne privilegios o estado?
   │  └─ Sí → [[Deserialización - manipulación de objeto]]   ← probá esto PRIMERO
   └─ ¿Necesitás ejecución?
      ├─ ¿El formato ejecuta por diseño? (pickle, YAML, node-serialize)
      │  └─ Sí → ejecución directa, sin gadget
      └─ ¿Hay cadena para las bibliotecas cargadas?
         └─ [[Deserialización - cadena de gadgets]]
```

Tres cosas que este orden codifica:

**La firma se prueba antes de atacarla.** Que el blob venga firmado no implica que la firma se verifique. Se emite al salir y nadie comprueba al entrar: pasa seguido y cuesta una petición descubrirlo.

**Manipular va antes que ejecutar.** Un objeto de sesión con un campo de rol adentro es escalada completa sin necesitar ni una biblioteca vulnerable. Se pasa por alto porque el dominio "es sobre RCE".

**Tres formatos ejecutan por diseño.** `pickle`, YAML con cargador inseguro y `node-serialize` no necesitan que nada sea vulnerable. Si el blob es uno de esos y llega al deserializador, el trabajo está hecho — y buscar cadenas ahí es perder el tiempo.

## Árbol de decisión — confirmar antes de romper

```
¿Confirmaste que se deserializa?
├─ Cambiar un byte     → ¿excepción de deserialización?
├─ Nombre de clase falso → ¿"class not found"?
└─ Java: cadena URLDNS → ¿llega la consulta DNS?
```

`URLDNS` no ejecuta nada: solo dispara una resolución. Es la confirmación correcta en Java porque **no toca el estado del proceso**. Ver el límite operativo de [[Deserialización - cadena de gadgets]]: una cadena a medio ejecutar puede tirar el trabajador, y confirmar y ejecutar tienen que ser dos pasos.

## Cheatsheets

- [[Deserialización - matriz de identificación]] — Firmas de formato, anatomía del blob de PHP, dónde aparecen, secretos por marco de trabajo
- [[Deserialización gadgets - matriz de referencia]] — Enumerar dependencias, `ysoserial`, `PHPGGC`, `pickle`, `ysoserial.net`, orden de trabajo

## Orden de aprendizaje

1. [[CWE-502 - Deserialization of Untrusted Data]] — por qué reconstruir no es leer
2. [[Deserialización - matriz de identificación]] — reconocer un blob, que es el trabajo caro
3. [[Deserialización - manipulación de objeto]] — la rama barata, y la que más veces alcanza
4. [[Deserialización - firma débil]] — el obstáculo real en producción
5. [[Deserialización - cadena de gadgets]] — la que le dio fama al dominio, al final
6. [[LFI - phar deserialization]] — el vector sin llamada explícita

El punto 5 va último a propósito, al revés de como suele enseñarse. Empezar por `ysoserial` deja la impresión de que sin cadena no hay dominio, que es falso y hace descartar casos explotables.

## Relación con otros dominios

- [[MOC - File inclusion]] — [[LFI - phar deserialization]] llega acá desde allá: cualquier operación de sistema de archivos sobre una ruta controlada dispara deserialización, **sin que exista una sola llamada a deserializar en el código**. Es el vector más difícil de auditar del dominio.
- [[MOC - Broken access control]] — [[Deserialización - manipulación de objeto]] es [[Control de acceso - mass assignment]] por otro medio: un campo que gobierna privilegios, escribible por quien no debería. La detección es la misma.
- [[MOC - File upload]] — OOXML y `phar` llegan por subida de archivos.
- [[Path traversal]] y [[XXE - canal directo]] — leer el archivo de configuración es lo que convierte una lectura arbitraria en la clave de firma, y con ella en ejecución. Ver [[Deserialización - firma débil]].

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Manipulación de objeto | [[Log de auditoría de la aplicación]] | Privilegio cambiado fuera del flujo administrativo |
| Cadena de gadgets | [[Proceso hijo del servidor web]] | El gadget final ejecuta: lo ve la detección de efecto |
| Cadena de gadgets | [[Conexión saliente del servidor de aplicación]] | Búsqueda remota de clase o resolución del gadget |
| Intentos fallidos | [[Log de errores del servidor web]] | Ráfaga de excepciones de deserialización |
| Firma débil | — | **Nada**: la fuerza bruta de la clave es fuera de línea |

Dos observaciones que este dominio deja claras:

**Ninguna detección propia hizo falta.** Es el segundo dominio que se cierra reutilizando artefactos y reglas existentes: [[Intérprete de comandos como hijo del servidor web]] lo detecta sin saber que hubo deserialización de por medio, y [[Cambio de privilegio fuera del flujo administrativo]] cubre la manipulación. Es la mejor evidencia de que detectar efecto en vez de firma paga.

**Lo fallido es más visible que lo exitoso.** Una cadena que no funciona lanza una excepción; la que funciona, no. Una ráfaga de excepciones de deserialización en [[Log de errores del servidor web]] es reconocimiento en curso, y suele **preceder** al intento que sale bien. Es la ventana de detección real del dominio.

## Huecos conocidos

- [x] Las tres ramas: manipular, firmar, ejecutar
- [x] Formatos e identificación — en [[Deserialización - matriz de identificación]]
- [x] Cadenas por lenguaje — en [[Deserialización gadgets - matriz de referencia]]
- [x] Cara azul — cubierta por detecciones existentes, sin reglas nuevas
- [ ] **`CWE-1321` — contaminación de prototipos.** Es deserialización-adyacente en JavaScript y tiene ejes propios: fuentes de contaminación, gadgets del lado del cliente y del servidor. Dominio aparte, sin modelar
- [ ] Cadenas de gadgets propias de la aplicación, cuando no hay ninguna publicada
