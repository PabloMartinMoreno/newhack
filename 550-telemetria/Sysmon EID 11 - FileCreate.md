---
tipo: telemetria
plataforma: [windows]
producto: Sysmon
identificador: "EID 11"
por-defecto: false
coste: alto
aliases:
  - creación de archivo Sysmon
  - FileCreate
tags:
  - plataforma/windows
---

# Sysmon EID 11 - FileCreate

## Qué lo genera

Creación o sobrescritura de un archivo, con **el proceso que lo escribió**.

Es el equivalente en Windows de [[Escritura de archivo en la raíz web]], y comparte su virtud: es un artefacto de **efecto**. Muchas técnicas distintas convergen en dejar un archivo donde no debería haberlo, y una sola condición las alcanza a todas.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `Image` | Proceso que escribió | **La clave**: un documento de oficina escribiendo un ejecutable |
| `TargetFilename` | Ruta completa | Dónde cayó |
| `ProcessGuid` | Identificador del proceso | Une con la creación del proceso |
| `CreationUtcTime` | Marca temporal | Detecta manipulación de fechas si se compara con la del sistema de archivos |

Las combinaciones que valen: proceso de ofimática o navegador escribiendo un ejecutable o un script; cualquier cosa escribiendo en las carpetas de inicio automático; un ejecutable apareciendo en carpetas temporales o de perfil de usuario.

## Coste de recolección

Alto sin filtros — el sistema escribe archivos todo el tiempo. Se domina por **extensión y por ruta**: registrar solo lo ejecutable y lo interpretable, y solo en las ubicaciones que importan.

## Cómo se activa

Sección correspondiente de la configuración de Sysmon. Complementa con el evento de creación de flujo de datos alternativo, que es el que delata la marca de procedencia de internet — útil para saber si un archivo vino de una descarga.

## Limitaciones

- **No ve modificaciones de archivos existentes**, solo creación y sobrescritura. Un atacante que altera un archivo legítimo ya presente pasa por debajo.
- **No ve el contenido.** El nombre y la ruta son todo lo que hay.
- **Volumen.** Sin filtros, es de las fuentes más ruidosas.
- **Los procesos legítimos escriben en todas partes** — instaladores, actualizadores, cachés. La lista de exclusión es específica de cada entorno.
- **Un archivo borrado enseguida deja el evento pero no el archivo.** Bueno para detectar, incómodo para responder.

## Quién lo emite / quién lo consume

Rojo: pendiente — ver [[MOC - Telemetría de Windows]]
Azul: pendiente
