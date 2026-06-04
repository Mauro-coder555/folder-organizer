# Folder Organizer

Aplicación local creada en Python para ayudar a personas no técnicas a ordenar carpetas desorganizadas de forma simple, visual y segura.

Folder Organizer analiza los archivos de una carpeta, propone una clasificación automática, muestra una vista previa de los movimientos y solo mueve archivos cuando el usuario lo confirma explícitamente.

---

## Índice

* [Problema que resuelve](#problema-que-resuelve)
* [Para quién es útil](#para-quién-es-útil)
* [Características principales](#características-principales)
* [Herramientas utilizadas](#herramientas-utilizadas)
* [Cómo instalarlo](#cómo-instalarlo)
* [Cómo ejecutarlo](#cómo-ejecutarlo)
* [Cómo usarlo paso a paso](#cómo-usarlo-paso-a-paso)
* [Cómo funciona internamente](#cómo-funciona-internamente)
* [Estructura de carpetas](#estructura-de-carpetas)
* [Categorías disponibles](#categorías-disponibles)
* [Ejemplos de uso](#ejemplos-de-uso)
* [Seguridad y rollback](#seguridad-y-rollback)
* [Resumen Markdown de operaciones](#resumen-markdown-de-operaciones)
* [Tests](#tests)
* [Limitaciones actuales](#limitaciones-actuales)
* [Posibles mejoras futuras](#posibles-mejoras-futuras)
* [Estado del proyecto](#estado-del-proyecto)

---

## Problema que resuelve

Muchas personas tienen carpetas llenas de archivos mezclados: facturas, contratos, imágenes, capturas de pantalla, documentos, videos, archivos comprimidos y otros elementos sin orden claro.

Ordenar todo manualmente puede ser lento, repetitivo y riesgoso, especialmente si el usuario no tiene conocimientos técnicos o si la carpeta tiene muchos archivos.

Folder Organizer ayuda a resolver ese problema proponiendo una organización automática, pero sin mover nada hasta que el usuario revise y apruebe los cambios.

---

## Para quién es útil

Este proyecto está pensado para:

* Personas no técnicas que quieren ordenar carpetas sin usar herramientas complejas.
* Usuarios que tienen carpetas de descargas desorganizadas.
* Personas que trabajan con facturas, contratos, reportes o documentos mezclados.
* Usuarios que quieren una aplicación local, simple y segura.
* Personas que prefieren revisar antes de aplicar cambios en sus archivos.

---

## Características principales

* Selección visual de carpeta local.
* Escaneo de archivos dentro de la carpeta seleccionada.
* Clasificación automática por extensión y palabras clave en el nombre.
* Vista previa de movimientos propuestos.
* Aprobación individual de archivos con una interfaz tipo checkbox.
* Movimiento seguro solo de archivos aprobados.
* Creación automática de carpetas por categoría.
* Registro local de operaciones en JSON.
* Exportación de resumen de operación en Markdown.
* Opción para deshacer la última operación.
* Interfaz gráfica simple con Tkinter.
* Sin login.
* Sin nube.
* Sin dependencias externas en la primera versión.

---

## Herramientas utilizadas

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge\&logo=python)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green?style=for-the-badge)
![Local First](https://img.shields.io/badge/Local--First-Yes-orange?style=for-the-badge)
![No Cloud](https://img.shields.io/badge/Cloud-No-lightgrey?style=for-the-badge)
![Safe Preview](https://img.shields.io/badge/Safe--Preview-Enabled-brightgreen?style=for-the-badge)
![Rollback](https://img.shields.io/badge/Rollback-Enabled-purple?style=for-the-badge)

---

## Cómo instalarlo

Cloná o descargá el proyecto en tu computadora.

No es obligatorio crear un entorno virtual ni instalar dependencias externas para la primera versión.

Tkinter, unittest, pathlib, shutil, json y dataclasses vienen incluidos con Python.

Verificá que Python esté instalado ejecutando:

```bash
python --version
```

Si Python está instalado correctamente, deberías ver una versión similar a:

```bash
Python 3.x.x
```

---

## Cómo ejecutarlo

Desde la raíz del proyecto, ejecutá:

```bash
python main.py
```

Esto abrirá la interfaz gráfica de Folder Organizer.

---

## Cómo usarlo paso a paso

1. Abrí la aplicación con:

```bash
python main.py
```

2. Hacé click en:

```text
📁 Select folder
```

3. Seleccioná la carpeta que querés organizar.

4. Hacé click en:

```text
🔍 Scan folder
```

5. Revisá la tabla de vista previa.

6. Cada archivo aparecerá con una acción:

```text
☑ Move
```

o

```text
☐ Skip
```

7. Para cambiar si un archivo se moverá o no, seleccioná la fila y usá el botón:

```text
☑/☐ Change selected
```

También podés usar doble click sobre una fila.

8. Cuando estés conforme, hacé click en:

```text
Apply approved movements
```

9. Confirmá la operación.

10. La aplicación moverá únicamente los archivos aprobados.

11. Se guardará automáticamente:

```text
un log JSON de la operación
un resumen Markdown de la operación
```

12. Si necesitás revertir la última organización, usá:

```text
Undo last operation
```

---

## Cómo funciona internamente

Folder Organizer sigue un flujo seguro:

```text
scan folder
↓
build file items
↓
classify files
↓
create move plans
↓
show preview
↓
user approves or skips files
↓
apply only approved movements
↓
save operation log
↓
export Markdown summary
↓
allow rollback
```

La aplicación separa responsabilidades en módulos simples.

### Scanner

Escanea los archivos directos dentro de una carpeta.

No mueve archivos.

### Classifier

Propone una categoría según:

* extensión del archivo;
* palabras clave en el nombre;
* reglas simples definidas en configuración.

### Planner

Construye una propuesta de movimiento.

Ejemplo:

```text
sample_files/invoice_january.pdf
```

puede convertirse en:

```text
sample_files/invoices/invoice_january.pdf
```

### GUI

Muestra una tabla visual para que el usuario revise la propuesta.

Permite marcar archivos como:

```text
☑ Move
```

o:

```text
☐ Skip
```

### Organizer

Mueve únicamente archivos aprobados.

También evita sobrescribir archivos existentes.

### Log Repository

Guarda un archivo JSON por operación.

### Markdown Exporter

Genera un resumen en Markdown con los archivos movidos, sus categorías y sus rutas originales y finales.

### Rollback Manager

Lee el último log y restaura los archivos movidos a su ubicación original.

---

## Estructura de carpetas

```text
folder-organizer/
│
├── README.md
├── requirements.txt
├── .gitignore
├── main.py
│
├── app/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scanner.py
│   │   ├── classifier.py
│   │   ├── planner.py
│   │   ├── organizer.py
│   │   ├── rollback.py
│   │   └── summary.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── file_item.py
│   │   ├── move_plan.py
│   │   └── operation_log.py
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── log_repository.py
│   │   └── markdown_exporter.py
│   │
│   ├── gui/
│   │   ├── __init__.py
│   │   └── main_window.py
│   │
│   └── config/
│       ├── __init__.py
│       ├── categories.py
│       └── rules.py
│
├── data/
│   ├── logs/
│   └── summaries/
│
├── sample_files/
│
└── tests/
    ├── __init__.py
    └── test_app.py
```

---

## Categorías disponibles

La aplicación propone estas categorías:

```text
invoices
contracts
reports
screenshots
images
videos
documents
spreadsheets
archives
others
```

---

## Ejemplos de uso

### Ejemplo 1

Archivo original:

```text
invoice_january.pdf
```

Categoría sugerida:

```text
invoices
```

Destino propuesto:

```text
invoices/invoice_january.pdf
```

---

### Ejemplo 2

Archivo original:

```text
contract_client_acme.docx
```

Categoría sugerida:

```text
contracts
```

Destino propuesto:

```text
contracts/contract_client_acme.docx
```

---

### Ejemplo 3

Archivo original:

```text
screenshot_2026_06_04.png
```

Categoría sugerida:

```text
screenshots
```

Destino propuesto:

```text
screenshots/screenshot_2026_06_04.png
```

---

### Ejemplo 4

Archivo original:

```text
random_file.bin
```

Categoría sugerida:

```text
others
```

Destino propuesto:

```text
others/random_file.bin
```

---

## Seguridad y rollback

Folder Organizer está diseñado para evitar operaciones riesgosas.

Reglas principales:

* No mueve archivos durante el escaneo.
* No mueve archivos durante la vista previa.
* Solo mueve archivos cuando el usuario confirma explícitamente.
* Solo mueve archivos marcados como `☑ Move`.
* No mueve archivos marcados como `☐ Skip`.
* No sobrescribe archivos existentes.
* Si existe un archivo con el mismo nombre en destino, crea un nombre alternativo.
* Guarda un log JSON de cada operación.
* Permite deshacer la última operación usando el último log disponible.

Ejemplo de renombrado seguro:

```text
invoice_january.pdf
invoice_january_1.pdf
```

El rollback intenta mover cada archivo organizado de vuelta a su ubicación original.

Por seguridad, actualmente no elimina carpetas vacías después de restaurar archivos.

---

## Resumen Markdown de operaciones

Después de aplicar una organización, la aplicación genera automáticamente un resumen en Markdown dentro de:

```text
data/summaries/
```

El resumen incluye:

* ID de operación.
* Fecha y hora.
* Carpeta organizada.
* Cantidad de archivos movidos.
* Tabla con archivos movidos.
* Categoría asignada.
* Ruta original.
* Ruta final.
* Notas de seguridad.

Ejemplo de archivo generado:

```text
summary_operation_20260604_153000_ab12cd34.md
```

---

## Tests

El proyecto usa `unittest`, incluido en Python.

Para correr los tests:

```bash
python -m unittest tests/test_app.py
```

Resultado esperado:

```text
OK
```

---

## Limitaciones actuales

La primera versión tiene algunas limitaciones intencionales para mantener el proyecto simple:

* No analiza contenido interno con IA.
* No usa OCR para leer texto dentro de imágenes.
* No analiza profundamente PDFs.
* No escanea carpetas internas de forma recursiva.
* No borra carpetas vacías luego de hacer rollback.
* No tiene configuración avanzada desde la interfaz.
* La clasificación depende principalmente del nombre y la extensión del archivo.
* El resumen Markdown se exporta automáticamente, pero todavía no tiene una pantalla dedicada dentro de la GUI.

---

## Posibles mejoras futuras

Algunas mejoras posibles para próximas versiones:

* Agregar análisis profundo opcional para archivos de baja confianza.
* Usar OCR para distinguir facturas escaneadas de imágenes comunes.
* Analizar texto de PDFs.
* Agregar IA opcional para clasificar archivos difíciles.
* Permitir reglas personalizadas por el usuario.
* Agregar escaneo recursivo de subcarpetas.
* Mostrar detalles ampliados de cada archivo.
* Permitir editar la categoría sugerida antes de mover.
* Agregar limpieza opcional de carpetas vacías después del rollback.
* Agregar historial visual de operaciones.
* Agregar botón para abrir el último resumen Markdown.
* Empaquetar la aplicación como ejecutable para Windows.

---

## Estado del proyecto

Estado actual:

```text
MVP funcional
```

Incluye:

```text
GUI
scanner
classifier
preview
manual approval
safe movement
JSON logs
Markdown summaries
rollback
tests
```

El proyecto prioriza seguridad, simpleza y uso local.
