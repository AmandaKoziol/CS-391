from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory task list with status
tasks = []

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task_description = request.form.get('task')
    if task_description:
        tasks.append({'description': task_description, 'completed': False})
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
    return redirect(url_for('index'))

@app.route('/toggle_bulk', methods=['POST'])
def toggle_task_bulk():
    completed_tasks = request.form.getlist('completed_tasks')
    completed_indices = [int(i) for i in completed_tasks]

    # Update the completion status of each task
    for i, task in enumerate(tasks):
        if i in completed_indices:
            task['completed'] = True
        else:
            task['completed'] = False

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)