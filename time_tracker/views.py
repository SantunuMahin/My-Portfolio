import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Task

VALID_STATUSES = {'todo', 'in_progress', 'done'}
VALID_PRIORITIES = {'low', 'medium', 'high'}


def task_board(request):
    """Kanban board view."""
    tasks_todo = Task.objects.filter(status='todo')
    tasks_in_progress = Task.objects.filter(status='in_progress')
    tasks_done = Task.objects.filter(status='done')
    context = {
        'tasks_todo': tasks_todo,
        'tasks_in_progress': tasks_in_progress,
        'tasks_done': tasks_done,
    }
    return render(request, 'time_tracker/board.html', context)


@require_http_methods(["POST"])
def create_task(request):
    """Create a new Kanban task."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    title = str(data.get('title', '')).strip()
    if not title:
        return JsonResponse({'error': 'Task title is required'}, status=400)

    status = data.get('status', 'todo')
    if status not in VALID_STATUSES:
        status = 'todo'

    priority = data.get('priority', 'medium')
    if priority not in VALID_PRIORITIES:
        priority = 'medium'

    due_date = data.get('due_date') or None

    task = Task.objects.create(
        title=title,
        description=data.get('description', '').strip(),
        priority=priority,
        status=status,
        due_date=due_date,
    )
    return JsonResponse({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'due_date': str(task.due_date) if task.due_date else None,
    }, status=201)


@require_http_methods(["PATCH", "PUT"])
def update_task_status(request, pk):
    """Update task details or status."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

    if 'title' in data:
        new_title = str(data.get('title', '')).strip()
        if new_title:
            task.title = new_title

    if 'description' in data:
        task.description = str(data.get('description', '')).strip()

    if 'status' in data:
        new_status = data.get('status')
        if new_status in VALID_STATUSES:
            task.status = new_status

    if 'priority' in data:
        new_priority = data.get('priority')
        if new_priority in VALID_PRIORITIES:
            task.priority = new_priority

    if 'due_date' in data:
        due_date_val = data.get('due_date')
        task.due_date = due_date_val if due_date_val else None

    task.save()
    return JsonResponse({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'due_date': str(task.due_date) if task.due_date else None,
    })


@require_http_methods(["DELETE"])
def delete_task(request, pk):
    """Delete a task."""
    try:
        task = Task.objects.get(pk=pk)
        task.delete()
        return JsonResponse({'success': True, 'id': pk})
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)


def get_tasks(request):
    """Fetch all tasks as JSON."""
    tasks = list(Task.objects.values('id', 'title', 'description', 'status', 'priority', 'due_date'))
    return JsonResponse({'tasks': tasks})
