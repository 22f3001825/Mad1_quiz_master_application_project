from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Initialize SQLAlchemy globally

# User Model (Admin & Normal Users)
class User_Info(db.Model):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Integer, default=1)  # 0 = Admin, 1 = Normal User
    full_name = db.Column(db.String(150), nullable=False)
    qualification = db.Column(db.String(150))
    dob = db.Column(db.Date)

    scores = db.relationship('Score', backref='user', lazy='dynamic', cascade='all, delete-orphan')

# Subject Model
class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.String(300), nullable=False)

    chapters = db.relationship('Chapter', backref='subject', lazy='subquery', cascade='all, delete-orphan')

# Chapter Model
class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"), nullable=False)

    quizzes = db.relationship('Quiz', backref='chapter', lazy='subquery', cascade='all, delete-orphan')
    



# Quiz Model
class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete="CASCADE"), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)  
    duration_seconds = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.Text)

    questions = db.relationship('Question', backref='quiz', lazy='subquery', cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')


# Question Model
class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)
    statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  # Stores option number (1-4)
    explanation = db.Column(db.Text)

# Score Model
class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id', ondelete="CASCADE"), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    total_score = db.Column(db.Float, nullable=False)  # Use Float for percentage scores
    duration_seconds = db.Column(db.Integer, nullable=False)
