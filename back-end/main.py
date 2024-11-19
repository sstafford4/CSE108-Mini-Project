from flask import request, jsonify, render_template, url_for, redirect, flash
from config import db, app
from models import User, Course, Enrollment
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Secure ModelView to restrict admin access
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == 'Admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('index'))

# Customized UserModelView
class UserModelView(SecureModelView):
    column_list = ('id', 'username', 'user_type', 'person_name')
    column_searchable_list = ('username', 'person_name')
    column_filters = ('user_type',)
    form_choices = {
        'user_type': [
            ('Admin', 'Admin'),
            ('Student', 'Student'),
            ('Teacher', 'Teacher'),
        ]
    }


# Customized CourseModelView
class CourseModelView(SecureModelView):
    column_list = ('id', 'course_name', 'course_number', 'professor', 'capacity', 'enrolled_students')
    column_searchable_list = ('course_name', 'course_number', 'professor')
    column_filters = ('professor',)

# Customized EnrollmentModelView
class EnrollmentModelView(SecureModelView):
    inline_models = [(User, dict(form_columns=['username'])), (Course, dict(form_columns=['course_name']))]

# Initialize Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')
admin.add_view(UserModelView(User, db.session))
admin.add_view(CourseModelView(Course, db.session))
admin.add_view(SecureModelView(Enrollment, db.session))

app.secret_key = 'your_secret_key_here'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/create_acc_page')
def create_acc_page():
    return render_template('create_acc.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    username = request.json.get('username')  # Expect JSON data
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.password == password:
        login_user(user)
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user_type": user.user_type,
            "person_name": user.person_name
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid username or password"
        }), 401

    # if request.method == 'POST':
    #     username = request.form.get('username')
    #     password = request.form.get('password')
    #     user = User.query.filter_by(username=username).first()
    #
    #     if user and user.password == password:
    #         login_user(user)
    #         if user.user_type == "Student":
    #             return redirect(url_for('studentview', username=username))
    #         elif user.user_type == "Teacher":
    #             return redirect(url_for('teacherview', username=username))
    #         elif user.user_type == "Admin":
    #             return redirect('/admin')
    #     else:
    #         flash("Invalid username or password", "error")
    #         return redirect(url_for('index'))
    #
    # return render_template('login.html')

@app.route('/create_acc', methods=['POST'])
def create_account():
    username = request.form.get('username')
    person_name = request.form.get('person_name')
    password = request.form.get('password')
    user_type = request.form.get('user_type')

    if user_type not in ['Admin', 'Student', 'Teacher']:
        flash("Invalid user type selected.", "error")
        return redirect(url_for('create_acc_page'))

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash("Account already exists under this Username", "error")
        return redirect(url_for('create_acc_page'))

    new_user = User(username=username, password=password, user_type=user_type, person_name=person_name)
    db.session.add(new_user)
    db.session.commit()
    flash("Account created successfully! Please log in.", "success")
    return redirect(url_for('index'))

@app.route('/student/<username>')
@login_required
def studentview(username):
    user = User.query.filter_by(username=username).first()
    return render_template('studentview.html', person_name=user.person_name)

@app.route('/teacher/<username>')
@login_required
def teacherview(username):
    return render_template('teacherview.html')

@app.route('/get_all_courses', methods=['GET'])
@login_required
def get_all_courses():
    enrolled_course_ids = {
        enrollment.course_id for enrollment in Enrollment.query.filter_by(user_id=current_user.id).all()
    }
    all_courses_list = Course.query.all()
    return render_template('allCourses.html', courses=all_courses_list, enrolled_course_ids=enrolled_course_ids)

@app.route('/register_for_course/<int:course_id>', methods=['POST'])
@login_required
def register_for_course(course_id):
    course = Course.query.get(course_id)
    if course and course.has_capacity():
        course.enrolled_students += 1
        db.session.commit()
        enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({"message": "Successfully registered for the course"})
    else:
        return jsonify({"message": "Course is full or not found"}), 400

@app.route('/drop_course/<int:course_id>', methods=['POST'])
@login_required
def drop_course(course_id):
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if enrollment:
        course = Course.query.get(course_id)
        if course:
            course.enrolled_students -= 1
            db.session.commit()
        db.session.delete(enrollment)
        db.session.commit()
        return jsonify({"message": "Successfully dropped the course"})
    else:
        return jsonify({"message": "You are not enrolled in this course"}), 400

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
