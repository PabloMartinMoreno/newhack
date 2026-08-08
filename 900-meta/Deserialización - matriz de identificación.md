---
tipo: meta
aliases:
  - Firmas de formato serializado
  - Identificar un blob
tags:
  - meta/referencia
  - dominio/web
---

# Deserialización - matriz de identificación

> [!info] Referencia pura, no un zettel
> El trabajo caro de este dominio es **darse cuenta de que un parámetro es un objeto serializado**. Esta matriz resuelve eso. Las cadenas están en [[Deserialización gadgets - matriz de referencia]]; el criterio, en [[MOC - Deserialización]].

## 1. Firmas de formato

Lo primero es decodificar de base64 y mirar los primeros bytes.

| Empieza con | En base64 | Formato |
|---|---|---|
| `O:` `a:` `s:` `i:` | `Tzo` `YTo` | PHP nativo |
| `AC ED 00 05` | `rO0AB` | Java nativo |
| `\x80\x04` `\x80\x03` | `gASV` `gAN` | Python `pickle` |
| `\x04\x08` | `BAh` | Ruby `Marshal` |
| `00 01 00 00 00 FF FF FF FF` | `AAEAAAD/////` | .NET `BinaryFormatter` |
| `\xFF\x01` | `/wEP` `/wEB` | ASP.NET `ViewState` |
| `PK\x03\x04` | `UEsDBA` | ZIP — puede ser `phar` o un OOXML |

Formatos de texto que también deserializan:

```
{"@type":"com.x.Y"}          fastjson / Jackson con tipado polimórfico
{"$type":"System.X, mscorlib"}  Json.NET con TypeNameHandling
{"rce":"_$$ND_FUNC$$_function(){...}"}  node-serialize
!!python/object/apply:os.system  YAML sin cargador seguro
!ruby/object:Gem::Requirement    YAML de Ruby
```

Los de texto son los más fáciles de pasar por alto: **parecen JSON normal**. La señal es un campo de tipo con un nombre de clase adentro.

## 2. Anatomía de un blob de PHP

Es el formato más editable a mano y el que más aparece.

```
O:4:"User":2:{s:4:"name";s:3:"bob";s:4:"role";s:4:"user";}
│ │  │     │ └ cantidad de propiedades
│ │  │     └ nombre de la clase
│ │  └ largo del nombre
│ └ largo
└ O = objeto, a = array, s = string, i = int, b = bool, d = float, N = null
```

Para cambiar `user` por `administrator`:

```
s:4:"role";s:4:"user"   →   s:4:"role";s:13:"administrator"
```

> [!warning] El prefijo de longitud es el error mecánico del dominio
> Cada cadena declara su largo. Editar el valor sin corregir el número rompe el blob entero y el servidor tira una excepción. Es la causa de la mayoría de los "no funciona" en [[Deserialización - manipulación de objeto]].
>
> Y ojo con las propiedades privadas y protegidas, que llevan bytes nulos en el nombre y **cuentan para el largo**: `\0Clase\0prop` y `\0*\0prop`.

## 3. Dónde aparecen

```
cookies de sesión           el caso más común
campos ocultos de formulario
parámetros y cabeceras
tokens de "recordarme"
caché y colas de mensajes
archivos subidos            OOXML, phar
operaciones de sistema de archivos   phar:// — sin llamada explícita
```

La última no tiene ninguna función que se llame "deserializar" en el código: cualquier operación sobre una ruta controlada la dispara. Ver [[LFI - phar deserialization]].

## 4. Confirmar que se deserializa

```
cambiar un byte del blob   → ¿excepción de deserialización?
truncar el blob            → ¿error distinto del de un valor inválido?
cambiar el nombre de clase → ¿"class not found"?
```

Un error que **nombre la clase o el deserializador** confirma el vector y de paso revela el marco de trabajo.

## 5. Firma

Si el blob viene acompañado de un HMAC, la vía pasa por la clave. Ver [[Deserialización - firma débil]].

Primero, lo barato: **cambiar un byte y ver si el servidor protesta**. Si no protesta, la firma se emite y no se verifica, y no hace falta ninguna clave.

Dónde vive el secreto en cada marco de trabajo:

| Marco | Variable / archivo |
|---|---|
| Laravel | `APP_KEY` en `.env` |
| Symfony | `APP_SECRET` en `.env` |
| Django | `SECRET_KEY` en `settings.py` |
| Flask | `SECRET_KEY` en la configuración |
| Rails | `secret_key_base` en `config/credentials.yml.enc` o `secrets.yml` |
| ASP.NET | `machineKey` en `web.config` |
| Express | el secreto de `cookie-session` |

Los archivos a pedir cuando hay lectura arbitraria por [[Path traversal]] o [[LFI - inclusión local]]:

```
.env
config/credentials.yml.enc     y  config/master.key
web.config
settings.py
appsettings.json
```

Y las fuentes que no son técnicas y suelen rendir más: repositorios públicos, el historial de git de un repositorio que se abrió después, imágenes de contenedor publicadas, y las claves de ejemplo de la documentación que nadie rotó.

## 6. Qué se puede hacer con cada formato

| Formato | Sin gadget | Con gadget |
|---|---|---|
| PHP | editar campos | RCE con PHPGGC |
| Java | poco: formato binario | RCE con ysoserial |
| Python `pickle` | — | **RCE directo, sin gadget** |
| Ruby `Marshal` | editar campos | RCE con cadenas universales |
| .NET | poco | RCE con ysoserial.net |
| YAML inseguro | — | **RCE directo** |
| node-serialize | — | **RCE directo** |

Las tres filas de RCE directo no necesitan que ninguna biblioteca sea vulnerable: el formato ejecuta por diseño. Si el blob es uno de esos y llega al deserializador, el trabajo está hecho.
