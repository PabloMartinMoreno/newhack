---
tipo: moc
dominio: fase
aliases:
  - MOC explotación
  - Explotación
tags:
  - fase
---

# MOC - Explotación

> [!abstract] Fase del engagement
> Conseguir ejecución o acceso no autorizado, una vez mapeada la superficie en [[MOC - Reconocimiento]]. Enruta **por superficie** a los mapas de dominio, que siguen existiendo como vista propia. Lo que sigue a la ejecución, en [[MOC - Post-explotación]].

Esta fase no tiene técnica propia: es el **triage por superficie**. El nodo raíz es qué tenés delante; a partir de ahí se entra al mapa del dominio, que ordena internamente por su propio eje (web por mecanismo, AD por lo que tenés).

## Árbol de decisión — ¿qué superficie exploto?

```
¿Qué tipo de objetivo tengo delante?
├─ Aplicación web
│  └─ [[MOC - Explotación web]]   ← enruta por dónde falla la app (las seis familias)
└─ Active Directory
   ├─ Sin credencial (solo red)
   │  ├─ Responder a la escucha            → [[MOC - AD envenenamiento y relay]]
   │  └─ Cuentas sin preautenticación       → AS-REP roasting, en [[MOC - AD roasting]]
   ├─ Con una credencial de dominio
   │  ├─ Cuentas de servicio con SPN        → Kerberoasting, en [[MOC - AD roasting]]
   │  └─ PKI mal configurada                 → [[MOC - ADCS]]
   └─ La cadena completa, contada entera     → [[MOC - Active Directory]]
```

La enumeración de AD **no** vive acá: es reconocimiento ([[MOC - AD enumeración]] en [[MOC - Reconocimiento]]). Acá vive lo que se hace con lo que la enumeración encontró: romper, relayar, abusar la PKI.

## Adónde enruta

- **Web** — [[MOC - Explotación web]], hub por mecanismo (inyección, identidad, el servidor trae/incluye, cliente, discrepancia de parseo, lógica).
- **Active Directory** — la parte de acceso/escalada de la cadena: [[MOC - AD envenenamiento y relay]], [[MOC - AD roasting]], [[MOC - ADCS]]. La kill-chain entera, como historia única, en [[MOC - Active Directory]].

Un mismo dominio puede aparecer en más de una fase (es una vista, no un contenedor): AD también figura en [[MOC - Reconocimiento]] (enumeración), [[MOC - Post-explotación]] (volcado de credenciales), [[MOC - Movimiento lateral]] y [[MOC - Persistencia]].

## Relación con otras fases

- **Antes:** [[MOC - Reconocimiento]] mapea la superficie; [[MOC - Pre-explotación]] deja listo el arsenal (shell/payload) que esta fase entrega.
- **Después:** [[MOC - Post-explotación]] — con ejecución en mano; de ahí a [[MOC - Movimiento lateral]] y [[MOC - Persistencia]].

## Huecos conocidos

- [x] Enruta las dos superficies con contenido: web (hub por mecanismo) y AD (acceso/escalada).
- [ ] **Acceso inicial del lado cliente** — macros de Office, archivos LNK/iCal/JScript maliciosos, DLL hijacking por archivo. Es la rama "client-side" del ejemplo; sin dominio propio.
- [ ] **Explotación de servicios** — SSH, MSSQL (`xp_cmdshell`), RDP como vía de ejecución. Hoy vive dentro de cada matriz de [[MOC - Servicios de red]]; podría agruparse acá como rama propia.
- [ ] Otras superficies sin abrir (cloud, móvil, Wi-Fi): entran acá cuando existan como dominio.
