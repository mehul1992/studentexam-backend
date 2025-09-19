# Student Exams Backend (Django)

A Django-based backend system for managing student exams.  
This project provides secure APIs for student login, listing available exams, starting an exam, and analyzing results through a dashboard.

---

## 🚀 Features

- **Authentication & Login**: Secure login for students.  
- **Exam Management**: APIs to list available exams and start an exam.  
- **Results & Analysis**: Students can view their scores and track performance on the dashboard.  
- **Clean Architecture**: Built with **SOLID**, **DRY**, and **KISS** principles for maintainable and scalable code.  
- **Test Coverage**: Unit test cases included to ensure reliability and prevent regressions.  

---

## 🛠️ Tech Stack

- **Backend Framework**: Django  
- **Database**: PostgreSQL (default, can be swapped for MySQL or SQLite)  
- **Task Queue**: Celery + Redis (optional for async tasks)  
- **Testing**: Django Unit Tests (pytest compatible)  

---

## 📂 Project Structure

```
student-exams-backend/
│── exams/              # App for exam management
│   ├── models.py       # Database models (Students, Exams, Results)
│   ├── views.py        # API endpoints (login, list, start exam)
│   ├── serializers.py  # DRF serializers
│   ├── tests.py        # Unit test cases
│── student_dashboard/  # App for results & analysis
│── config/             # Django project settings
│── requirements.txt    # Python dependencies
│── manage.py           # Django CLI entry point
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/student-exams-backend.git
cd student-exams-backend
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply migrations
```bash
python manage.py migrate
```

### 5. Run the server
```bash
python manage.py runserver
```
Server will be available at: `http://127.0.0.1:8000/`

---

## 🔑 API Endpoints

| Endpoint              | Method | Description              |
|-----------------------|--------|--------------------------|
| `/api/login/`         | POST   | Student login            |
| `/api/exams/`         | GET    | List available exams     |
| `/api/exams/start/`   | POST   | Start an exam            |
| `/api/results/`       | GET    | View exam results        |
| `/api/dashboard/`     | GET    | Analyze score trends     |

---

## 🧪 Running Tests

```bash
python manage.py test
```

---

## 👨‍💻 Development Principles

- **SOLID**: Designed with clean architecture principles for long-term maintainability.  
- **DRY**: Reusable modules and minimal code duplication.  
- **KISS**: Simple, straightforward code to ensure clarity and reduce complexity.  


## 📄 License
This project is licensed under the MIT License.
