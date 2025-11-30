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
        
@csrf_exempt
@require_http_methods(["POST"])
def suggest_tasks(request):
    """
    POST /api/tasks/suggest/
    
    Return the top 3 tasks the user should work on today.
    
    Request body:
    {
        "tasks": [...],
        "strategy": "smart_balance" (optional)
    }
    
    Response:
    {
        "suggestions": [top 3 tasks with explanations],
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
        
        # Validate tasks
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
        
        # Calculate priorities
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
        
        # Sort and get top 3
        analyzed_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
        top_three = analyzed_tasks[:3]
        
        # Add detailed recommendations
        for idx, task in enumerate(top_three, 1):
            task['recommendation_rank'] = idx
            task['why_today'] = _generate_recommendation_reason(task, idx)
        
        return JsonResponse({
            'suggestions': top_three,
            'strategy_used': strategy,
            'total_tasks_analyzed': len(analyzed_tasks)
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

        
def _generate_recommendation_reason(task, rank):
    """Generate a specific recommendation for why to work on this task today."""
    reasons = []
    
    breakdown = task.get('score_breakdown', {})
    urgency = breakdown.get('urgency_score', 0)
    importance = breakdown.get('importance_score', 0)
    effort = breakdown.get('effort_score', 0)
    
    if rank == 1:
        reasons.append("This is your highest priority task.")
    
    if urgency > 95:
        reasons.append("It's overdue and needs immediate attention.")
    elif urgency > 85:
        reasons.append("The deadline is very close.")
    
    if importance > 80:
        reasons.append("It has high strategic importance.")
    
    if effort > 70:
        reasons.append("It's a quick win that you can complete efficiently.")
    
    if not reasons:
        reasons.append("It offers the best balance of urgency, importance, and effort.")
    
    return " ".join(reasons)
