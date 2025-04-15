from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt
import jwt
from datetime import datetime, timedelta
from sqlalchemy import func as db_func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:slava2006@localhost/attendance_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модели
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='student')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    group_number = db.Column(db.String(20), nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    attendance = db.Column(db.String(1), default='П')
    reason = db.Column(db.String(200), nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow().date)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)
    response = db.Column(db.String(200), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

def generate_token(user_id, role):
    payload = {'user_id': user_id, 'role': role, 'exp': datetime.utcnow() + timedelta(hours=24)}
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# Маршруты
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data['email']
    password = data['password'].encode('utf-8')
    name = data['name']
    group_number = data.get('group_number', '')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email уже зарегистрирован'}), 400

    role = 'student'
    if '_teacher' in email:
        role = 'teacher'
    elif '_headman' in email:
        role = 'headman'

    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
    user = User(email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()

    if role in ['student', 'headman']:
        student = Student(name=name, user_id=user.id, group_number=group_number)
        db.session.add(student)
        db.session.commit()

    token = generate_token(user.id, role)
    return jsonify({'message': 'Регистрация успешна', 'token': token}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email и пароль обязательны'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Неверный email или пароль'}), 401
    login_user(user)
    token = generate_token(user.id, user.role)
    return jsonify({'message': 'Вход успешен', 'token': token, 'role': user.role, 'user_id': user.id}), 200

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Выход успешен'}), 200

@app.route('/api/subjects', methods=['GET'])
@login_required
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'teacher_id': s.teacher_id} for s in subjects])

@app.route('/api/subjects', methods=['POST'])
@login_required
def create_subject():
    if current_user.role != 'teacher':
        return jsonify({'error': 'Доступ запрещен'}), 403
    data = request.json
    subject = Subject(name=data['name'], teacher_id=current_user.id)
    db.session.add(subject)
    db.session.commit()
    return jsonify({'message': 'Предмет создан', 'id': subject.id}), 201

@app.route('/api/attendance/<int:subject_id>', methods=['GET'])
@login_required
def get_attendance(subject_id):
    if current_user.role not in ['headman', 'teacher']:
        return jsonify({'error': 'Доступ запрещен'}), 403
    date_filter = request.args.get('date')
    query = Attendance.query.filter_by(subject_id=subject_id)
    if date_filter:
        query = query.filter_by(date=date_filter)
    attendances = query.all()
    result = []
    for att in attendances:
        student = Student.query.get(att.student_id)
        result.append({
            'id': att.id,
            'student_name': student.name,
            'group_number': student.group_number,
            'attendance': att.attendance,
            'reason': att.reason,
            'date': att.date.isoformat()
        })
    return jsonify(result)

@app.route('/api/update', methods=['POST'])
@login_required
def update_attendance():
    if current_user.role != 'headman':
        return jsonify({'error': 'Доступ запрещен'}), 403
    data = request.json
    student_id = data['student_id']
    subject_id = data['subject_id']
    attendance_value = data['attendance']
    date = data.get('date', datetime.utcnow().date().isoformat())

    att = Attendance.query.filter_by(student_id=student_id, subject_id=subject_id, date=date).first()
    if not att:
        att = Attendance(student_id=student_id, subject_id=subject_id, attendance=attendance_value, date=date)
        db.session.add(att)
    else:
        att.attendance = attendance_value
        att.reason = None

    db.session.commit()

    if attendance_value == 'Н':
        subject = Subject.query.get(subject_id)
        notification = Notification(
            student_id=student_id,
            subject_id=subject_id,
            message=f'Вы отсутствовали на предмете "{subject.name}" {date}. Укажите причину.'
        )
        db.session.add(notification)
        db.session.commit()

    return jsonify({'message': 'Updated successfully'})

@app.route('/api/student', methods=['GET'])
@login_required
def get_student_data():
    if current_user.role != 'student':
        return jsonify({'error': 'Доступ запрещен'}), 403
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Студент не найден'}), 404
    attendances = Attendance.query.filter_by(student_id=student.id).all()
    return jsonify({
        'name': student.name,
        'group_number': student.group_number,
        'attendances': [{'subject': att.subject.name, 'attendance': att.attendance, 'reason': att.reason, 'date': att.date.isoformat()} for att in attendances]
    })

@app.route('/api/students', methods=['GET'])
@login_required
def get_students():
    if current_user.role != 'headman':
        return jsonify({'error': 'Доступ запрещен'}), 403
    headman_student = Student.query.filter_by(user_id=current_user.id).first()
    if not headman_student:
        return jsonify({'error': 'Староста не найден'}), 404
    students = Student.query.filter_by(group_number=headman_student.group_number).all()
    return jsonify([{'id': s.id, 'name': s.name, 'group_number': s.group_number} for s in students])

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    if current_user.role != 'student':
        return jsonify({'error': 'Доступ запрещен'}), 403
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Студент не найден'}), 404
    notifications = Notification.query.filter_by(student_id=student.id, is_resolved=False).all()
    return jsonify([{
        'id': n.id,
        'subject_id': n.subject_id,
        'subject_name': Subject.query.get(n.subject_id).name,
        'message': n.message,
        'created_at': n.created_at.isoformat(),
        'attendance_date': Attendance.query.filter_by(
            student_id=n.student_id,
            subject_id=n.subject_id,
            attendance='Н'
        ).filter(Attendance.date <= db_func.date(n.created_at)).order_by(Attendance.date.desc()).first().date.isoformat()
        if Attendance.query.filter_by(student_id=n.student_id, subject_id=n.subject_id, attendance='Н').first()
        else n.created_at.isoformat()
    } for n in notifications])

@app.route('/api/reason', methods=['POST'])
@login_required
def submit_reason():
    if current_user.role != 'student':
        return jsonify({'error': 'Доступ запрещен'}), 403
    data = request.json
    notification_id = data['notification_id']
    response = data['response']
    date = data.get('date')

    notification = Notification.query.get(notification_id)
    if notification and notification.student_id == Student.query.filter_by(user_id=current_user.id).first().id:
        notification.response = response
        notification.is_resolved = True
        
        attendance = Attendance.query.filter_by(
            student_id=notification.student_id, 
            subject_id=notification.subject_id, 
            date=date
        ).first()
        if attendance:
            attendance.reason = response
        else:
            attendance = Attendance(
                student_id=notification.student_id,
                subject_id=notification.subject_id,
                attendance='Н',
                reason=response,
                date=date
            )
            db.session.add(attendance)
        
        db.session.commit()
        return jsonify({'message': 'Причина сохранена'}), 200
    return jsonify({'error': 'Уведомление не найдено'}), 404

@app.route('/api/teacher/attendance/<int:subject_id>', methods=['GET'])
@login_required
def get_teacher_attendance(subject_id):
    if current_user.role != 'teacher':
        return jsonify({'error': 'Доступ запрещен'}), 403
    filter_type = request.args.get('filter', 'day')
    date_filter = request.args.get('date')
    today = datetime.utcnow().date()

    if filter_type == 'day':
        if date_filter:
            start_date = end_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        else:
            start_date = end_date = today
    elif filter_type == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif filter_type == 'month':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    attendances = Attendance.query.filter(
        Attendance.subject_id == subject_id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).all()
    
    result = []
    for att in attendances:
        student = Student.query.get(att.student_id)
        notification = Notification.query.filter_by(
            student_id=att.student_id,
            subject_id=att.subject_id,
            is_resolved=True
        ).filter(db_func.date(Notification.created_at) >= att.date).first()
        
        reason = notification.response if notification and notification.response else (att.reason or 'Не указано')
        
        result.append({
            'id': att.id,
            'student_name': student.name,
            'group_number': student.group_number,
            'attendance': att.attendance,
            'reason': reason,
            'date': att.date.isoformat()
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)