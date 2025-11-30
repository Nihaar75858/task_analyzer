import pytest
from datetime import date, timedelta
from .scoring import PriorityScorer

# Create your tests here.
@pytest.mark.django_db
class TestPriorityScorer:
    """Test suite for the PriorityScorer algorithm"""
    
    def test_calculate_priority_basic(self):
        """Test basic priority calculation"""
        task = {
            'id': 1,
            'title': 'Test Task',
            'due_date': date.today() + timedelta(days=3),
            'estimated_hours': 2,
            'importance': 8,
            'dependencies': []
        }
        
        result = PriorityScorer.calculate_priority(task)
        
        assert 'priority_score' in result
        assert 'breakdown' in result
        assert 'explanation' in result
        assert 'strategy_used' in result
        assert isinstance(result['priority_score'], float)
        assert result['priority_score'] > 0
        
    def test_overdue_task_priority(self):
        """Test that overdue tasks get very high priority"""
        overdue_task = {
            'id': 1,
            'title': 'Overdue Task',
            'due_date': date.today() - timedelta(days=5),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': []
        }
        
        normal_task = {
            'id': 2,
            'title': 'Normal Task',
            'due_date': date.today() + timedelta(days=7),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': []
        }
        
        overdue_score = PriorityScorer.calculate_priority(overdue_task)
        normal_score = PriorityScorer.calculate_priority(normal_task)
        
        assert overdue_score['priority_score'] > normal_score['priority_score']