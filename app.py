from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import logging
import json
import time
import socket
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'change_this_secret_key_in_production'

# Función para crear logs en formato GELF
def create_gelf_log(short_message, full_message=None, level=6, extra_fields=None):
    gelf_message = {
        "version": "1.1",
        "host": socket.gethostname(),
        "short_message": short_message,
        "timestamp": time.time(),
        "level": level,
        "_application": "todo-app"
    }
    
    if full_message:
        gelf_message["full_message"] = full_message
    
    if extra_fields:
        for key, value in extra_fields.items():
            field_name = key if key.startswith('_') else f'_{key}'
            gelf_message[field_name] = value
    
    return json.dumps(gelf_message)

# Configuración de logging GELF
class GELFFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, 'gelf_data'):
            return record.gelf_data
        
        return create_gelf_log(
            short_message=record.getMessage(),
            level=self.get_gelf_level(record.levelno)
        )
    
    def get_gelf_level(self, python_level):
        mapping = {50: 2, 40: 3, 30: 4, 20: 6, 10: 7}
        return mapping.get(python_level, 6)

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Crear directorio de logs si no existe
os.makedirs('logs', exist_ok=True)

# Handler para archivo GELF
file_handler = logging.FileHandler('logs/todo_app_gelf.log')
file_handler.setFormatter(GELFFormatter())
logger.addHandler(file_handler)

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

def log_gelf(short_message, full_message=None, extra_fields=None):
    """Función helper para generar logs GELF"""
    gelf_log = create_gelf_log(short_message, full_message, extra_fields=extra_fields)
    record = logging.LogRecord(
        name='todo-app', level=logging.INFO, pathname='', lineno=0,
        msg='', args=(), exc_info=None
    )
    record.gelf_data = gelf_log
    logger.handle(record)

@app.route('/')
def index():
    if 'todos' not in session:
        session['todos'] = []
        log_gelf(
            short_message="Nueva sesión iniciada",
            full_message="Se ha iniciado una nueva sesión de usuario",
            extra_fields={'action': 'session_started'}
        )
    
    # Ordenar por importancia (1=alta, 2=media, 3=baja)
    todos = sorted(session['todos'], key=lambda x: (x.get('completed', False), x.get('importance', 3)))
    
    log_gelf(
        short_message="Acceso a página principal",
        extra_fields={
            'action': 'page_access',
            'page': 'index',
            'tasks_count': len(session['todos'])
        }
    )
    
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    task = request.form.get('task')
    importance = int(request.form.get('importance', 3))
    
    if task:
        todo_item = {
            'id': str(uuid.uuid4()),
            'task': task,
            'importance': importance,
            'completed': False,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if 'todos' not in session:
            session['todos'] = []
        
        session['todos'].append(todo_item)
        session.modified = True
        
        importance_text = {1: 'Alta', 2: 'Media', 3: 'Baja'}[importance]
        
        log_gelf(
            short_message="Nueva tarea agregada",
            full_message=f"Se agregó la tarea: '{task}' con importancia {importance_text} e ID: {todo_item['id']}",
            extra_fields={
                'action': 'task_created',
                'task_id': todo_item['id'],
                'task_name': task,
                'task_importance': importance,
                'task_importance_text': importance_text,
                'total_tasks': len(session['todos'])
            }
        )
    
    return redirect(url_for('index'))

@app.route('/complete/<todo_id>')
def complete_todo(todo_id):
    if 'todos' in session:
        for todo in session['todos']:
            if todo['id'] == todo_id:
                todo['completed'] = not todo['completed']
                session.modified = True
                
                log_gelf(
                    short_message="Estado de tarea modificado",
                    full_message=f"Tarea '{todo['task']}' marcada como {'completada' if todo['completed'] else 'pendiente'}",
                    extra_fields={
                        'action': 'task_status_changed',
                        'task_id': todo_id,
                        'task_name': todo['task'],
                        'task_importance': todo.get('importance', 3),
                        'new_status': 'completed' if todo['completed'] else 'pending'
                    }
                )
                break
    
    return redirect(url_for('index'))

@app.route('/edit/<todo_id>')
def edit_todo_form(todo_id):
    if 'todos' in session:
        for todo in session['todos']:
            if todo['id'] == todo_id:
                return render_template('edit.html', todo=todo)
    return redirect(url_for('index'))

@app.route('/edit/<todo_id>', methods=['POST'])
def edit_todo(todo_id):
    task = request.form.get('task')
    importance = int(request.form.get('importance', 3))
    
    if 'todos' in session and task:
        for todo in session['todos']:
            if todo['id'] == todo_id:
                old_task = todo['task']
                old_importance = todo.get('importance', 3)
                
                todo['task'] = task
                todo['importance'] = importance
                session.modified = True
                
                log_gelf(
                    short_message="Tarea editada",
                    full_message=f"Tarea modificada de '{old_task}' a '{task}', importancia de {old_importance} a {importance}",
                    extra_fields={
                        'action': 'task_edited',
                        'task_id': todo_id,
                        'old_task_name': old_task,
                        'new_task_name': task,
                        'old_importance': old_importance,
                        'new_importance': importance
                    }
                )
                break
    
    return redirect(url_for('index'))

@app.route('/delete/<todo_id>')
def delete_todo(todo_id):
    if 'todos' in session:
        original_count = len(session['todos'])
        task_name = None
        task_importance = None
        
        for todo in session['todos']:
            if todo['id'] == todo_id:
                task_name = todo['task']
                task_importance = todo.get('importance', 3)
                break
        
        session['todos'] = [todo for todo in session['todos'] if todo['id'] != todo_id]
        
        if len(session['todos']) < original_count:
            session.modified = True
            
            log_gelf(
                short_message="Tarea eliminada",
                full_message=f"Se eliminó la tarea: '{task_name}' con ID: {todo_id}",
                extra_fields={
                    'action': 'task_deleted',
                    'task_id': todo_id,
                    'task_name': task_name or 'unknown',
                    'task_importance': task_importance,
                    'remaining_tasks': len(session['todos'])
                }
            )
    
    return redirect(url_for('index'))

@app.route('/clear')
def clear_todos():
    if 'todos' in session:
        count = len(session['todos'])
        session['todos'] = []
        session.modified = True
        
        log_gelf(
            short_message="Todas las tareas eliminadas",
            full_message=f"Se eliminaron todas las tareas de la sesión",
            extra_fields={
                'action': 'all_tasks_cleared',
                'deleted_count': count
            }
        )
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
