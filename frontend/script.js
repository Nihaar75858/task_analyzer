// State management
let tasks = [];
let taskIdCounter = 1;

// DOM elements
const taskTitleInput = document.getElementById('taskTitle');
const dueDateInput = document.getElementById('dueDate');
const estimatedHoursInput = document.getElementById('estimatedHours');
const importanceInput = document.getElementById('importance');
const importanceValue = document.getElementById('importanceValue');
const dependenciesInput = document.getElementById('dependencies');
const addTaskBtn = document.getElementById('addTaskBtn');
const bulkInput = document.getElementById('bulkInput');
const bulkAddBtn = document.getElementById('bulkAddBtn');
const taskList = document.getElementById('taskList');
const taskCount = document.getElementById('taskCount');
const analyzeBtn = document.getElementById('analyzeBtn');
const strategySelect = document.getElementById('strategy');
const suggestionsSection = document.getElementById('suggestionsSection');
const suggestions = document.getElementById('suggestions');
const resultsSection = document.getElementById('resultsSection');
const results = document.getElementById('results');

// Event listeners
importanceInput.addEventListener('input', (e) => {
    importanceValue.textContent = e.target.value;
});

addTaskBtn.addEventListener('click', addTask);
bulkAddBtn.addEventListener('click', addBulkTasks);
analyzeBtn.addEventListener('click', analyzeTasks);

// Set minimum date to today
dueDateInput.min = new Date().toISOString().split('T')[0];

function addTask() {
    // Validate inputs
    if (!taskTitleInput.value.trim()) {
        alert('Please enter a task title');
        return;
    }
    if (!dueDateInput.value) {
        alert('Please select a due date');
        return;
    }
    if (!estimatedHoursInput.value || estimatedHoursInput.value < 0.5) {
        alert('Please enter estimated hours (minimum 0.5)');
        return;
    }

    const task = {
        id: taskIdCounter++,
        title: taskTitleInput.value.trim(),
        due_date: dueDateInput.value,
        estimated_hours: parseFloat(estimatedHoursInput.value),
        importance: parseInt(importanceInput.value),
        dependencies: dependenciesInput.value
            ? dependenciesInput.value.split(',').map(d => d.trim()).filter(d => d)
            : []
    };

    tasks.push(task);
    updateTaskList();
    clearForm();
}

function addBulkTasks() {
    try {
        const bulkTasks = JSON.parse(bulkInput.value);
        
        if (!Array.isArray(bulkTasks)) {
            alert('Invalid JSON: Expected an array of tasks');
            return;
        }

        bulkTasks.forEach(task => {
            if (!validateTaskData(task)) {
                throw new Error('Invalid task data in bulk input');
            }
            tasks.push({
                ...task,
                id: taskIdCounter++
            });
        });

        updateTaskList();
        bulkInput.value = '';
        alert(`Successfully added ${bulkTasks.length} tasks`);
    } catch (error) {
        alert('Error parsing JSON: ' + error.message);
    }
}

function validateTaskData(task) {
    return task.title &&
           task.due_date &&
           task.estimated_hours >= 0.5 &&
           task.importance >= 1 &&
           task.importance <= 10;
}

function clearForm() {
    taskTitleInput.value = '';
    dueDateInput.value = '';
    estimatedHoursInput.value = '';
    importanceInput.value = 5;
    importanceValue.textContent = 5;
    dependenciesInput.value = '';
}

function updateTaskList() {
    taskCount.textContent = tasks.length;

    if (tasks.length === 0) {
        taskList.innerHTML = '<p style="text-align: center; color: #999;">No tasks added yet. Add a task to get started.</p>';
        return;
    }

    taskList.innerHTML = tasks.map(task => `
        <div class="task-item">
            <h4>${task.title}</h4>
            <div class="task-item-details">
                <span>Due: ${task.due_date}</span>
                <span>${task.estimated_hours}h</span>
                <span>Importance: ${task.importance}/10</span>
                ${task.dependencies.length > 0 ? `<span> Dependencies: ${task.dependencies.join(', ')}</span>` : ''}
            </div>
        </div>
    `).join('');
}

async function analyzeTasks() {
    if (tasks.length === 0) return;

    suggestionsSection.classList.add('hidden');
    resultsSection.classList.add('hidden');

    const strategy = strategySelect.value;

    try {
        // Call analyze endpoint
        const analyzeResponse = await fetch('http://127.0.0.1:8000/api/tasks/analyze/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategy
            })
        });

        if (!analyzeResponse.ok) {
            const error = await analyzeResponse.json();
            throw new Error(error.error || 'Failed to analyze tasks');
        }

        const analyzeData = await analyzeResponse.json();

        // Call suggest endpoint
        const suggestResponse = await fetch('http://127.0.0.1:8000/api/tasks/suggest/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategy
            })
        });

        if (!suggestResponse.ok) {
            throw new Error('Failed to get suggestions');
        }

        const suggestData = await suggestResponse.json();

        // Display results
        displaySuggestions(suggestData.suggestions);
        displayResults(analyzeData.tasks);

        // Check for circular dependencies
        if (analyzeData.circular_dependencies && analyzeData.circular_dependencies.length > 0) {
            alert(`Warning: Circular dependencies detected in tasks: ${analyzeData.circular_dependencies.join(', ')}`);
        }

    } catch (error) {
        alert('Error analyzing tasks: ' + error.message);
        console.error('Analysis error:', error);
    } finally {
        
    }
}

