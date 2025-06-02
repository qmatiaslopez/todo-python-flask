# 📝 ToDo App - Lista de Tareas

Una aplicación web moderna y elegante para gestionar tus tareas diarias, desarrollada con Flask (Python) y diseñada con un enfoque en la usabilidad y el monitoreo avanzado.

## 🌐 Descripción

Esta aplicación de lista de tareas fue desarrollada y probada específicamente en **Debian 12 Bookworm**, aunque también debería funcionar sin problemas en otras distribuciones de Linux (Ubuntu, Mint, Fedora, etc.) y sistemas operativos que soporten Python 3.11

La aplicación ofrece una interfaz web intuitiva para organizar tus tareas con sistema de prioridades visuales, almacenamiento en sesión del navegador, y un sistema de logging estructurado en formato GELF que permite integración completa con **Graylog** para monitoreo y análisis de uso en tiempo real.

**Características principales:**
- ✅ Gestión completa de tareas (crear, editar, completar, eliminar)
- 🎯 Sistema de prioridades con indicadores visuales (🔴 Alta, 🟡 Media, 🟢 Baja)
- 📱 Interfaz responsive para dispositivos móviles y escritorio
- 📊 Logging avanzado en formato GELF para análisis y monitoreo
- 🎨 Diseño moderno con tema visual atractivo
- 💾 Almacenamiento en sesión (no requiere base de datos)

## 🛠️ Requisitos (Debian 12)

```bash
# Instalar Python, pip y venv
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

## 🚀 Instalación

```bash
# 1. Crear entorno virtual
python3 -m venv venv

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Ejecutar la aplicación

```bash
# Activar entorno virtual (si no está activo)
source venv/bin/activate

# Ejecutar aplicación
python3 app.py
```

La aplicación estará disponible en: **http://127.0.0.1:8000** 🌐

## 🎯 Cómo usar

- ➕ **Agregar tarea**: Escribe la descripción, selecciona importancia (Alta 🔴, Media 🟡, Baja 🟢) y clic en "Agregar"
- ✅ **Completar**: Clic en "Completar" para marcar como hecha
- ✏️ **Editar**: Clic en "Editar" para modificar la tarea
- 🗑️ **Eliminar**: Clic en "Eliminar" para borrar la tarea
- 🧹 **Limpiar todo**: Eliminar todas las tareas de una vez

## 📊 Logs GELF

Los logs se guardan automáticamente en formato GELF en `logs/todo_app_gelf.log` para ser compatibles con **Graylog**. Se registran todas las acciones: creación, edición, eliminación y cambios de estado de las tareas.

## 🛑 Detener la aplicación

Presiona `Ctrl + C` en la terminal donde está ejecutándose la aplicación.