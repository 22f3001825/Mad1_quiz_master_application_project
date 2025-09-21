# kwiz - Exam Preparation Web Application(https://youtu.be/fGpqmnVGfcw?si=Wlm9g7p8HRj7Cr_C)

kwiz is a multi-user web application designed to help students prepare for exams efficiently. Built using **Flask**, **SQLite**, **HTML**, and **CSS**, it provides a seamless platform for administrators to create quizzes and for users to attempt them while tracking their performance with analytics.

## 🚀 Features

- **Quiz Management**: Admins can create and manage subjects, chapters, and quizzes.
- **Time-Based Tests**: Configurable quiz durations for better exam simulation.
- **Real-Time Scoring**: Instant evaluation of quiz attempts.
- **Performance Analytics**: Users can track progress with detailed reports and charts.
  
## 🛠 Tech Stack

### **Backend:**

- Flask, Flask-RESTful
- SQLAlchemy, SQLite
- Matplotlib, Seaborn (for data vizualization)

### **Frontend:**

- HTML , CSS 
- Bootstrap

## 📦 Installation & Setup

### **1. Create a Virtual Environment**

```sh
python3 -m venv venv
./venv/scripts/activate
```

### **2. Install Dependencies**

```sh
pip install -r requirement.txt
```

### **3. Start the Services**

#### **Backend **

```sh
flask run : python3 app.py
```


## 📊 Usage

1. **Admin Panel**: Create subjects, chapters, and quizzes.
2. **User Dashboard**: Attempt quizzes and view performance analytics.

---

**Developed by Ali Jawad as part of the Modern Application Development course at IIT Madras.**
