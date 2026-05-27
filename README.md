🔺 KarionIDE v1.0 (beta)

[![Estado](https://img.shields.io/badge/estado-beta-orange?style=flat-square)](https://github.com/Roussel19/karionideof)
[![Plataforma](https://img.shields.io/badge/plataforma-Windows%20solo-blue?style=flat-square)](https://www.microsoft.com/windows)
[![Licencia](https://img.shields.io/badge/licencia-MIT-green?style=flat-square)](LICENSE)

> Un editor de código humilde, oscuro y con alma de principiante.  
> **Hecho para PCs de bajos recursos, por curiosidad y ganas de aprender.**

**⚠️ ADVERTENCIA:** Esta es una versión **muy temprana, inestable y NO confiable** para proyectos serios. Puede fallar, perder datos o comportarse de forma inesperada. Está pensada para experimentar, aprender y divertirse. Si buscas un IDE profesional, usa VSCode, PyCharm o similares.

---

## 📦 Estado actual

- **Versión:** 1.0 (beta)
- **Soporte:** Solo **Windows** (no probado en Linux aún – próximamente)
- **Estabilidad:** ⭐⭐☆☆☆ (muy baja)
- **Confianza:** ⚠️ **No usar en producción** ⚠️

Esta es la **base** sobre la que construiré mejoras. Si te gusta la idea, puedes seguir el desarrollo y aportar lo que quieras.

---

## ✨ Características (lo que ya funciona a medias)

| Área            | Lo que hay                               |
|-----------------|------------------------------------------|
| Editor          | Monaco (el mismo de VSCode)              |
| Tema oscuro     | `karion-dark` con neones verdes          |
| Árbol de archivos| Navegación, crear, eliminar, renombrar   |
| Pestañas        | Con scroll, cierre individual            |
| Terminal integrada| Comandos básicos, historial (↑/↓)      |
| Guardado        | **Manual** (Ctrl+S) – nada de autoguardado |
| Búsqueda        | Ctrl+F (nativo del Monaco)               |
| Cambio de proyecto| Desde menú, sin reiniciar              |

---

## 🧰 Dependencias necesarias

Antes de ejecutar o compilar, instala estos paquetes de Python:

```bash
pip install PyQt5 PyQtWebEngine
```

> **Nota:** PyQtWebEngine es necesario para el editor Monaco. En algunas máquinas puede pesar ~100 MB.

---

## 🚀 Cómo ejecutar desde código fuente (modo desarrollo)

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Roussel19/karionideof.git
   cd karionideof
   ```
2. Instala dependencias (ver arriba).
3. Ejecuta:
   ```bash
   python main.py
   ```

Si todo va bien, aparecerá un diálogo de bienvenida para seleccionar tu carpeta de proyecto.

---

## 🧱 Cómo compilar un ejecutable (.exe) para Windows

Puedes generar un archivo `.exe` independiente usando **PyInstaller**. Sigue estos pasos:

1. Instala PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Desde la carpeta raíz del proyecto, ejecuta:
   ```bash
   pyinstaller --onefile --windowed --icon=logo.ico --name=KarionIDE main.py
   ```
   - `--onefile` → un solo `.exe`
   - `--windowed` → no muestra consola negra detrás
   - `--icon` → asigna el icono (si tienes `logo.ico`)
   - `--name` → nombre del ejecutable

3. El ejecutable aparecerá en la carpeta `dist/`.  
   **Importante:** Para que funcione el editor Monaco, necesitas que los archivos web se carguen desde internet. El ejecutable requiere conexión a internet la primera vez que abres el editor (descarga Monaco desde CDN). Después usa caché.

> 🧪 **Testeado en:** Windows 10 y 11 (64 bits).  
> 🐧 **Linux:** Aún no probado – es probable que necesites ajustar rutas o instalar `pyqtwebengine` con el gestor de paquetes del sistema.

---

## 🐞 Errores conocidos (y por qué no es confiable)

| Problema                                    | Estado / solución                          |
|---------------------------------------------|--------------------------------------------|
| El editor a veces no detecta cambios        | Ocurre al cambiar de pestaña rápido        |
| La terminal no maneja bien comandos interactivos (como `python`) | Solo funciona para comandos que terminan |
| El árbol de archivos no siempre se refresca tras cambios externos | Hay que usar botón "Refrescar" manual |
| El monitor de cambios (`QFileSystemWatcher`) falla en carpetas muy grandes | No recomendado para proyectos con miles de archivos |
| El foco del editor se pierde al volver de la terminal | Se soluciona haciendo clic en el editor |
| No hay soporte para temas claros ni traducción | Solo español/inglés mezclados             |

**Además:** puede crashear sin previo aviso, consumir mucha RAM en archivos enormes, y perder el contenido de pestañas sin guardar si se cierra inesperadamente.

---

## 🔮 Próximas mejoras (si el tiempo y la vida lo permiten)

- [ ] **Soporte para Linux** (adaptar rutas y terminal)
- [ ] **Mejor sistema de detección de cambios** (reemplazar polling por eventos del DOM)
- [ ] **Guardado automático opcional** (pero que se pueda desactivar)
- [ ] **Buscador avanzado en archivos** (grep)
- [ ] **Atajos de teclado configurables**
- [ ] **Minimapa** (si se puede sin matar el rendimiento)
- [ ] **Temas claros y más colores**
- [ ] **Mejorar la terminal** para que soporte aplicaciones interactivas

---

## ❤️ ¿Por qué hice esto?

> **Todo comenzó con una PC de bajos recursos**, donde cualquier IDE moderno iba lento. Quería algo ligero, oscuro, que me permitiera programar sin distracciones.  
> También **por curiosidad y ganas de aprender** cómo funciona PyQt5, cómo integrar Monaco, cómo manejar procesos de terminal, etc.  
> **No nació para competir**, sino para aprender y tal vez ayudar a alguien más que tenga una máquina humilde o que quiera ver cómo se construye un IDE desde cero.

Si llegas a usar esto y te gusta, o encuentras un bug, **abre un issue**. Si mejoras algo, **envía un pull request**. Todo se agradece.

---

## 📄 Licencia

MIT. Puedes hacer lo que quieras con el código, pero **bajo tu propio riesgo**. No me hago responsable de pérdida de datos, explosiones nucleares o que tu gato desaparezca.

---

<div align="center">
  <sub>Hecho con 💚 y mucho café ☕ – Roussel19</sub>
</div>
```
