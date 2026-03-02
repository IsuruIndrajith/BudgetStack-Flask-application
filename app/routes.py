from flask import Blueprint, render_template, request, redirect, url_for
from . import db
from .models import Expense
from flask import session
from .models import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    expenses = Expense.query.filter_by(user_id=session['user_id'])\
                            .order_by(Expense.date.desc()).all()
    total = sum(e.amount for e in expenses)
    return render_template('index.html', expenses=expenses, total=total)

@main.route('/add', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        expense = Expense(
            title=request.form['title'],
            amount=float(request.form['amount']),
            category=request.form['category'],
            description=request.form.get('description', ''),
            user_id=session['user_id']
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

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            email=request.form['email']
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('main.index'))
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.login'))