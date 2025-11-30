# Smart Task Analyzer

An intelligent task management system that prioritizes tasks based on multiple factors including urgency, importance, effort, and dependencies.

## Features

- **Multi-Factor Priority Scoring**: Analyzes tasks using urgency, importance, effort, and dependencies
- **Multiple Sorting Strategies**: 
  - Smart Balance (default)
  - Fastest Wins (effort-focused)
  - High Impact (importance-focused)
  - Deadline Driven (urgency-focused)
- **Top 3 Recommendations**: Get personalized suggestions for what to work on today
- **Circular Dependency Detection**: Identifies problematic task dependencies
- **Comprehensive Validation**: Ensures data integrity with detailed error messages
- **Clean REST API**: Well-structured endpoints for task analysis
- **Responsive UI**: Works seamlessly on desktop, tablet, and mobile

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the repository**

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Start the development server**
```bash
python manage.py runserver
```

6. **Access the application**
Open your browser and navigate to: `http://localhost:8000`

## Running Tests

Run the test suite using pytest:

```bash
pytest
```

For verbose output:
```bash
pytest -v
```

For coverage report:
```bash
pytest --cov=tasks tests/
```

## Algorithm Explanation

The Smart Task Analyzer uses a sophisticated multi-factor scoring algorithm to prioritize tasks:

### Core Components

1. **Urgency Score (0-150)**
   - Overdue tasks: 100 + (days overdue × 5) - escalates rapidly
   - Due today: 95 points
   - Due tomorrow: 85 points
   - Due in 2-3 days: 70 points
   - Due in 4-7 days: 50 points
   - Due in 8-14 days: 30 points
   - Due beyond 14 days: 10 points

2. **Importance Score (0-100)**
   - Directly normalized from user's 1-10 rating
   - Allows users to flag critical tasks regardless of deadline

3. **Effort Score (0-100)**
   - Inverse relationship: Lower effort = higher score
   - Promotes "quick wins" that can be completed efficiently
   - Formula: max(0, 100 - (estimated_hours × 10))

4. **Dependency Score (0+)**
   - 15 points per dependent task
   - Tasks that block other work receive higher priority
   - Helps prevent bottlenecks in task workflows

### Scoring Strategies

The system offers four configurable strategies that weight factors differently:

**Smart Balance (Default)**
- Urgency: 35%
- Importance: 30%
- Effort: 20%
- Dependencies: 15%
- Best for: General productivity and balanced workflow

**Fastest Wins**
- Effort: 70%
- Importance: 20%
- Urgency: 10%
- Dependencies: 0%
- Best for: Building momentum and clearing small tasks

**High Impact**
- Importance: 80%
- Urgency: 15%
- Effort: 5%
- Dependencies: 0%
- Best for: Strategic work and high-value deliverables

**Deadline Driven**
- Urgency: 80%
- Importance: 15%
- Effort: 5%
- Dependencies: 0%
- Best for: Time-sensitive environments and deadline management

### Edge Cases Handled

- **Past-due tasks**: Receive escalating urgency scores to ensure immediate attention
- **Missing data**: Comprehensive validation prevents invalid tasks from being processed
- **Circular dependencies**: Graph-based detection algorithm identifies cycles
- **Zero dependencies**: Tasks function normally without blocking relationships
- **Extreme values**: Scores are bounded and normalized to prevent overflow

## API Endpoints

### POST /api/tasks/analyze/
Analyze and sort tasks by priority score.

**Request:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Fix login bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ],
  "strategy": "smart_balance"
}
```

**Response:**
```json
{
  "tasks": [...sorted tasks with scores...],
  "circular_dependencies": [],
  "strategy_used": "smart_balance",
  "total_tasks": 1
}
```

### POST /api/tasks/suggest/
Get top 3 recommended tasks to work on today.

**Request:** Same as analyze endpoint

**Response:**
```json
{
  "suggestions": [
    {
      "id": 1,
      "title": "Fix login bug",
      "priority_score": 87.5,
      "explanation": "Overdue task with high importance",
      "why_today": "This is your highest priority task. It's overdue and needs immediate attention."
    }
  ],
  "strategy_used": "smart_balance",
  "total_tasks_analyzed": 5
}
```

## Design Decisions

### 1. **Stateless API Design**
- Tasks are not persisted in the database for this assignment
- Focus on algorithm quality over data persistence
- Allows for easy testing and demonstration
- Production version would include full CRUD operations

### 2. **Configurable Scoring Weights**
- Different work contexts require different prioritization
- Users can switch strategies without modifying code
- Easy to add new strategies by defining weight configurations

### 3. **Overdue Task Escalation**
- Overdue tasks receive increasingly higher scores
- Prevents tasks from languishing in "overdue limbo"
- Encourages timely completion or re-evaluation

### 4. **Effort-Based Quick Wins**
- Lower effort tasks can be valuable momentum builders
- "Fastest Wins" strategy specifically targets this
- Balances strategic importance with psychological benefits of completion

### 5. **Dependency Awareness**
- Identifies tasks that block other work
- Circular dependency detection prevents impossible schedules
- Helps users understand task relationships

## Time Breakdown

- Algorithm Design & Implementation: 1.5 hours
- Django Backend (models, views, scoring, unit tests): 1 hour 15 min
- API Endpoints & Error Handling: 45 minutes
- Frontend (HTML/CSS/JavaScript): 2 hours
- Documentation: 20 minutes

**Total: 4 hours**

## Bonus Challenges Completed

- **Comprehensive Unit Tests**: 5 tests covering all major functionality
- **Circular Dependency Detection**: Graph-based cycle detection algorithm
- **Multiple Sorting Strategies**: Four different prioritization approaches
- **Detailed Explanations**: Human-readable reasoning for each priority score

## Future Improvements

With additional time, I would implement:

1. **Persistence Layer**
   - Full CRUD operations for tasks
   - User authentication and multi-user support
   - Task history and completion tracking

2. **Advanced Features**
   - Calendar integration for deadline awareness
   - Weekend/holiday consideration in urgency calculation
   - Machine learning to personalize weights based on user behavior
   - Eisenhower Matrix visualization (2D urgent vs important grid)

3. **Enhanced UX**
   - Drag-and-drop task reordering
   - Visual dependency graph with interactive nodes
   - Task templates for common workflows
   - Export functionality (CSV, PDF reports)

4. **Performance Optimization**
   - Caching for frequently analyzed task sets
   - Async processing for large task lists
   - Database indexing strategies

5. **Analytics Dashboard**
   - Completion rate tracking
   - Time estimation accuracy
   - Priority distribution visualizations
   - Personal productivity insights

## Project Structure

```
task-analyzer/
├── backend/
│   ├── manage.py
│   ├── task_analyzer/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── tasks/
│   |   ├── models.py
│   |   ├── views.py
│   |   ├── scoring.py
│   |   ├── urls.py
│   |   └── tests.py
│   ├── pytest.ini
|   └── requirements.txt
|
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── .gitignore
└── README.md
```

## Technologies Used

- **Backend**: Django 4.2, Python 3.8+
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Testing**: pytest, pytest-django
- **Database**: SQLite (development)

## Contributing

This is a technical assessment project. For production use, please fork and adapt as needed.

## License

MIT License - feel free to use this code for learning and development purposes.
