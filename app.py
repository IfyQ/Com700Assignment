from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from models.users import User, db, init_models
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

# MongoDB configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/your_database'
mongo = PyMongo(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

init_models(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/patients', methods=['GET', 'POST'])
def patients():
    if request.method == 'POST':
        patient_data = {
            'id': request.form['id'],
            'gender': request.form['gender'],
            'age': request.form['age'],
            'hypertension': request.form['hypertension'],
            'heart_disease': request.form['heart_disease'],
            'ever_married': request.form['ever_married'],
            'work_type': request.form['work_type'],
            'Residence_type': request.form['Residence_type'],
            'avg_glucose_level': request.form['avg_glucose_level'],
            'bmi': request.form['bmi'],
            'smoking_status': request.form['smoking_status']
        }
        mongo.db.patients.insert_one(patient_data)
        flash('Patient record added successfully!', 'success')
        return redirect(url_for('patients'))
    patients = mongo.db.patients.find()
    return render_template('patients.html', patients=patients)

@app.route('/edit_patient/<patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = mongo.db.patients.find_one({'_id': ObjectId(patient_id)})
    if request.method == 'POST':
        updated_data = {
            'id': request.form['id'],
            'gender': request.form['gender'],
            'age': request.form['age'],
            'hypertension': request.form['hypertension'],
            'heart_disease': request.form['heart_disease'],
            'ever_married': request.form['ever_married'],
            'work_type': request.form['work_type'],
            'Residence_type': request.form['Residence_type'],
            'avg_glucose_level': request.form['avg_glucose_level'],
            'bmi': request.form['bmi'],
            'smoking_status': request.form['smoking_status']
        }
        mongo.db.patients.update_one({'_id': ObjectId(patient_id)}, {'$set': updated_data})
        flash('Patient record updated successfully!', 'success')
        return redirect(url_for('patients'))
    return render_template('edit_patient.html', patient=patient)

@app.route('/delete_patient/<patient_id>')
def delete_patient(patient_id):
    mongo.db.patients.delete_one({'_id': ObjectId(patient_id)})
    flash('Patient record deleted successfully!', 'success')
    return redirect(url_for('patients'))

if __name__ == '__main__':
    app.run(debug=True)