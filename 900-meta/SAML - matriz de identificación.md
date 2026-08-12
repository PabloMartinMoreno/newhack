---
tipo: meta
aliases:
  - decodificar SAML
  - SAMLResponse
  - identificar SAML
tags:
  - meta/referencia
  - dominio/web
---

# SAML - matriz de identificación

> [!info] Referencia pura, no un zettel
> Reconocer un flujo SAML, decodificar la aserción y saber qué campo tocar. Los patrones de envoltura están en [[SAML XSW - matriz de referencia]]; el criterio, en [[MOC - SAML]].

## 1. Reconocer que es SAML

Señales en el tráfico:

| Señal | Dónde |
|---|---|
| Parámetro `SAMLResponse` | Cuerpo de un `POST` al proveedor de servicio |
| Parámetro `SAMLRequest` | Query de la redirección al proveedor de identidad |
| `RelayState` | Acompaña a los anteriores |
| Endpoint `/saml/acs`, `/sso/saml`, `/Shibboleth.sso` | El punto de consumo |
| `urn:oasis:names:tc:SAML:2.0` | Dentro del XML decodificado |

## 2. Decodificar

**Binding POST** — base64 directo:

```sh
echo "$SAMLRESPONSE" | base64 -d | xmllint --format -
```

**Binding Redirect** — base64 + DEFLATE crudo:

```sh
echo "$SAMLREQUEST" | base64 -d | python3 -c 'import sys,zlib; sys.stdout.buffer.write(zlib.decompress(sys.stdin.buffer.read(),-15))'
```

El `-15` es lo que hace la diferencia: es DEFLATE **sin** cabecera zlib. Con el valor por defecto falla, y es el error más común al empezar.

Recodificar para el binding Redirect:

```sh
cat asercion.xml | python3 -c 'import sys,zlib,base64,urllib.parse; d=zlib.compressobj(9,zlib.DEFLATED,-15); c=d.compress(sys.stdin.buffer.read())+d.flush(); print(urllib.parse.quote(base64.b64encode(c)))'
```

Para el binding POST alcanza con `base64 -w0`.

## 3. Anatomía de la aserción

```xml
<samlp:Response>
  <saml:Issuer>https://idp.com</saml:Issuer>
  <ds:Signature>...</ds:Signature>          <!-- firma de la Response -->
  <samlp:Status>...</samlp:Status>
  <saml:Assertion ID="_abc123">
    <saml:Issuer>https://idp.com</saml:Issuer>
    <ds:Signature>...</ds:Signature>        <!-- firma de la Assertion -->
    <saml:Subject>
      <saml:NameID>usuario@objetivo.com</saml:NameID>   <!-- EL CAMPO -->
    </saml:Subject>
    <saml:Conditions NotBefore="..." NotOnOrAfter="...">
      <saml:AudienceRestriction>
        <saml:Audience>https://sp.com</saml:Audience>
      </saml:AudienceRestriction>
    </saml:Conditions>
    <saml:AttributeStatement>
      <saml:Attribute Name="role"><saml:AttributeValue>user</saml:AttributeValue></saml:Attribute>
    </saml:AttributeStatement>
  </saml:Assertion>
</samlp:Response>
```

| Elemento | Qué es | Qué se le hace |
|---|---|---|
| `NameID` | Identifica al usuario | Cambiarlo por la víctima |
| `ds:Signature` | La firma | Quitarla, envolverla, anularla |
| `ID` de la aserción | Referencia de la firma | Duplicarlo para XSW |
| `Audience` | Para qué proveedor de servicio es | Debe coincidir; si no se valida, se reutiliza la aserción de otro |
| `NotOnOrAfter` | Vencimiento | Si no se valida, se reusa una vieja |
| `AttributeStatement` | Roles y atributos | Cambiar `role` a admin |

> [!warning] Firmar la Response o la Assertion son cosas distintas
> La firma puede cubrir la `Response` entera, solo la `Assertion`, o las dos. Hay que mirar dónde está el `<Signature>` y qué `ID` referencia. Muchos ataques de envoltura dependen de que se firme una y se lea la otra.

## 4. Las cinco pruebas de apertura

Una por rama, en orden de coste.

| Prueba | Si pasa |
|---|---|
| Quitar `<Signature>`, editar `NameID`, reenviar | No verifica firma → [[SAML - firma no verificada o eliminada]] |
| Cambiar `SignatureMethod` a un algoritmo nulo | Acepta firma nula → misma nota |
| Duplicar la aserción con una falsa sin firma | Verifica una, lee otra → [[SAML - envoltura de firma XML]] |
| Entidad externa de prueba en el XML | El parser resuelve → [[SAML - XXE en el parser de la aserción]] |
| `NameID` con `<!---->` partido | Lectura y verificación difieren → [[SAML - inyección de comentarios en NameID]] |

## 5. Dónde tocar según el objetivo

```
¿Qué quiero?
├─ Entrar como la víctima
│  ├─ ¿La firma se valida? No → editar NameID, quitar firma
│  │                        Sí → envoltura, o comentario en NameID
│  └─ ¿Puedo elegir mi NameID en el IdP? → probar inyección de comentarios
├─ Escalar privilegios con mi propia cuenta
│  └─ editar AttributeStatement (role → admin), si la firma no lo cubre
├─ Reusar una aserción
│  └─ ¿Se valida Audience y NotOnOrAfter? No → sirve para otro SP o más tarde
└─ Atacar el servidor
   └─ XXE en el parser → [[MOC - XXE]]
```

## 6. Herramienta

**SAML Raider** (extensión de Burp) — decodifica, edita, aplica los ocho patrones de XSW automáticamente y gestiona certificados propios. Es lo que hace viable la rama de envoltura sin construir cada XML a mano.

`python3 -m saml2` y `xmlsec1` para trabajar la firma desde la línea de comandos.

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `zlib` falla al decodificar el Redirect | Falta el `-15`. Es DEFLATE crudo, sin cabecera |
| El SP rechaza el XML editado | Quedó mal formado. Validar con `xmllint` antes de reenviar |
| Firma inválida al quitar `<Signature>` | El SP exige que exista. Ir a envoltura |
| `Audience mismatch` | La aserción es para otro SP. Se valida el destinatario |
| `Assertion expired` | Se valida `NotOnOrAfter`. Hace falta una fresca |
| La envoltura no cambia la identidad | El patrón no coincide con cómo resuelve la referencia. Probar otro |
| El comentario no parte el NameID | La biblioteca concatena todos los nodos de texto. Rama cerrada |

## Relacionadas

[[MOC - SAML]] · [[SAML XSW - matriz de referencia]] · [[OAuth - matriz de reconocimiento]] · [[XXE payloads - matriz de referencia]]
