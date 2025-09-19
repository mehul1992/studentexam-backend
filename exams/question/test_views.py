from django.test import TestCase
from unittest.mock import patch

from core.test_utils import BaseTestCase
from exams.models import Exam, ExamQuestion
from exams.models import Question, QuestionAnswer


class QuestionListViewTest(BaseTestCase):
    
    def setUp(self):
        super().setUp()
        self.client.defaults['HTTP_X_STUDENT_ID'] = str(self.test_student.id)
    
    def test_get_questions_success(self):
        question2 = Question.objects.create(
            question_name='What is JavaScript?',
            category='Programming',
            description='Basic JavaScript question',
            is_active=True,
            created_by=self.test_user
        )
        
        answer2_correct = QuestionAnswer.objects.create(
            question=question2,
            answer='A programming language',
            is_correct=True,
            is_active=True
        )
        
        answer2_incorrect = QuestionAnswer.objects.create(
            question=question2,
            answer='A type of coffee',
            is_correct=False,
            is_active=True
        )
        
        ExamQuestion.objects.create(
            exam=self.test_exam,
            question=question2,
            score=25,
            is_active=True
        )
        
        inactive_question = Question.objects.create(
            question_name='Inactive Question',
            category='Programming',
            description='This question is inactive',
            is_active=False,
            created_by=self.test_user
        )
        
        ExamQuestion.objects.create(
            exam=self.test_exam,
            question=inactive_question,
            score=15,
            is_active=True
        )
        
        with patch('exams.question.views.request') as mock_request:
            mock_request.student = self.test_student
            
            response = self.client.get(f'/api/questions?exam_id={self.test_exam.id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('results', data)
        results = data['results']
        
        self.assertEqual(len(results), 2)
        
        question_names = [q['question_name'] for q in results]
        self.assertIn('What is Python?', question_names)
        self.assertIn('What is JavaScript?', question_names)
        self.assertNotIn('Inactive Question', question_names)
    
    def test_get_questions_missing_exam_id(self):
        with patch('exams.question.views.request') as mock_request:
            mock_request.student = self.test_student
            
            response = self.client.get('/api/questions')
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        
        self.assertIn('detail', data)
        self.assertEqual(data['detail'], 'exam_id is required')
    
    def test_get_questions_invalid_exam_id(self):
        invalid_exam_id = '00000000-0000-0000-0000-000000000000'
        
        with patch('exams.question.views.request') as mock_request:
            mock_request.student = self.test_student
            
            response = self.client.get(f'/api/questions?exam_id={invalid_exam_id}')
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        
        self.assertIn('detail', data)
        self.assertEqual(data['detail'], 'Exam not found')
    
    def test_get_questions_inactive_exam(self):
        self.test_exam.is_active = False
        self.test_exam.save()
        
        with patch('exams.question.views.request') as mock_request:
            mock_request.student = self.test_student
            
            response = self.client.get(f'/api/questions?exam_id={self.test_exam.id}')
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        
        self.assertIn('detail', data)
        self.assertEqual(data['detail'], 'Exam not found')
    
    def test_get_questions_response_structure(self):
        with patch('exams.question.views.request') as mock_request:
            mock_request.student = self.test_student
            
            response = self.client.get(f'/api/questions?exam_id={self.test_exam.id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)
        
        if data['results']:
            question = data['results'][0]
            expected_fields = [
                'id', 'exam_question_id', 'question_name', 'category',
                'description', 'score', 'answers'
            ]
            
            for field in expected_fields:
                self.assertIn(field, question, f"Field '{field}' missing from question data")
    
    def test_get_questions_serialized_data(self):
        with patch('exams.question.views.request') as mock_request:
            mock_request.student = self.test_student
            
            response = self.client.get(f'/api/questions?exam_id={self.test_exam.id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data['results']
        
        if results:
            question = results[0]
            
            self.assertEqual(question['question_name'], 'What is Python?')
            self.assertEqual(question['category'], 'Programming')
            self.assertEqual(question['description'], 'Basic Python question')
            self.assertEqual(question['score'], 20)
            
            self.assertIsInstance(question['id'], str)
            self.assertIsInstance(question['exam_question_id'], str)
            
            self.assertIn('answers', question)
            self.assertIsInstance(question['answers'], list)
            
            if question['answers']:
                answer = question['answers'][0]
                self.assertIn('id', answer)
                self.assertIn('answer', answer)
                self.assertIsInstance(answer['id'], str)
                self.assertIsInstance(answer['answer'], str)
    
    def test_get_questions_ordered_by_creation_date(self):
        question2 = Question.objects.create(
            question_name='Second Question',
            category='Programming',
            description='Second question',
            is_active=True,
            created_by=self.test_user
        )
        
        QuestionAnswer.objects.create(
            question=question2,
            answer='Answer for second question',
            is_correct=True,
            is_active=True
        )
        
        ExamQuestion.objects.create(
            exam=self.test_exam,
            question=question2,
            score=25,
            is_active=True
        )
        
        with patch('exams.question.views.request') as mock_request:
            mock_request.student = self.test_student
            
            response = self.client.get(f'/api/questions?exam_id={self.test_exam.id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data['results']
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['question_name'], 'What is Python?')
        self.assertEqual(results[1]['question_name'], 'Second Question')
    
    def test_get_questions_with_inactive_exam_question(self):
        question2 = Question.objects.create(
            question_name='Inactive Exam Question',
            category='Programming',
            description='Question with inactive exam link',
            is_active=True,
            created_by=self.test_user
        )
        
        QuestionAnswer.objects.create(
            question=question2,
            answer='Answer for inactive exam question',
            is_correct=True,
            is_active=True
        )
        
        ExamQuestion.objects.create(
            exam=self.test_exam,
            question=question2,
            score=25,
            is_active=False
        )
        
        with patch('exams.question.views.request') as mock_request:
            mock_request.student = self.test_student
            
            response = self.client.get(f'/api/questions?exam_id={self.test_exam.id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data['results']
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['question_name'], 'What is Python?')
    
    def test_get_questions_with_inactive_question(self):
        self.test_question.is_active = False
        self.test_question.save()
        
        with patch('exams.question.views.request') as mock_request:
            mock_request.student = self.test_student
            
            response = self.client.get(f'/api/questions?exam_id={self.test_exam.id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data['results']
        
        self.assertEqual(len(results), 0)
    
    def test_get_questions_optimized_query(self):
        with patch('exams.question.views.ExamQuestion.objects') as mock_objects:
            mock_queryset = mock_objects.select_related.return_value.filter.return_value.order_by.return_value
            
            with patch('exams.question.views.request') as mock_request:
                mock_request.student = self.test_student
                
                self.client.get(f'/api/questions?exam_id={self.test_exam.id}')
            
            mock_objects.select_related.assert_called_with('question')
            mock_queryset.filter.assert_called_once()
            mock_queryset.order_by.assert_called_with('created_at')