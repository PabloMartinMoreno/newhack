---
tipo: tecnica
taxonomia: cwe
identificador: CWE-287
wstg: [WSTG-ATHN-01, WSTG-ATHN-02, WSTG-ATHN-03]
tacticas: []
aliases:
  - CWE-287
  - Improper authentication
  - Autenticación defectuosa
tags:
  - dominio/web
---

# CWE-287 - Improper Authentication

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Autenticación]]; la variante, en [[Autenticación - bypass de segundo factor]].

## Qué es

La aplicación cree haber verificado la identidad de quien pide algo, y no la verificó. Es la CWE más general del dominio: cubre todo fallo del mecanismo en sí, a diferencia de [[CWE-307 - Improper Restriction of Excessive Authentication Attempts]], que es sobre el ritmo, y de [[CWE-204 - Observable Response Discrepancy]], que es sobre lo que se filtra.

## Dónde falla en la práctica

El caso que domina los informes reales es el **segundo factor mal integrado**, y el patrón se repite con pocas variaciones: la aplicación trata la verificación del segundo factor como un paso de la interfaz en lugar de como una condición para emitir la sesión.

Las tres formas concretas:

- **La sesión se emite antes de verificar el segundo factor.** El primer paso ya entrega una cookie válida, y el segundo solo decide a qué pantalla se redirige. Saltar la redirección basta.
- **El paso siguiente no verifica que el anterior se completó.** Es el mismo fallo estructural que [[Control de acceso - salto de contexto]], aplicado al flujo de acceso.
- **El código es verificable sin límite.** Seis dígitos son un millón de combinaciones, que sin control de ritmo se agotan en minutos. Cuando el código además es de cuatro dígitos o vive mucho tiempo, es cuestión de segundos.

## El caso que no es un fallo de código

Los **mecanismos alternativos** son la puerta de atrás del dominio. Una aplicación con MFA impecable en su formulario web que además expone una API, un cliente móvil o un protocolo heredado sin MFA no tiene MFA: tiene MFA en un camino.

Lo mismo vale para los códigos de respaldo y para la recuperación de cuenta, que por diseño existen para **evitar** el segundo factor. Ver [[CWE-640 - Weak Password Recovery Mechanism for Forgotten Password]].

Buscar el camino sin MFA suele rendir más que atacar el MFA.

## La mitigación real

Que la sesión autenticada **no exista** hasta que todos los factores estén verificados. El estado intermedio tiene que ser un token de un solo uso, de vida corta, que no sirva para nada más que completar el segundo paso.

Y: inventariar todos los caminos de acceso, no solo el principal.

## Referencias canónicas

- [CWE-287](https://cwe.mitre.org/data/definitions/287.html)
- [CWE-1390](https://cwe.mitre.org/data/definitions/1390.html) — Weak Authentication
- WSTG-ATHN-01, WSTG-ATHN-02, WSTG-ATHN-03
