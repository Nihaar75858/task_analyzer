from datetime import date, datetime
from typing import List, Dict, Any
class PriorityScorer:
    """
    Intelligent priority scoring algorithm for tasks.
    
    The algorithm considers multiple factors:
    - Urgency: How soon is the task due?
    - Importance: User-provided rating (1-10)
    - Effort: Lower effort tasks are "quick wins"
    - Dependencies: Tasks blocking others rank higher
    """
    
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
        """
        Calculate urgency score based on days until due date.
        
        Scoring logic:
        - Overdue: 100 + (days overdue * 5) - highest priority
        - Due today: 95
        - Due tomorrow: 85
        - Due in 2-3 days: 70
        - Due in 4-7 days: 50
        - Due in 8-14 days: 30
        - Due beyond 14 days: 10
        """
        
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
        """
        Normalize importance (1-10 scale) to 0-100 score.
        """
        return (importance / 10) * 100
    
    @staticmethod
    def calculate_effort_score(estimated_hours: float) -> float:
        """
        Calculate effort score (inverse relationship).
        Lower effort = higher score (quick wins).
        
        - 1 hour or less: 90+ points
        - 2-3 hours: 70-80 points
        - 4-5 hours: 50-60 points
        - 6+ hours: diminishing returns
        """
        # Inverse scoring - less time = higher score
        return max(0, 100 - (estimated_hours * 10))
    
    @staticmethod
    def calculate_dependency_score(dependencies: List) -> float:
        """
        Score based on number of dependencies.
        More dependencies = higher score (blocks other work).
        """
        return len(dependencies) * 15
    
    @classmethod
    def calculate_priority(
        cls,
        task: Dict[str, Any],
        strategy: str = 'smart_balance'
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive priority score for a task.
        
        Args:
            task: Dictionary containing task details
            strategy: Scoring strategy to use
            
        Returns:
            Dictionary with score, breakdown, and explanation
        """
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
        
        # Generate explanation
        explanation = cls._generate_explanation(
            task, urgency, importance, effort, dependencies, strategy
        )
        
        return {
            'priority_score': round(final_score, 2),
            'breakdown': {
                'urgency_score': round(urgency, 2),
                'importance_score': round(importance, 2),
                'effort_score': round(effort, 2),
                'dependency_score': round(dependencies, 2)
            },
            'explanation': explanation,
            'strategy_used': strategy
        }
        
    @classmethod
    def detect_circular_dependencies(
        cls,
        tasks: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Detect circular dependencies in task list.
        
        Returns:
            List of task IDs involved in circular dependencies
        """
        task_map = {task['id']: task.get('dependencies', []) for task in tasks}
        circular = []
        
        def has_cycle(task_id, visited, rec_stack):
            visited.add(task_id)
            rec_stack.add(task_id)
            
            for dep_id in task_map.get(task_id, []):
                if dep_id not in visited:
                    if has_cycle(dep_id, visited, rec_stack):
                        return True
                elif dep_id in rec_stack:
                    circular.append(task_id)
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        visited = set()
        for task_id in task_map.keys():
            if task_id not in visited:
                has_cycle(task_id, visited, set())
        
        return list(set(circular))
        
    @classmethod
    def validate_task(cls, task: Dict[str, Any]) -> List[str]:
        """
        Validate task data and return list of errors.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        required_fields = ['title', 'due_date', 'estimated_hours', 'importance']
        for field in required_fields:
            if field not in task or task[field] is None:
                errors.append(f"Missing required field: {field}")
        
        if 'importance' in task:
            if not (1 <= task['importance'] <= 10):
                errors.append("Importance must be between 1 and 10")
        
        if 'estimated_hours' in task:
            if task['estimated_hours'] < 0.5:
                errors.append("Estimated hours must be at least 0.5")
        
        return errors
    
    @staticmethod
    def _generate_explanation(
        task: Dict,
        urgency: float,
        importance: float,
        effort: float,
        dependencies: float,
        strategy: str
    ) -> str:
        """Generate human-readable explanation for the priority score."""
        reasons = []
        
        if urgency > 95:
            reasons.append("OVERDUE - requires immediate attention")
        elif urgency > 85:
            reasons.append("due very soon")
        elif urgency > 70:
            reasons.append("approaching deadline")
        
        if importance > 80:
            reasons.append("high importance rating")
        elif importance > 50:
            reasons.append("moderate importance")
        
        if effort > 70:
            reasons.append("quick win opportunity")
        elif effort < 30:
            reasons.append("significant time investment")
        
        if dependencies > 20:
            reasons.append("blocks other tasks")
        
        if not reasons:
            reasons.append("balanced priority across all factors")
        
        strategy_context = {
            'fastest_wins': "Prioritized for quick completion. ",
            'high_impact': "Prioritized for maximum impact. ",
            'deadline_driven': "Prioritized by deadline urgency. ",
            'smart_balance': "Balanced priority considering all factors. "
        }
        
        return strategy_context.get(strategy, "") + ", ".join(reasons).capitalize() + "."