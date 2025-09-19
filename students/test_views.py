from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json

from core.test_utils import APITestCase
from .models import Student, StudentExam, StudentExamResult
from core.exceptions import AuthenticationError, NotFoundError


class StudentLoginViewTest(APITestCase):
    
    def test_login_success(self):
        login_data = {
            'email': self.test_student.email_address,
            'password': 'testpass123'
        }
        
        with patch('students.services.AuthenticationService.authenticate_student') as mock_auth, \
             patch('students.services.AuthenticationService.generate_tokens') as mock_tokens:
            
            mock_auth.return_value = self.test_student
            mock_tokens.return_value = {
                'access': 'mock_access_token',
                'refresh': 'mock_refresh_token'
            }
            
            response = self.client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn('access', data)
            self.assertIn('refresh', data)
            self.assertIn('student', data)
            self.assertEqual(data['student']['id'], str(self.test_student.id))
            self.assertEqual(data['student']['email_address'], self.test_student.email_address)
    
    def test_login_missing_credentials(self):
        login_data = {'email': self.test_student.email_address}
        
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('Missing required fields', data['detail'])
    
    def test_login_invalid_credentials(self):
        login_data = {
            'email': self.test_student.email_address,
            'password': 'wrongpassword'
        }
        
        with patch('students.services.AuthenticationService.authenticate_student') as mock_auth:
            mock_auth.side_effect = AuthenticationError('Invalid credentials')
            
            response = self.client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 401)
            data = response.json()
            self.assertIn('detail', data)
            self.assertEqual(data['detail'], 'Invalid credentials')
    
    def test_login_invalid_json(self):
        response = self.client.post(
            '/api/auth/login',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('detail', data)


class StartExamViewTest(APITestCase):
    
    def setUp(self):
        super().setUp()
        self.client.defaults['HTTP_X_STUDENT_ID'] = str(self.test_student.id)
    
    def test_start_exam_success(self):
        exam_data = {'exam_id': str(self.test_exam.id)}
        
        with patch('students.services.ExamService.get_exam_by_id') as mock_get_exam, \
             patch('students.services.ExamService.get_or_create_student_exam') as mock_get_create:
            
            mock_get_exam.return_value = self.test_exam
            mock_get_create.return_value = self.student_exam
            
            with patch('students.views.request') as mock_request:
                mock_request.student = self.test_student
                
                response = self.client.post(
                    '/api/start-exam',
                    data=json.dumps(exam_data),
                    content_type='application/json'
                )
            
            self.assertEqual(response.status_code, 201)
            data = response.json()
            
            self.assertIn('student_exam_id', data)
            self.assertIn('exam_id', data)
            self.assertEqual(data['exam_id'], str(self.test_exam.id))
    
    def test_start_exam_missing_exam_id(self):
        exam_data = {}
        
        response = self.client.post(
            '/api/start-exam',
            data=json.dumps(exam_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('Missing required fields', data['detail'])
    
    def test_start_exam_not_found(self):
        exam_data = {'exam_id': '00000000-0000-0000-0000-000000000000'}
        
        with patch('students.services.ExamService.get_exam_by_id') as mock_get_exam:
            mock_get_exam.side_effect = NotFoundError('Exam not found')
            
            with patch('students.views.request') as mock_request:
                mock_request.student = self.test_student
                
                response = self.client.post(
                    '/api/start-exam',
                    data=json.dumps(exam_data),
                    content_type='application/json'
                )
            
            self.assertEqual(response.status_code, 404)
            data = response.json()
            self.assertIn('detail', data)
            self.assertEqual(data['detail'], 'Exam not found')


class SubmitAnswerViewTest(APITestCase):
    
    def setUp(self):
        super().setUp()
        self.submit_data = {
            'student_exam_id': str(self.student_exam.id),
            'exam_question_id': str(self.exam_question.id),
            'answer_id': str(self.correct_answer.id)
        }
    
    def test_submit_answer_success(self):
        with patch('students.services.ExamService.get_active_student_exam') as mock_get_exam, \
             patch('students.services.ExamService.get_exam_question') as mock_get_question, \
             patch('students.services.ExamService.get_question_answer') as mock_get_answer, \
             patch('students.services.AnswerSubmissionService.submit_answer') as mock_submit:
            
            mock_get_exam.return_value = self.student_exam
            mock_get_question.return_value = self.exam_question
            mock_get_answer.return_value = self.correct_answer
            
            mock_result = StudentExamResult.objects.create(
                student_exam=self.student_exam,
                exam_question=self.exam_question,
                answer=self.correct_answer,
                is_correct=True,
                score=20
            )
            mock_submit.return_value = mock_result
            
            with patch('students.views.request') as mock_request:
                mock_request.student = self.test_student
                
                response = self.client.post(
                    '/api/submit-answer',
                    data=json.dumps(self.submit_data),
                    content_type='application/json'
                )
            
            self.assertEqual(response.status_code, 201)
            data = response.json()
            
            self.assertIn('result_id', data)
            self.assertIn('student_exam_id', data)
            self.assertIn('exam_question_id', data)
            self.assertIn('answer_id', data)
            self.assertIn('score', data)
    
    def test_submit_answer_missing_fields(self):
        incomplete_data = {
            'student_exam_id': str(self.student_exam.id),
            'exam_question_id': str(self.exam_question.id)
        }
        
        response = self.client.post(
            '/api/submit-answer',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('Missing required fields', data['detail'])
    
    def test_submit_answer_exam_not_found(self):
        with patch('students.services.ExamService.get_active_student_exam') as mock_get_exam:
            mock_get_exam.side_effect = NotFoundError('Student exam not found')
            
            with patch('students.views.request') as mock_request:
                mock_request.student = self.test_student
                
                response = self.client.post(
                    '/api/submit-answer',
                    data=json.dumps(self.submit_data),
                    content_type='application/json'
                )
            
            self.assertEqual(response.status_code, 404)
            data = response.json()
            self.assertIn('detail', data)
            self.assertEqual(data['detail'], 'Student exam not found')


class CompleteExamViewTest(APITestCase):
    
    def test_complete_exam_success(self):
        exam_data = {'student_exam_id': str(self.student_exam.id)}
        
        with patch('students.services.ExamService.get_active_student_exam') as mock_get_exam, \
             patch('students.services.ExamCompletionService.complete_exam') as mock_complete:
            
            mock_get_exam.return_value = self.student_exam
            mock_complete.return_value = {
                'total_score': 80,
                'max_score': 100,
                'exam_result': 'pass',
                'end_time': '2023-01-01T12:00:00Z'
            }
            
            with patch('students.views.request') as mock_request:
                mock_request.student = self.test_student
                
                response = self.client.post(
                    '/api/complete-exam',
                    data=json.dumps(exam_data),
                    content_type='application/json'
                )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn('student_exam_id', data)
            self.assertIn('total_score', data)
            self.assertIn('max_score', data)
            self.assertIn('exam_result', data)
            self.assertIn('end_time', data)
    
    def test_complete_exam_missing_id(self):
        exam_data = {}
        
        response = self.client.post(
            '/api/complete-exam',
            data=json.dumps(exam_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('Missing required fields', data['detail'])
    
    def test_complete_exam_not_found(self):
        exam_data = {'student_exam_id': '00000000-0000-0000-0000-000000000000'}
        
        with patch('students.services.ExamService.get_active_student_exam') as mock_get_exam:
            mock_get_exam.side_effect = NotFoundError('Student exam not found')
            
            with patch('students.views.request') as mock_request:
                mock_request.student = self.test_student
                
                response = self.client.post(
                    '/api/complete-exam',
                    data=json.dumps(exam_data),
                    content_type='application/json'
                )
            
            self.assertEqual(response.status_code, 404)
            data = response.json()
            self.assertIn('detail', data)
            self.assertEqual(data['detail'], 'Student exam not found')