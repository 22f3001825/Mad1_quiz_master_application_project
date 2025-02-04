from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, abort
from datetime import datetime
from backend.models import *  
from app import app  
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload


#  Home & Auth Pages
@app.route('/')
def index():
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('email')
        pwd = request.form.get('password')

        # Query the user by email and password
        usr = User_Info.query.filter_by(email=uname).first()

        if usr and usr.password == pwd:  
            session['user_email'] = usr.email  # Store the email or any unique identifier
            
            # Check if the user is an admin (role == 0 for admin)
            if usr.role == 0:  # Admin
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
            else:  # Regular user
                return redirect(url_for('user_dashboard'))  # Redirect to user dashboard
        else:
            return render_template('login.html', msg='Invalid credentials!')

    return render_template('login.html', msg='')


@app.route('/register', methods=["GET", "POST"])
def signup():  # 'signup' function remains unchanged
    if request.method == 'POST':
        uname = request.form.get('email')
        pwd = request.form.get('password')
        fullname = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob_string = request.form.get('dob')     
        dob = datetime.strptime(dob_string, "%Y-%m-%d").date()

        usr = User_Info.query.filter_by(email=uname).first()
        if usr:
            return render_template('signup.html', msg='Email already registered!')

        new_usr = User_Info(email=uname, password=pwd, full_name=fullname, qualification=qualification, dob=dob)
        db.session.add(new_usr)
        db.session.commit()

        return redirect(url_for('login'))  # Redirect to login after successful signup

    return render_template('signup.html', msg='')

@app.route('/logout')
def logout():
    session.pop('user_email', None)  # Remove the user from the session
    return redirect(url_for('index'))  # Redirect to the homepage or login page




# Admin Routes (Inside templates/admin)

@app.route('/admin/dashboard')
def admin_dashboard():
    subjects = Subject.query.all()  # Get all subjects

    # Fetch quizzes for each chapter
    for subject in subjects:
        for chapter in subject.chapters:
            # Fetch quizzes associated with each chapter
            chapter.quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()

    return render_template('admin/admin_dashboard.html', subjects=subjects)


@app.route('/admin/new_subject', methods=['GET', 'POST'])
def new_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/admin_new_subject.html')

@app.route('/admin/delete_subject/<int:subject_id>', methods=['GET'])
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))  # Redirect back to the dashboard


@app.route('/admin/new_chapter', methods=['GET', 'POST'])
def new_chapter():
    subject_id = request.args.get('subject_id')
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        subject_id = request.form.get('subject_id')
    
        # Ensure that a valid subject is selected
        subject = Subject.query.get(subject_id)
        if subject:
            new_chapter = Chapter(name=name, description=description, subject_id=subject.id)
            db.session.add(new_chapter)
            db.session.commit()
            flash('Chapter added successfully!', 'success')  # Flash success message
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid subject selected', 'danger')  # Flash error message
            return redirect(url_for('admin_dashboard'))
    
    # If GET request, render the form with the available subjects
    subjects = Subject.query.all()
    return render_template(
        'admin/admin_new_chapter.html', 
        subjects=subjects, 
        selected_subject_id=subject_id
    )

@app.route('/admin/delete_chapter/<int:chapter_id>', methods=['GET'])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if chapter:
        db.session.delete(chapter)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))  # Redirect back to the dashboard

@app.route('/admin/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form['description']
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))  # Redirect back to the dashboard

    return render_template('admin/edit_chapter.html', chapter=chapter)



@app.route('/admin/new_question', methods=['GET', 'POST'])
def new_question():
    if request.method == 'POST':
        statement = request.form.get('statement')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')
        quiz_id = request.form.get('quiz_id')  # Now correctly fetching quiz_id

        quiz = Quiz.query.get(quiz_id)  # Fetch the Quiz
        if quiz:
            new_question = Question(
                statement=statement,
                option1=option1,
                option2=option2,
                option3=option3,
                option4=option4,
                correct_option=int(correct_option),
                quiz_id=quiz.id  # Correctly linking question to quiz
            )
            db.session.add(new_question)
            db.session.commit()
            flash("Question added successfully!", "success")  # Flash message
            return redirect(url_for('quiz_management'))  # Redirect to quiz management page

    quizzes = Quiz.query.all()  # Fetch all quizzes instead of chapters
    return render_template('admin/admin_new_question.html', quizzes=quizzes)



from datetime import datetime


@app.route('/admin/new_quiz', methods=['GET', 'POST'])
def new_quiz():
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        date_of_quiz = request.form.get('date_of_quiz')
        duration_str = request.form.get('duration')

        try:
            # Convert date string to date object
            date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%d').date()

            # Convert "hh:mm" format into seconds
            hours, minutes = map(int, duration_str.split(":"))
            duration_seconds = (hours * 3600) + (minutes * 60)

            chapter = Chapter.query.get(chapter_id)
            if chapter:
                new_quiz = Quiz(
                    chapter_id=chapter.id,
                    date_of_quiz=date_of_quiz,
                    duration_seconds=duration_seconds
                )
                db.session.add(new_quiz)
                db.session.commit()

                return redirect(url_for('quiz_management'))  
        
        except ValueError:
            flash("Invalid date or duration format. Please use YYYY-MM-DD and HH:MM.", "danger")

    chapters = Chapter.query.all()
    return render_template('admin/admin_new_quiz.html', chapters=chapters)



@app.route('/admin/quiz_management', methods=['GET'])
def quiz_management():
    # Fetch all chapters with quizzes
    chapters = Chapter.query.options(db.joinedload(Chapter.quizzes)).all()
    
    # Fetch all quizzes separately
    quizzes = Quiz.query.all()

    return render_template('admin/admin_quiz_management.html', chapters=chapters, quizzes=quizzes)



@app.route('/admin/delete_quiz/<quiz_id>', methods=['GET'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if quiz:
        db.session.delete(quiz)
        db.session.commit()
    return redirect(url_for('quiz_management'))


@app.route('/admin/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    # Fetch the quiz to be edited
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Fetch all chapters for the chapter selection dropdown
    chapters = Chapter.query.all()

    if request.method == 'POST':
        # Get form data
        chapter_id = request.form.get('chapter_id')
        date_of_quiz = request.form.get('date_of_quiz')
        duration_str = request.form.get('duration')
        remarks = request.form.get('remarks')

        try:
            # Convert the date string to a date object
            date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%d').date()

            # Convert hh:mm format into seconds
            hours, minutes = map(int, duration_str.split(":"))
            duration_seconds = (hours * 3600) + (minutes * 60)

            # Get the selected chapter
            chapter = Chapter.query.get(chapter_id)
            if chapter:
                # Update the quiz details
                quiz.chapter_id = chapter.id
                quiz.date_of_quiz = date_of_quiz
                quiz.duration_seconds = duration_seconds
                quiz.remarks = remarks  # Update remarks

                # Commit the changes to the database
                db.session.commit()

                flash('Quiz updated successfully!', 'success')
                return redirect(url_for('quiz_management'))  # Redirect to quiz management page

        except ValueError:
            flash("Invalid date or duration format. Please use YYYY-MM-DD and HH:MM.", "danger")

    # Render the edit quiz form
    return render_template('admin/edit_quiz.html', quiz=quiz, chapters=chapters)


import matplotlib.pyplot as plt
import seaborn as sns
import os
from flask import render_template, url_for
from io import BytesIO
import base64

@app.route('/admin/summary_charts')
def admin_summary_charts():
    total_quizzes = Quiz.query.count()
    total_attempts = Score.query.count()
    average_score = round(db.session.query(db.func.avg(Score.total_score)).scalar() or 0, 2)
    total_subjects = Subject.query.count()

    # Fetch top performers
    top_performers = db.session.query(
        User_Info.full_name, db.func.avg(Score.total_score).label('score')
    ).join(Score, Score.user_id == User_Info.id).group_by(User_Info.full_name).order_by(db.desc('score')).limit(5).all()

    # Fetch latest quiz attempts
    latest_attempts = db.session.query(
        User_Info.full_name, Score.total_score, Quiz.id
    ).join(Score, Score.user_id == User_Info.id).join(Quiz, Quiz.id == Score.quiz_id).order_by(Score.timestamp.desc()).limit(5).all()

    # Prepare Data for Charts
    top_performer_names = [p[0] for p in top_performers]
    top_performer_scores = [p[1] for p in top_performers]

    # Ensure static/images directory exists
    os.makedirs("static/images", exist_ok=True)

    #Chart 1: Top Performers
    plt.figure(figsize=(8, 5))
    sns.barplot(x=top_performer_scores, y=top_performer_names, palette="viridis")
    plt.xlabel("Average Score (%)")
    plt.ylabel("Top Performers")
    plt.title("Top Performers in Quiz")
    plt.tight_layout()
    plt.savefig("static/images/top_performers.png")
    plt.close()

    # Chart 2: Quiz Attempts Over Time
    attempts_by_date = db.session.query(Score.timestamp, db.func.count(Score.id)).group_by(Score.timestamp).all()
    
    if attempts_by_date:
        dates, counts = zip(*attempts_by_date)
        plt.figure(figsize=(8, 5))
        plt.plot(dates, counts, marker='o', linestyle='-', color='b')
        plt.xlabel("Date")
        plt.ylabel("Number of Attempts")
        plt.title("Quiz Attempts Over Time")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("static/images/quiz_attempts.png")
        plt.close()

    return render_template(
        'admin/admin_new_summary.html',
        total_quizzes=total_quizzes,
        total_attempts=total_attempts,
        average_score=average_score,
        total_subjects=total_subjects,
        top_performers=[{"name": p[0], "score": p[1]} for p in top_performers],
        latest_attempts=[{"user": a[0], "score": a[1], "quiz_name": f"Quiz {a[2]}"} for a in latest_attempts]
    )




# User Routes (Inside templates/user)


@app.route('/user/dashboard')
def user_dashboard():
    # Retrieve user from the session or database
    user_email = session.get('user_email')  # Assuming email is stored in the session
    user = User_Info.query.filter_by(email=user_email).first() if user_email else None

    if not user:
        return redirect('/login')  # Redirect to login if no user found

    # Fetch upcoming quizzes 
    from datetime import datetime
    quizzes = Quiz.query.filter(Quiz.date_of_quiz >= datetime.now()).all()

    return render_template('user/user_dashboard.html', user=user, quizzes=quizzes)


@app.route('/user/scores')
def user_scores():
    user_email = session.get('user_email')
    user = User_Info.query.filter_by(email=user_email).first() if user_email else None

    if not user:
        return redirect('/login')

    scores = Score.query.filter_by(user_id=user.id).all()
    return render_template('user/user_scores.html', scores=scores)


@app.route('/user/start_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def user_start_quiz(quiz_id):
    user_email = session.get('user_email')
    user = User_Info.query.filter_by(email=user_email).first() if user_email else None

    if not user:
        return redirect('/login')

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return "Quiz not found", 404

    questions = quiz.questions
    total_questions = len(questions)

    # Initialize quiz progress if not already present
    if 'quiz_progress' not in session:
        session['quiz_progress'] = {'answers': {}, 'current_index': 0}
    elif 'current_index' not in session['quiz_progress']:
        session['quiz_progress']['current_index'] = 0

    # Get the current index safely
    try:
        question_index = int(session['quiz_progress'].get('current_index', 0))
    except ValueError:
        question_index = 0

    if request.method == 'POST':
        action = request.form.get('action')
        question_id = request.form.get('question_id')
        selected_option = request.form.get('selected_option')

        # Validate and store answers
        try:
            question_id = int(question_id)
            selected_option = int(selected_option)
        except (ValueError, TypeError):
            return "Invalid question ID or selected option", 400

        session['quiz_progress']['answers'][str(question_id)] = selected_option
        session.modified = True

        # Handle button actions
        if action == 'submit':
            return redirect(url_for('user_submit_quiz', quiz_id=quiz_id))
        elif action == 'back' and question_index > 0:
            session['quiz_progress']['current_index'] = question_index - 1
        elif action == 'next' and question_index < total_questions - 1:
            session['quiz_progress']['current_index'] = question_index + 1

        session.modified = True
        return redirect(url_for('user_start_quiz', quiz_id=quiz_id))

    # Redirect if quiz is complete
    if question_index >= total_questions:
        return redirect(url_for('user_submit_quiz', quiz_id=quiz_id))

    # Fetch the current question
    question = questions[question_index]
    print(question)

    return render_template(
        'user/user_start_quiz.html',
        quiz=quiz,
        question=question,
        current_question_index=question_index,
        total_questions=total_questions
    )


@app.route('/user/submit_quiz/<int:quiz_id>', methods=['GET'])
def user_submit_quiz(quiz_id):
    user_email = session.get('user_email')
    user = User_Info.query.filter_by(email=user_email).first() if user_email else None

    if not user:
        return redirect('/login')

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return "Quiz not found", 404

    # Retrieve user's answers
    quiz_progress = session.get('quiz_progress', {})  # Use get() instead of pop()
    user_answers = quiz_progress.get('answers', {})

    # Evaluate score
    correct_count = sum(
        1 for question in quiz.questions
        if int(user_answers.get(str(question.id), -1)) == question.correct_option
    )

    total_questions = len(quiz.questions)

    # Proper calculation of the score
    total_score = ((correct_count / total_questions) * 100) if total_questions > 0 else 0

    # Save score in the database
    existing_score = Score.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()

    if existing_score:
        existing_score.total_score = total_score
        db.session.commit()
    else:
        score_entry = Score(user_id=user.id, quiz_id=quiz.id, total_score=total_score)
        db.session.add(score_entry)
        db.session.commit()

    scores = Score.query.filter_by(user_id=user.id).all()

    # Clear the quiz progress
    session.pop('quiz_progress', None)

    return render_template('user/user_scores.html', scores=scores, total_score=total_score, message="Quiz submitted successfully!")



@app.route('/user/view_quiz/<quiz_id>')
def user_view_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if quiz:
        return render_template('user/user_view_quiz.html', quiz=quiz, divmod=divmod)
    else:
        return "Quiz not found", 404





@app.route('/user/summary_charts')
def user_summary_charts():
    os.makedirs("static/images", exist_ok=True)

    # Subject-wise No. of Quizzes
    subject_data = db.session.query(
        Subject.name, func.count(Quiz.id)
    ).select_from(Subject) \
    .join(Chapter, Chapter.subject_id == Subject.id) \
    .join(Quiz, Quiz.chapter_id == Chapter.id) \
    .group_by(Subject.name).all()

    subject_labels = [row[0] for row in subject_data]
    subject_counts = [row[1] for row in subject_data]

    

    return render_template(
        'user/user_summary_chart.html',
        subject_chart=url_for('static', filename='images/subject_quizzes.png'),
        month_chart=url_for('static', filename='images/month_quizzes.png')
    )




