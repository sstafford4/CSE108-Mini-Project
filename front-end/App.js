import React, { useState } from 'react';
import './App.css';

const availableCourses = [
    { name: 'Math 101', teacher: 'Ralph Jenkins', teacherUsername: 'rjenkins', time: 'MWF 10:00-10:50 AM', studentsEnrolled: '4/8' },
    { name: 'CS 162', teacher: 'Ammon Hepworth', teacherUsername: 'ahepworth', time: 'TR 3:00-3:50 PM', studentsEnrolled: '4/4' }
];

const enrolledCourses = [
    { name: 'Physics 121', teacher: 'Susan Walker', teacherUsername: 'swalker', time: 'TR 11:00-11:50 AM', studentsEnrolled: '5/10' },
    { name: 'CS 106', teacher: 'Ammon Hepworth', teacherUsername: 'ahepworth', time: 'MWF 2:00-2:50 PM', studentsEnrolled: '4/10' }
];

const coursesTaught = [
    { name: 'CS 106', teacher: 'Ammon Hepworth', teacherUsername: 'ahepworth', time: 'MWF 2:00-2:50 PM', studentsEnrolled: '4/10' },
    { name: 'CS 162', teacher: 'Ammon Hepworth', teacherUsername: 'ahepworth', time: 'TR 3:00-3:50 PM', studentsEnrolled: '4/4' }
];

function App() {
    const [view, setView] = useState('login');
    const [studentSubView, setStudentSubView] = useState('your-courses');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [studentName, setStudentName] = useState('');
    const [teacherName, setTeacherName] = useState('');
    const [studentCourses, setStudentCourses] = useState(enrolledCourses);
    const [availableCoursesList, setAvailableCoursesList] = useState(availableCourses);

    const handleLogin = (event) => {
        event.preventDefault();
        if (username === 'cnorris' && password === 'chris') {
            setStudentName('Chris Norris');
            setView('student-dashboard');
        } else if (username === 'ahepworth' && password === 'ammon') {
            setTeacherName('Ammon Hepworth');
            setView('teacher-dashboard');
        } else {
            alert('Invalid username or password');
        }
    };

    const handleLogout = () => {
        setUsername('');
        setPassword('');
        setView('login');
    };

    const addCourse = (courseName) => {
        const courseIndex = availableCoursesList.findIndex(course => course.name === courseName);
        if (courseIndex !== -1) {
            const course = availableCoursesList[courseIndex];
            setAvailableCoursesList(prevCourses => prevCourses.filter(course => course.name !== courseName));
            setStudentCourses(prevCourses => [...prevCourses, course]);
        }
    };

    const removeCourse = (courseName) => {
        const courseIndex = studentCourses.findIndex(course => course.name === courseName);
        if (courseIndex !== -1) {
            const course = studentCourses[courseIndex];
            setStudentCourses(prevCourses => prevCourses.filter(course => course.name !== courseName));
            setAvailableCoursesList(prevCourses => [...prevCourses, course]);
        }
    };

    return (
        <div className="container">
            {view === 'login' && (
                <div id="login-view" className="view active d-flex justify-content-center align-items-center">
                    <div className="login-form">
                        <img src="https://assets.foleon.com/eu-west-2/uploads-7e3kk3/16926/ucm_logo_rgb_m_3.60692d9749f2.png" alt="UC Merced Logo" className="uc-merced-logo" />
                        <h3>Login</h3>
                        <form onSubmit={handleLogin}>
                            <div className="mb-3">
                                <input
                                    type="text"
                                    className="form-control custom-input"
                                    id="username"
                                    placeholder="Username"
                                    required
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            </div>
                            <div className="mb-3">
                                <input
                                    type="password"
                                    className="form-control custom-input"
                                    id="password"
                                    placeholder="Password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                            <button type="submit" className="btn btn-primary d-block mx-auto">Sign In</button>
                        </form>
                    </div>
                </div>
            )}

            {view === 'student-dashboard' && (
                <div id="student-dashboard" className="view active">
                    <div className="text-center mb-3">
                        <h2>Welcome, {studentName}!</h2>
                        <h4>University of California, Merced</h4>
                        <a href="#" className="btn btn-link text-white" onClick={handleLogout}>Sign Out</a>
                    </div>

                    <div className="course-container">
                        <div className="d-flex justify-content-between mb-3">
                            <button
                                className={`btn btn-primary btn-toggle ${studentSubView === 'your-courses' ? 'active' : ''}`}
                                onClick={() => setStudentSubView('your-courses')}>
                                Your Courses
                            </button>
                            <button
                                className={`btn btn-primary btn-toggle ${studentSubView === 'add-courses' ? 'active' : ''}`}
                                onClick={() => setStudentSubView('add-courses')}>
                                Add Courses
                            </button>
                        </div>

                        {studentSubView === 'your-courses' && (
                            <div id="your-courses" className="view active">
                                <table className="table table-dark table-striped">
                                    <thead>
                                    <tr>
                                        <th>Course Name</th>
                                        <th>Teacher</th>
                                        <th>Time</th>
                                        <th>Students Enrolled</th>
                                        <th>Actions</th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {studentCourses.map((course) => (
                                        <tr key={course.name}>
                                            <td>{course.name}</td>
                                            <td>{course.teacher}</td>
                                            <td>{course.time}</td>
                                            <td>{course.studentsEnrolled}</td>
                                            <td>
                                                <button className="btn btn-danger" onClick={() => removeCourse(course.name)}>Remove</button>
                                            </td>
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                            </div>
                        )}

                        {studentSubView === 'add-courses' && (
                            <div id="add-courses" className="view active">
                                <table className="table table-dark table-striped">
                                    <thead>
                                    <tr>
                                        <th>Course Name</th>
                                        <th>Teacher</th>
                                        <th>Time</th>
                                        <th>Students Enrolled</th>
                                        <th>Actions</th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {availableCoursesList.map((course) => (
                                        <tr key={course.name}>
                                            <td>{course.name}</td>
                                            <td>{course.teacher}</td>
                                            <td>{course.time}</td>
                                            <td>{course.studentsEnrolled}</td>
                                            <td>
                                                <button className="btn btn-success" onClick={() => addCourse(course.name)}>Add</button>
                                            </td>
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {view === 'teacher-dashboard' && (
                <div id="teacher-dashboard" className="view active">
                    <div className="text-center mb-3">
                        <img
                            src="https://assets.foleon.com/eu-west-2/uploads-7e3kk3/16926/ucm_logo_rgb_m_3.60692d9749f2.png"
                            alt="UC Merced Logo"
                            className="uc-merced-logo"
                        />
                        <h2>Welcome, {teacherName}!</h2>
                        <h4>University of California, Merced</h4>
                        <a href="#" className="btn btn-link text-white" onClick={handleLogout}>
                            Sign out
                        </a>
                    </div>

                    <div className="course-container">
                        <h3>Your Courses</h3>
                        <table className="table table-dark table-striped">
                            <thead>
                            <tr>
                                <th>Course Name</th>
                                <th>Time</th>
                                <th>Students Enrolled</th>
                            </tr>
                            </thead>
                            <tbody>
                            {coursesTaught
                                .filter((course) => course.teacher) // Match by teacherUsername
                                .map((course) => (
                                    <tr key={course.name}>
                                        <td>{course.name}</td>
                                        <td>{course.time}</td>
                                        <td>{course.studentsEnrolled}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;