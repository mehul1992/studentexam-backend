from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date

from core.test_utils import ModelTestCase, create_test_student
from .models import Student, StudentExam, StudentExamResult


User = get_user_model()


class StudentModelTest(ModelTestCase):
    
    def setUp(self):
        self.student_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email_address': 'john.doe@example.com',
            'date_of_brith': date(1990, 1, 1),
            'country_code': '+1',
            'mobile_number': '1234567890',
            'is_active': True
        }
    
    def test_student_creation(self):
        student = Student.objects.create(**self.student_data)
        
        self.assertEqual(student.first_name, 'John')
        self.assertEqual(student.last_name, 'Doe')
        self.assertEqual(student.email_address, 'john.doe@example.com')
        self.assertEqual(student.date_of_brith, date(1990, 1, 1))
        self.assertEqual(student.country_code, '+1')
        self.assertEqual(student.mobile_number, '1234567890')
        self.assertTrue(student.is_active)
        self.assertIsNotNone(student.id)
    
    def test_student_str_representation(self):
        student = Student.objects.create(**self.student_data)
        expected_str = "John Doe"
        self.assertEqual(str(student), expected_str)
    
    def test_student_unique_email(self):
        Student.objects.create(**self.student_data)
        
        duplicate_data = self.student_data.copy()
        with self.assertRaises(Exception):
            Student.objects.create(**duplicate_data)
    
    def test_student_password_hashing(self):
        student = Student.objects.create(**self.student_data)
        
        raw_password = 'testpass123'
        student.set_password(raw_password)
        student.save()
        
        self.assertNotEqual(student.password, raw_password)
        self.assertTrue(student.password.startswith(('pbkdf2_', 'argon2$', 'bcrypt$')))
        
        self.assertTrue(student.check_password(raw_password))
        self.assertFalse(student.check_password('wrongpassword'))
    
    def test_student_model_fields(self):
        expected_fields = [
            'id', 'first_name', 'last_name', 'email_address',
            'password', 'date_of_brith', 'country_code', 'mobile_number',
            'created_at', 'updated_at', 'is_active'
        ]
        self.assertModelFields(Student, expected_fields)
    
    def test_student_defaults(self):
        student = Student.objects.create(**self.student_data)
        self.assertTrue(student.is_active)


class StudentExamModelTest(ModelTestCase):
    
    def setUp(self):
        from core.test_utils import BaseTestCase
        self.base = BaseTestCase()
        self.base._create_test_data()
        
        self.student = self.base.test_student
        self.exam = self.base.test_exam
    
    def test_student_exam_creation(self):
        student_exam = StudentExam.objects.create(
            student=self.student,
            exam=self.exam,
            start_time=timezone.now(),
            status='in_progress',
            max_exam_score=self.exam.max_score
        )
        
        self.assertEqual(student_exam.student, self.student)
        self.assertEqual(student_exam.exam, self.exam)
        self.assertEqual(student_exam.status, 'in_progress')
        self.assertEqual(student_exam.max_exam_score, self.exam.max_score)
        self.assertIsNone(student_exam.end_time)
        self.assertEqual(student_exam.total_score, 0)
        self.assertIsNone(student_exam.exam_result)
    
    def test_student_exam_str_representation(self):
        student_exam = StudentExam.objects.create(
            student=self.student,
            exam=self.exam,
            start_time=timezone.now(),
            status='in_progress',
            max_exam_score=self.exam.max_score
        )
        
        expected_str = f"StudentExam({self.student.id}, {self.exam.id})"
        self.assertEqual(str(student_exam), expected_str)
    
    def test_student_exam_status_choices(self):
        student_exam = StudentExam.objects.create(
            student=self.student,
            exam=self.exam,
            start_time=timezone.now(),
            status='pending',
            max_exam_score=self.exam.max_score
        )
        
        valid_statuses = ['pending', 'in_progress', 'done']
        for status in valid_statuses:
            student_exam.status = status
            student_exam.save()
            self.assertEqual(student_exam.status, status)
    
    def test_student_exam_result_choices(self):
        student_exam = StudentExam.objects.create(
            student=self.student,
            exam=self.exam,
            start_time=timezone.now(),
            status='done',
            max_exam_score=self.exam.max_score,
            exam_result='pass'
        )
        
        valid_results = ['pass', 'fail']
        for result in valid_results:
            student_exam.exam_result = result
            student_exam.save()
            self.assertEqual(student_exam.exam_result, result)
    
    def test_student_exam_score_validation(self):
        student_exam = StudentExam.objects.create(
            student=self.student,
            exam=self.exam,
            start_time=timezone.now(),
            status='in_progress',
            max_exam_score=self.exam.max_score
        )
        
        valid_scores = [0, 50, 100]
        for score in valid_scores:
            student_exam.total_score = score
            student_exam.save()
            self.assertEqual(student_exam.total_score, score)
    
    def test_student_exam_model_fields(self):
        expected_fields = [
            'id', 'student', 'exam', 'start_time', 'end_time',
            'total_score', 'status', 'exam_result', 'max_exam_score',
            'created_at', 'updated_at'
        ]
        self.assertModelFields(StudentExam, expected_fields)


class StudentExamResultModelTest(ModelTestCase):
    
    def setUp(self):
        from core.test_utils import BaseTestCase
        self.base = BaseTestCase()
        self.base._create_test_data()
        
        self.student_exam = self.base.student_exam
        self.exam_question = self.base.exam_question
        self.answer = self.base.correct_answer
    
    def test_student_exam_result_creation(self):
        result = StudentExamResult.objects.create(
            student_exam=self.student_exam,
            exam_question=self.exam_question,
            answer=self.answer,
            is_correct=True,
            score=20
        )
        
        self.assertEqual(result.student_exam, self.student_exam)
        self.assertEqual(result.exam_question, self.exam_question)
        self.assertEqual(result.answer, self.answer)
        self.assertTrue(result.is_correct)
        self.assertEqual(result.score, 20)
    
    def test_student_exam_result_str_representation(self):
        result = StudentExamResult.objects.create(
            student_exam=self.student_exam,
            exam_question=self.exam_question,
            answer=self.answer,
            is_correct=True,
            score=20
        )
        
        expected_str = f"StudentExamResult({self.student_exam.id}, {self.exam_question.id})"
        self.assertEqual(str(result), expected_str)
    
    def test_student_exam_result_model_fields(self):
        expected_fields = [
            'id', 'student_exam', 'exam_question', 'answer',
            'is_correct', 'score'
        ]
        self.assertModelFields(StudentExamResult, expected_fields)
    
    def test_student_exam_result_score_validation(self):
        result = StudentExamResult.objects.create(
            student_exam=self.student_exam,
            exam_question=self.exam_question,
            answer=self.answer,
            is_correct=True,
            score=0
        )
        
        valid_scores = [0, 10, 25, 100]
        for score in valid_scores:
            result.score = score
            result.save()
            self.assertEqual(result.score, score)