from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .scoring import PriorityScorer
from datetime import datetime

@csrf_exempt
@require_http_methods(["POST"])
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/
    
    Accept a list of tasks and return them sorted by priority score.
    
    Request body:
    {
        "tasks": [...],
        "strategy": "smart_balance" (optional)
    }
    
    Response:
    {
        "tasks": [...sorted tasks with scores...],
        "circular_dependencies": [...],
        "strategy_used": "smart_balance"
    }
    """
    try:
        data = json.loads(request.body)
        tasks = data.get('tasks', [])
        strategy = data.get('strategy', 'smart_balance')
        
        if not tasks:
            return JsonResponse({
                'error': 'No tasks provided'
            }, status=400)
        
        # Validate all tasks
        validation_errors = {}
        for idx, task in enumerate(tasks):
            errors = PriorityScorer.validate_task(task)
            if errors:
                validation_errors[f'task_{idx}'] = errors
        
        if validation_errors:
            return JsonResponse({
                'error': 'Validation failed',
                'details': validation_errors
            }, status=400)
        
        # Check for circular dependencies
        circular_deps = PriorityScorer.detect_circular_dependencies(tasks)
        
        # Calculate priority for each task
        analyzed_tasks = []
        for task in tasks:
            priority_data = PriorityScorer.calculate_priority(task, strategy)
            analyzed_task = {
                **task,
                'priority_score': priority_data['priority_score'],
                'score_breakdown': priority_data['breakdown'],
                'explanation': priority_data['explanation']
            }
            analyzed_tasks.append(analyzed_task)
        
        # Sort by priority score (descending)
        analyzed_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return JsonResponse({
            'tasks': analyzed_tasks,
            'circular_dependencies': circular_deps,
            'strategy_used': strategy,
            'total_tasks': len(analyzed_tasks)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
