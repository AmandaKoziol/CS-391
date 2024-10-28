from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model to store income and expenses
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Query the database to get all transactions
    transactions = Transaction.query.all()

    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expenses

    return render_template('index.html', transactions=transactions, total_income=total_income,
                           total_expenses=total_expenses, balance=balance)

@app.route('/add', methods=['POST'])
def add_transaction():
    amount = float(request.form['amount'])
    type = request.form['type']
    category = request.form['category']
    description = request.form['description']

    # Create a new transaction
    new_transaction = Transaction(amount=amount, type=type, category=category, description=description)
    db.session.add(new_transaction)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_transaction(id):
    # Find the transaction by ID and delete it
    transaction = Transaction.query.get(id)
    db.session.delete(transaction)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
