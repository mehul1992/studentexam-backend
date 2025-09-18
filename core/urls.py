"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path
from students.views import StudentLoginView, StartExamView, SubmitAnswerView, CompleteExamView
from exams.views import ExamListView
from exams.question.views import QuestionListView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication endpoints
    path('api/auth/login', StudentLoginView.as_view(), name='student-login'),
    
    # Exam endpoints
    path('api/exams', ExamListView.as_view(), name='exams-list'),
    path('api/questions', QuestionListView.as_view(), name='questions-list'),
    
    # Student exam endpoints
    path('api/start-exam', StartExamView.as_view(), name='start-exam'),
    path('api/submit-answer', SubmitAnswerView.as_view(), name='submit-answer'),
    path('api/complete-exam', CompleteExamView.as_view(), name='complete-exam'),
]