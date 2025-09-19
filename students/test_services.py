from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
import jwt
import datetime as dt

from core.test_utils import ServiceTestCase, create_test_student, create_test_exam_data
from core.exceptions import AuthenticationError, NotFoundError, ValidationError, BusinessLogicError
from .models import Student, StudentExam, StudentExamResult


User = get_user_model()


class AuthenticationServiceTest(ServiceTestCase):
    
    def test_authenticate_student_valid_credentials(self):
        email = self.test_student.email_address
        password = 'testpass123'
        
        student = self.auth_service.authenticate_student(email, password)
        
        self.assertEqual(student, self.test_student)
        self.assertEqual(student.email_address, email)
    
    def test_authenticate_student_invalid_email(self):
        with self.assertRaises(AuthenticationError) as context:
            self.auth_service.authenticate_student('invalid@example.com', 'password')
        
        self.assertIn('Invalid credentials', str(context.exception))
    
    def test_authenticate_student_invalid_password(self):
        with self.assertRaises(AuthenticationError) as context:
            self.auth_service.authenticate_student(
                self.test_student.email_address, 
                'wrongpassword'
            )
        
        self.assertIn('Invalid credentials', str(context.exception))
    
    def test_authenticate_student_inactive_student(self):
        self.test_student.is_active = False
        self.test_student.save()
        
        with self.assertRaises(AuthenticationError) as context:
            self.auth_service.authenticate_student(
                self.test_student.email_address, 
                'testpass123'
            )
        
        self.assertIn('Invalid credentials', str(context.exception))
    
    @override_settings(
        JWT_AUTH={
            'JWT_SECRET_KEY': 'test-secret',
            'JWT_ACCESS_TOKEN_LIFETIME': dt.timedelta(hours=1),
            'JWT_REFRESH_TOKEN_LIFETIME': dt.timedelta(days=7)
        }
    )
    def test_generate_tokens(self):
        tokens = self.auth_service.generate_tokens(self.test_student)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        
        access_token = tokens['access']
        decoded = jwt.decode(access_token, 'test-secret', algorithms=['HS256'])
        
        self.assertEqual(decoded['sub'], str(self.test_student.id))
        self.assertEqual(decoded['email'], self.test_student.email_address)
        self.assertEqual(decoded['type'], 'access')
        
        refresh_token = tokens['refresh']
        decoded_refresh = jwt.decode(refresh_token, 'test-secret', algorithms=['HS256'])
        
        self.assertEqual(decoded_refresh['sub'], str(self.test_student.id))
        self.assertEqual(decoded_refresh['type'], 'refresh')
    
    def test_generate_tokens_default_settings(self):
        tokens = self.auth_service.generate_tokens(self.test_student)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        
        access_token = tokens['access']
        decoded = jwt.decode(access_token, 'dev-secret-change-me', algorithms=['HS256'])
        self.assertEqual(decoded['sub'], str(self.test_student.id))


class ExamServiceTest(ServiceTestCase):
    
    def test_get_exam_by_id_valid(self):
        exam = self.exam_service.get_exam_by_id(str(self.test_exam.id))
        
        self.assertEqual(exam, self.test_exam)
        self.assertEqual(exam.exam_name, 'Python Programming Test')
    
    def test_get_exam_by_id_invalid(self):
        invalid_id = '00000000-0000-0000-0000-000000000000'
        
        with self.assertRaises(NotFoundError) as context:
            self.exam_service.get_exam_by_id(invalid_id)
        
        self.assertIn('Exam not found', str(context.exception))
    
    def test_get_exam_by_id_inactive(self):
        self.test_exam.is_active = False
        self.test_exam.save()
        
        with self.assertRaises(NotFoundError) as context:
            self.exam_service.get_exam_by_id(str(self.test_exam.id))
        
        self.assertIn('Exam not found', str(context.exception))
    
    def test_get_or_create_student_exam_new(self):
        new_student = create_test_student()
        
        student_exam = self.exam_service.get_or_create_student_exam(new_student, self.test_exam)
        
        self.assertEqual(student_exam.student, new_student)
        self.assertEqual(student_exam.exam, self.test_exam)
        self.assertEqual(student_exam.status, 'in_progress')
        self.assertEqual(student_exam.max_exam_score, self.test_exam.max_score)
        self.assertIsNotNone(student_exam.start_time)
    
    def test_get_or_create_student_exam_existing(self):
        student_exam = self.exam_service.get_or_create_student_exam(
            self.test_student, 
            self.test_exam
        )
        
        self.assertEqual(student_exam, self.student_exam)
    
    def test_get_active_student_exam_valid(self):
        student_exam = self.exam_service.get_active_student_exam(
            self.test_student, 
            str(self.student_exam.id)
        )
        
        self.assertEqual(student_exam, self.student_exam)
    
    def test_get_active_student_exam_invalid_id(self):
        invalid_id = '00000000-0000-0000-0000-000000000000'
        
        with self.assertRaises(NotFoundError) as context:
            self.exam_service.get_active_student_exam(self.test_student, invalid_id)
        
        self.assertIn('Student exam not found', str(context.exception))
    
    def test_get_active_student_exam_not_in_progress(self):
        self.student_exam.status = 'done'
        self.student_exam.save()
        
        with self.assertRaises(NotFoundError) as context:
            self.exam_service.get_active_student_exam(
                self.test_student, 
                str(self.student_exam.id)
            )
        
        self.assertIn('Student exam not found', str(context.exception))
    
    def test_get_exam_question_valid(self):
        exam_question = self.exam_service.get_exam_question(
            str(self.exam_question.id), 
            self.test_exam
        )
        
        self.assertEqual(exam_question, self.exam_question)
    
    def test_get_exam_question_invalid(self):
        invalid_id = '00000000-0000-0000-0000-000000000000'
        
        with self.assertRaises(NotFoundError) as context:
            self.exam_service.get_exam_question(invalid_id, self.test_exam)
        
        self.assertIn('Exam question not found', str(context.exception))
    
    def test_get_question_answer_valid(self):
        answer = self.exam_service.get_question_answer(
            str(self.correct_answer.id), 
            self.test_question
        )
        
        self.assertEqual(answer, self.correct_answer)
    
    def test_get_question_answer_invalid(self):
        invalid_id = '00000000-0000-0000-0000-000000000000'
        
        with self.assertRaises(NotFoundError) as context:
            self.exam_service.get_question_answer(invalid_id, self.test_question)
        
        self.assertIn('Answer not found', str(context.exception))


class AnswerSubmissionServiceTest(ServiceTestCase):
    
    def test_submit_answer_new_result(self):
        result = self.answer_service.submit_answer(
            self.student_exam, 
            self.exam_question, 
            self.correct_answer
        )
        
        self.assertEqual(result.student_exam, self.student_exam)
        self.assertEqual(result.exam_question, self.exam_question)
        self.assertEqual(result.answer, self.correct_answer)
        self.assertTrue(result.is_correct)
        self.assertEqual(result.score, 20)
    
    def test_submit_answer_incorrect_result(self):
        result = self.answer_service.submit_answer(
            self.student_exam, 
            self.exam_question, 
            self.incorrect_answer
        )
        
        self.assertEqual(result.answer, self.incorrect_answer)
        self.assertFalse(result.is_correct)
        self.assertEqual(result.score, 0)
    
    def test_submit_answer_update_existing(self):
        initial_result = self.answer_service.submit_answer(
            self.student_exam, 
            self.exam_question, 
            self.incorrect_answer
        )
        
        updated_result = self.answer_service.submit_answer(
            self.student_exam, 
            self.exam_question, 
            self.correct_answer
        )
        
        self.assertEqual(initial_result.id, updated_result.id)
        self.assertEqual(updated_result.answer, self.correct_answer)
        self.assertTrue(updated_result.is_correct)
        self.assertEqual(updated_result.score, 20)


class ExamCompletionServiceTest(ServiceTestCase):
    
    def setUp(self):
        super().setUp()
        StudentExamResult.objects.create(
            student_exam=self.student_exam,
            exam_question=self.exam_question,
            answer=self.correct_answer,
            is_correct=True,
            score=20
        )
    
    def test_complete_exam_pass(self):
        completion_data = self.completion_service.complete_exam(self.student_exam)
        
        self.student_exam.refresh_from_db()
        
        self.assertEqual(completion_data['total_score'], 20)
        self.assertEqual(completion_data['max_score'], 100)
        self.assertEqual(completion_data['exam_result'], 'pass')
        self.assertIsNotNone(completion_data['end_time'])
        
        self.assertEqual(self.student_exam.status, 'done')
        self.assertEqual(self.student_exam.total_score, 20)
        self.assertEqual(self.student_exam.exam_result, 'pass')
        self.assertIsNotNone(self.student_exam.end_time)
    
    def test_complete_exam_fail(self):
        self.test_exam.passing_score = 80
        self.test_exam.save()
        
        completion_data = self.completion_service.complete_exam(self.student_exam)
        
        self.assertEqual(completion_data['exam_result'], 'fail')
        
        self.student_exam.refresh_from_db()
        self.assertEqual(self.student_exam.exam_result, 'fail')
    
    def test_complete_exam_no_results(self):
        StudentExamResult.objects.filter(student_exam=self.student_exam).delete()
        
        completion_data = self.completion_service.complete_exam(self.student_exam)
        
        self.assertEqual(completion_data['total_score'], 0)
        self.assertEqual(completion_data['exam_result'], 'fail')