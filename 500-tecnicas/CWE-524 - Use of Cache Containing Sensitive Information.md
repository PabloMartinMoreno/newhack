---
tipo: tecnica
taxonomia: cwe
identificador: CWE-524
wstg: WSTG-ATHN-06
tacticas: []
aliases:
  - CWE-524
  - web cache deception
  - engaño de caché
tags:
  - dominio/web
---

# CWE-524 - Use of Cache Containing Sensitive Information

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Web cache]]; la técnica, en [[Web cache - engaño de caché]].

## Qué es

Es el reverso del envenenamiento. En vez de meter contenido malo en una entrada pública, el atacante engaña a la caché para que **guarde la respuesta privada de la víctima** —su página de cuenta, con sus datos— como si fuera un recurso público, y después la lee él mismo desde la entrada cacheada.

La víctima carga una URL preparada por el atacante; la caché, creyendo que es un recurso estático, guarda la respuesta personalizada de la víctima; el atacante pide la misma URL y recibe la copia con los datos de la víctima adentro.

## Por qué es el opuesto del envenenamiento

Los dos viven en la caché y van en direcciones contrarias, igual que [[MOC - CSRF]] y [[MOC - CORS]]:

| | Envenenamiento (CWE-349) | Engaño (CWE-524) |
|---|---|---|
| Dirección | Empuja contenido malo **hacia** todos | Roba contenido privado **desde** la víctima |
| Qué se cachea | La respuesta del atacante | La respuesta de la víctima |
| Quién sufre | Todos los usuarios | La víctima concreta |
| El fallo | Entrada sin clave influye en la respuesta | La caché guarda algo que era privado |

Entenderlos como opuestos es lo que ordena el dominio: comparten la capa y no comparten casi nada más.

## Por qué la caché se equivoca

La caché decide qué guardar por reglas simples —a menudo la extensión de la URL o un prefijo de ruta—: "todo lo que termine en `.css` o `.js` es estático, guardalo". El atacante abusa la diferencia entre **cómo la caché interpreta la URL** y **cómo la interpreta el servidor de aplicación**:

- `cuenta.php/inexistente.css` — la caché ve `.css` y guarda; el servidor ignora el sufijo y sirve la página de cuenta.
- `cuenta.php%00.css`, `cuenta.php;.css`, `cuenta.php#.css` — variantes de confusión de ruta, según qué delimitador corte cada capa.

Es la misma clase de discrepancia entre dos parsers que [[MOC - Request smuggling]], aplicada a la ruta en vez de al largo del cuerpo.

## Por qué la mitigación es de coherencia

- Cachear por el **`Content-Type` real** de la respuesta, no por la extensión de la URL.
- No servir contenido dinámico bajo rutas que la caché trata como estáticas.
- Que la caché y el servidor **normalicen la ruta igual**, o que la caché respete las cabeceras `Cache-Control` de la respuesta en vez de decidir por la URL.

## Referencias canónicas

- [CWE-524](https://cwe.mitre.org/data/definitions/524.html)
- WSTG-ATHN-06
- OWASP — Web Cache Deception
