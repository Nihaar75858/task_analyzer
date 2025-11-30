from datetime import date, datetime
from typing import List, Dict, Any
class PriorityScorer:
    
    # Configurable weights for different strategies
    STRATEGY_WEIGHTS = {
        'smart_balance': {
            'urgency': 0.35,
            'importance': 0.30,
            'effort': 0.20,
            'dependencies': 0.15
        },
        'fastest_wins': {
            'urgency': 0.10,
            'importance': 0.20,
            'effort': 0.70,
            'dependencies': 0.00
        },
        'high_impact': {
            'urgency': 0.15,
            'importance': 0.80,
            'effort': 0.05,
            'dependencies': 0.00
        },
        'deadline_driven': {
            'urgency': 0.80,
            'importance': 0.15,
            'effort': 0.05,
            'dependencies': 0.00
        }
    }
    
    @staticmethod
    def calculate_urgency_score(due_date: date) -> float:
        today = date.today()
        days_until_due = (due_date - today).days
        
        if days_until_due < 0:
            # Overdue - escalates quickly
            return min(150, 100 + abs(days_until_due) * 5)
        elif days_until_due == 0:
            return 95
        elif days_until_due == 1:
            return 85
        elif days_until_due <= 3:
            return 70
        elif days_until_due <= 7:
            return 50
        elif days_until_due <= 14:
            return 30
        else:
            return 10
    
    @staticmethod
    def calculate_importance_score(importance: int) -> float:
        return (importance / 10) * 100
    
    @staticmethod
    def calculate_effort_score(estimated_hours: float) -> float:
        # Inverse scoring - less time = higher score
        return max(0, 100 - (estimated_hours * 10))
    
    @staticmethod
    def calculate_dependency_score(dependencies: List) -> float:
        return len(dependencies) * 15
    
    @classmethod
    def calculate_priority(
        cls,
        task: Dict[str, Any],
        strategy: str = 'smart_balance'
    ) -> Dict[str, Any]:
        # Handle due_date validation
        if isinstance(task.get('due_date'), str):
            due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
        else:
            due_date = task['due_date']
        
        # Calculate individual scores
        urgency = cls.calculate_urgency_score(due_date)
        importance = cls.calculate_importance_score(task['importance'])
        effort = cls.calculate_effort_score(task['estimated_hours'])
        dependencies = cls.calculate_dependency_score(task.get('dependencies', []))
        
        # Get weights for selected strategy
        weights = cls.STRATEGY_WEIGHTS.get(strategy, cls.STRATEGY_WEIGHTS['smart_balance'])
        
        # Calculate weighted final score
        final_score = (
            urgency * weights['urgency'] +
            importance * weights['importance'] +
            effort * weights['effort'] +
            dependencies * weights['dependencies']
        )
        
        return {
            'priority_score': round(final_score, 2),
            'breakdown': {
                'urgency_score': round(urgency, 2),
                'importance_score': round(importance, 2),
                'effort_score': round(effort, 2),
                'dependency_score': round(dependencies, 2)
            },
            'explanation': "",
            'strategy_used': strategy
        }