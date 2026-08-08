---
tipo: deteccion
tecnicas: ["[[CWE-918 - Server-Side Request Forgery]]"]
telemetria: ["[[Conexión saliente del servidor de aplicación]]"]
forma: evento
ventana: 
estado: idea
fidelidad: alta
logica: sigma
validada: 
aliases:
  - acceso a IMDS
tags:
  - dominio/web
---

# Petición al servicio de metadatos de instancia

## Qué detecta

Conexión desde el proceso de la aplicación hacia la dirección de enlace local del servicio de metadatos de la nube.

Es la detección de mayor fidelidad de todo el lado web del vault, y el motivo es de comportamiento, no técnico: **una aplicación consulta metadatos al arrancar, no en medio de una petición de usuario**, y prácticamente nunca consulta las rutas de credenciales.

## Lógica

```yaml
detection:
  selection:
    DestinationIp:
      - '169.254.169.254'
      - '100.100.100.200'
      - '192.0.0.192'
    SourceImage|endswith:
      - '/php-fpm'
      - '/node'
      - '/java'
      - '/python3'
      - '\w3wp.exe'
  condition: selection
```

Con proxy de egress que registre la URL, el refuerzo de alta fidelidad es la ruta: cualquier cosa bajo `iam/security-credentials`, `service-accounts/*/token` o `metadata/identity/oauth2/token` es robo de credenciales, no reconocimiento.

Segunda mitad, del lado de la nube y más valiosa aún: **credenciales de instancia usadas desde una IP que no es la de la instancia**. Eso ya no es una petición sospechosa, es la prueba de que las credenciales salieron. Vive en el registro de auditoría del proveedor, no acá.

## Falsos positivos conocidos

- **Agentes legítimos** —el agente del proveedor, herramientas de inventario, bibliotecas de SDK— consultan metadatos con normalidad. Se separan por proceso de origen: el filtro de imagen de arriba es lo que hace usable la regla.
- **La aplicación consulta metadatos al arrancar** para descubrir su región o su rol. Se distingue por momento: al inicio del proceso, no durante una petición.
- **Bibliotecas de nube dentro de la propia aplicación** que renuevan credenciales solas. Es el falso positivo difícil, y se resuelve por ruta y por frecuencia: la renovación es periódica y predecible.

## Evasiones conocidas

- **IMDSv2 no la evade**, la vuelve innecesaria: si el token es obligatorio, [[SSRF - metadatos de instancia cloud]] no funciona y no hay nada que detectar.
- **Formas alternativas de escribir la dirección** — decimal, octal, IPv6 — no evaden esta regla si se filtra por la IP **resuelta** en el flujo de red, que es lo que ve el artefacto. Sí evaden cualquier regla puesta sobre el texto de la URL, que es la razón para no ponerla ahí.
- **Redirección** hacia el servicio desde un dominio externo: la conexión final sigue siendo a la misma IP.

## Cómo se prueba

Disparador: [[SSRF - metadatos de instancia cloud]] contra una instancia de laboratorio con IMDSv1 habilitado. Un disparo la valida.
