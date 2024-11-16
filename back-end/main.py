from flask import request, jsonify, render_template, url_for, redirect, flash, session
from config import db, app
from models import User, Course, Enrollment

# Set a secret key for session management
app.secret_key = 'your_secret_key_here'  # Change this to a secure random key

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/create_acc_page')
def create_acc_page():
    return render_template('create_acc.html')

@app.route('/all_courses')
def all_courses():
    return render_template('allCourses.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            # Store user information in session
            session['user_id'] = user.id  # Store user ID in session

            # Redirect based on user_type
            if user.user_type == "Student":
                return redirect(url_for('studentview', username=username))
            elif user.user_type == "Teacher":
                return redirect(url_for('teacherview', username=username))
            elif user.user_type == "Admin" and user.password == 'ADMIN':
                return redirect(url_for('adminview', username=username))
        else:
            # Invalid credentials
            flash("Invalid username or password", "error")
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/create_acc', methods=['POST'])
def create_account():
    # Retrieve form data
    username = request.form.get('username')
    person_name = request.form.get('person_name')
    password = request.form.get('password')
    user_type = request.form.get('user_type')

    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash("Account already exists under this Username", "error")
        return redirect(url_for('create_acc_page'))

    # Create new user
    new_user = User(username=username, password=password, user_type=user_type, person_name=person_name)
    db.session.add(new_user)
    db.session.commit()

    flash("Account created successfully! Please log in.", "success")
    return redirect(url_for('index'))

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    course_name = request.form.get('course_name')
    course_number = request.form.get('course_number')
    professor = request.form.get('professor')
    capacity = request.form.get('capacity')

    existing_course = Course.query.filter_by(course_name=course_name).first()
    if existing_course:
        flash("Course already exists under this name", "error")
        return redirect(url_for('adminview'))

    new_course = Course(course_name=course_name, course_number=course_number,professor=professor, capacity=capacity, enrolled_students=0)
    db.session.add(new_course)
    db.session.commit()

    flash("Course added successfully!", "success")
    return render_template('adminview.html')


# Add dummy routes for student, teacher, and admin views
@app.route('/student/<username>')
def studentview(username):
    # Check if user is logged in (session)
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in

    user = User.query.filter_by(username=username).first()
    return render_template('studentview.html', person_name=user.person_name)

@app.route('/teacher/<username>')
def teacherview(username):
    # Check if user is logged in (session)
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in
    return render_template('teacherview.html')

@app.route('/admin/<username>')
def adminview(username):
    # Check if user is logged in (session)
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to login if not logged in
    return render_template('adminview.html')

@app.route('/get_all_courses', methods=['GET'])
def get_all_courses():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']

    enrolled_course_ids = {
        enrollment.course_id for enrollment in Enrollment.query.filter_by(user_id=user_id).all()
    }

    all_courses_list = Course.query.all()
    return render_template('allCourses.html', courses=all_courses_list, enrolled_course_ids=enrolled_course_ids)

@app.route('/register_for_course/<int:course_id>', methods=['GET', 'POST'])
def register_for_course(course_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to login if no user session

    course = Course.query.get(course_id)
    if course and course.has_capacity():
        # Increment the enrolled students for the course
        course.enrolled_students += 1
        db.session.commit()

        # You can also create a new enrollment record here if necessary
        enrollment = Enrollment(user_id=session['user_id'], course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()

        return jsonify({"message": "Successfully registered for the course"})
    else:
        return jsonify({"message": "Course is full or not found"}), 400

@app.route('/drop_course/<int:course_id>', methods=['POST'])
def drop_course(course_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to login if no user session

    user_id = session['user_id']

    # Check if the enrollment exists
    enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if enrollment:
        # Decrement the enrolled students for the course
        course = Course.query.get(course_id)
        if course:
            course.enrolled_students -= 1
            db.session.commit()

        # Remove the enrollment
        db.session.delete(enrollment)
        db.session.commit()

        return jsonify({"message": "Successfully dropped the course"})
    else:
        return jsonify({"message": "You are not enrolled in this course"}), 400


@app.route('/student_courses', methods=['GET'])
def student_courses():
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('index'))

    # Get the logged-in user's ID
    user_id = session['user_id']

    # Query enrollments and join with courses
    registered_courses = Enrollment.query.filter_by(user_id=user_id).join(Course).with_entities(
        Course.id,
        Course.course_name,
        Course.course_number,
        Course.professor,
        Course.enrolled_students,
    ).all()

    return render_template('student_courses.html', courses=registered_courses)

@app.route("/logout")
def logout():
    # Clear session data (log out the user)
    session.clear()  # Clear all session data
    return redirect(url_for('index')), flash("You have been logged out.", "info")  # Redirect to login page

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database is created
    app.run(debug=True)