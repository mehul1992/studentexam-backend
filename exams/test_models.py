from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.test_utils import ModelTestCase
from .models import Exam, Question, ExamQuestion, QuestionAnswer


User = get_user_model()


class ExamModelTest(ModelTestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.exam_data = {
            'exam_name': 'Python Programming Test',
            'category': 'Programming',
            'description': 'Test your Python knowledge',
            'number_of_questions': 5,
            'passing_score': 70,
            'max_score': 100,
            'exam_timer': 3600,
            'is_active': True,
            'created_by': self.user
        }
    
    def test_exam_creation(self):
        exam = Exam.objects.create(**self.exam_data)
        
        self.assertEqual(exam.exam_name, 'Python Programming Test')
        self.assertEqual(exam.category, 'Programming')
        self.assertEqual(exam.description, 'Test your Python knowledge')
        self.assertEqual(exam.number_of_questions, 5)
        self.assertEqual(exam.passing_score, 70)
        self.assertEqual(exam.max_score, 100)
        self.assertEqual(exam.exam_timer, 3600)
        self.assertTrue(exam.is_active)
        self.assertEqual(exam.created_by, self.user)
        self.assertIsNotNone(exam.id)
    
    def test_exam_str_representation(self):
        exam = Exam.objects.create(**self.exam_data)
        expected_str = "Python Programming Test"
        self.assertEqual(str(exam), expected_str)
    
    def test_exam_model_fields(self):
        expected_fields = [
            'id', 'exam_name', 'category', 'description',
            'number_of_questions', 'passing_score', 'max_score',
            'exam_timer', 'is_active', 'created_at', 'updated_at',
            'created_by'
        ]
        self.assertModelFields(Exam, expected_fields)
    
    def test_exam_defaults(self):
        exam_data = self.exam_data.copy()
        del exam_data['is_active']
        
        exam = Exam.objects.create(**exam_data)
        self.assertTrue(exam.is_active)
    
    def test_exam_timer_validation(self):
        valid_timers = [0, 1800, 3600, 7200]
        for timer in valid_timers:
            exam_data = self.exam_data.copy()
            exam_data['exam_timer'] = timer
            exam = Exam.objects.create(**exam_data)
            self.assertEqual(exam.exam_timer, timer)


class QuestionModelTest(ModelTestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.question_data = {
            'question_name': 'What is Python?',
            'category': 'Programming',
            'description': 'Basic Python question',
            'is_active': True,
            'created_by': self.user
        }
    
    def test_question_creation(self):
        question = Question.objects.create(**self.question_data)
        
        self.assertEqual(question.question_name, 'What is Python?')
        self.assertEqual(question.category, 'Programming')
        self.assertEqual(question.description, 'Basic Python question')
        self.assertTrue(question.is_active)
        self.assertEqual(question.created_by, self.user)
        self.assertIsNotNone(question.id)
    
    def test_question_str_representation(self):
        question = Question.objects.create(**self.question_data)
        expected_str = "What is Python?"
        self.assertEqual(str(question), expected_str)
    
    def test_question_str_representation_long_text(self):
        long_question_data = self.question_data.copy()
        long_question_data['question_name'] = 'A' * 70
        
        question = Question.objects.create(**long_question_data)
        expected_str = 'A' * 60
        self.assertEqual(str(question), expected_str)
    
    def test_question_model_fields(self):
        expected_fields = [
            'id', 'question_name', 'category', 'description',
            'is_active', 'created_at', 'updated_at', 'created_by'
        ]
        self.assertModelFields(Question, expected_fields)
    
    def test_question_defaults(self):
        question_data = self.question_data.copy()
        del question_data['is_active']
        
        question = Question.objects.create(**question_data)
        self.assertTrue(question.is_active)


class ExamQuestionModelTest(ModelTestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.exam = Exam.objects.create(
            exam_name='Test Exam',
            category='Testing',
            description='Test exam',
            number_of_questions=1,
            passing_score=50,
            max_score=100,
            exam_timer=1800,
            is_active=True,
            created_by=self.user
        )
        
        self.question = Question.objects.create(
            question_name='Test Question',
            category='Testing',
            description='Test question',
            is_active=True,
            created_by=self.user
        )
    
    def test_exam_question_creation(self):
        exam_question = ExamQuestion.objects.create(
            exam=self.exam,
            question=self.question,
            score=25,
            is_active=True
        )
        
        self.assertEqual(exam_question.exam, self.exam)
        self.assertEqual(exam_question.question, self.question)
        self.assertEqual(exam_question.score, 25)
        self.assertTrue(exam_question.is_active)
        self.assertIsNotNone(exam_question.id)
    
    def test_exam_question_str_representation(self):
        exam_question = ExamQuestion.objects.create(
            exam=self.exam,
            question=self.question,
            score=25,
            is_active=True
        )
        
        expected_str = f"ExamQuestion(exam={self.exam.id}, question={self.question.id})"
        self.assertEqual(str(exam_question), expected_str)
    
    def test_exam_question_unique_together(self):
        ExamQuestion.objects.create(
            exam=self.exam,
            question=self.question,
            score=25,
            is_active=True
        )
        
        with self.assertRaises(Exception):
            ExamQuestion.objects.create(
                exam=self.exam,
                question=self.question,
                score=30,
                is_active=True
            )
    
    def test_exam_question_model_fields(self):
        expected_fields = [
            'id', 'exam', 'question', 'score',
            'is_active', 'created_at', 'updated_at'
        ]
        self.assertModelFields(ExamQuestion, expected_fields)


class QuestionAnswerModelTest(ModelTestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.question = Question.objects.create(
            question_name='Test Question',
            category='Testing',
            description='Test question',
            is_active=True,
            created_by=self.user
        )
    
    def test_question_answer_creation(self):
        answer = QuestionAnswer.objects.create(
            question=self.question,
            answer='This is a test answer',
            is_correct=True,
            is_active=True
        )
        
        self.assertEqual(answer.question, self.question)
        self.assertEqual(answer.answer, 'This is a test answer')
        self.assertTrue(answer.is_correct)
        self.assertTrue(answer.is_active)
        self.assertIsNotNone(answer.id)
    
    def test_question_answer_str_representation(self):
        answer = QuestionAnswer.objects.create(
            question=self.question,
            answer='Test Answer',
            is_correct=True,
            is_active=True
        )
        
        expected_str = f"Answer({answer.id}) for Question({self.question.id})"
        self.assertEqual(str(answer), expected_str)
    
    def test_question_answer_model_fields(self):
        expected_fields = [
            'id', 'question', 'answer', 'is_correct',
            'is_active', 'created_at', 'updated_at'
        ]
        self.assertModelFields(QuestionAnswer, expected_fields)
    
    def test_question_answer_defaults(self):
        answer = QuestionAnswer.objects.create(
            question=self.question,
            answer='Test Answer'
        )
        
        self.assertFalse(answer.is_correct)
        self.assertTrue(answer.is_active)