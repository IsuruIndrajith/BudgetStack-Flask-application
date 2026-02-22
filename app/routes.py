from flask import Blueprint, render_template, request, redirect, url_for
from . import db
from .models import Expense

main = Blueprint('main', __name__)

@main.route('/')
def index():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    total = sum(e.amount for e in expenses)
    return render_template('index.html', expenses=expenses, total=total)

@main.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        expense = Expense(
            title=request.form['title'],
            amount=float(request.form['amount']),
            category=request.form['category'],
            description=request.form.get('description', '')
        )
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('add_expense.html')

@main.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('main.index'))