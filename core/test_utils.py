from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

from students.models import Student, StudentExam, StudentExamResult
from exams.models import Exam, Question, ExamQuestion, QuestionAnswer


User = get_user_model()


class BaseTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self._create_test_data()
    
    def _create_test_data(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.test_student = Student.objects.create(
            first_name='John',
            last_name='Doe',
            email_address='john.doe@example.com',
            date_of_brith='1990-01-01',
            country_code='+1',
            mobile_number='1234567890',
            is_active=True
        )
        self.test_student.set_password('testpass123')
        self.test_student.save()
        
        self.test_exam = Exam.objects.create(
            exam_name='Python Programming Test',
            category='Programming',
            description='Test your Python knowledge',
            number_of_questions=5,
            passing_score=70,
            max_score=100,
            exam_timer=3600,
            is_active=True,
            created_by=self.test_user
        )
        
        self.test_question = Question.objects.create(
            question_name='What is Python?',
            category='Programming',
            description='Basic Python question',
            is_active=True,
            created_by=self.test_user
        )
        
        self.correct_answer = QuestionAnswer.objects.create(
            question=self.test_question,
            answer='A programming language',
            is_correct=True,
            is_active=True
        )
        
        self.incorrect_answer = QuestionAnswer.objects.create(
            question=self.test_question,
            answer='A type of snake',
            is_correct=False,
            is_active=True
        )
        
        self.exam_question = ExamQuestion.objects.create(
            exam=self.test_exam,
            question=self.test_question,
            score=20,
            is_active=True
        )
        
        self.student_exam = StudentExam.objects.create(
            student=self.test_student,
            exam=self.test_exam,
            start_time=timezone.now(),
            status='in_progress',
            max_exam_score=self.test_exam.max_score
        )


class APITestCase(BaseTestCase):
    
    def setUp(self):
        super().setUp()
        self._setup_authentication()
    
    def _setup_authentication(self):
        self.auth_headers = {
            'HTTP_AUTHORIZATION': f'Bearer mock_token_for_{self.test_student.id}',
            'CONTENT_TYPE': 'application/json'
        }


class ModelTestCase(TestCase):
    
    def assertModelFields(self, model_class, expected_fields):
        model_fields = [field.name for field in model_class._meta.fields]
        for field in expected_fields:
            self.assertIn(field, model_fields, f"Field '{field}' not found in {model_class.__name__}")
    
    def assertModelConstraints(self, model_class, expected_constraints):
        pass


class ServiceTestCase(BaseTestCase):
    
    def setUp(self):
        super().setUp()
        from students.services import AuthenticationService, ExamService, AnswerSubmissionService, ExamCompletionService
        self.auth_service = AuthenticationService
        self.exam_service = ExamService
        self.answer_service = AnswerSubmissionService
        self.completion_service = ExamCompletionService


def create_test_exam_data():
    user = User.objects.create_user(
        username=f'testuser_{uuid.uuid4().hex[:8]}',
        email=f'test_{uuid.uuid4().hex[:8]}@example.com',
        password='testpass123'
    )
    
    exam = Exam.objects.create(
        exam_name=f'Test Exam {uuid.uuid4().hex[:8]}',
        category='Testing',
        description='Test exam for unit tests',
        number_of_questions=3,
        passing_score=60,
        max_score=100,
        exam_timer=1800,
        is_active=True,
        created_by=user
    )
    
    return user, exam


def create_test_question_with_answers(exam, user, question_text="Test Question"):
    question = Question.objects.create(
        question_name=question_text,
        category='Testing',
        description='Test question for unit tests',
        is_active=True,
        created_by=user
    )
    
    correct_answer = QuestionAnswer.objects.create(
        question=question,
        answer='Correct Answer',
        is_correct=True,
        is_active=True
    )
    
    incorrect_answer = QuestionAnswer.objects.create(
        question=question,
        answer='Incorrect Answer',
        is_correct=False,
        is_active=True
    )
    
    exam_question = ExamQuestion.objects.create(
        exam=exam,
        question=question,
        score=25,
        is_active=True
    )
    
    return question, [correct_answer, incorrect_answer], exam_question


def create_test_student():
    student = Student.objects.create(
        first_name=f'Test_{uuid.uuid4().hex[:8]}',
        last_name='Student',
        email_address=f'test_student_{uuid.uuid4().hex[:8]}@example.com',
        date_of_brith='1995-01-01',
        country_code='+1',
        mobile_number='1234567890',
        is_active=True
    )
    student.set_password('testpass123')
    student.save()
    return student