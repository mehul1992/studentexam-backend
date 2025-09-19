from django.test import TestCase
from django.contrib.auth import get_user_model

from core.test_utils import BaseTestCase
from .models import Exam


User = get_user_model()


class ExamListViewTest(BaseTestCase):
    
    def test_get_exams_success(self):
        exam2 = Exam.objects.create(
            exam_name='JavaScript Test',
            category='Programming',
            description='Test your JavaScript knowledge',
            number_of_questions=3,
            passing_score=60,
            max_score=100,
            exam_timer=1800,
            is_active=True,
            created_by=self.test_user
        )
        
        exam3 = Exam.objects.create(
            exam_name='Inactive Exam',
            category='Programming',
            description='This exam is inactive',
            number_of_questions=2,
            passing_score=50,
            max_score=100,
            exam_timer=900,
            is_active=False,
            created_by=self.test_user
        )
        
        response = self.client.get('/api/exams')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('results', data)
        results = data['results']
        
        self.assertEqual(len(results), 2)
        
        exam_names = [exam['exam_name'] for exam in results]
        self.assertIn('Python Programming Test', exam_names)
        self.assertIn('JavaScript Test', exam_names)
        self.assertNotIn('Inactive Exam', exam_names)
    
    def test_get_exams_empty_list(self):
        Exam.objects.all().delete()
        
        response = self.client.get('/api/exams')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 0)
    
    def test_get_exams_only_active(self):
        self.test_exam.is_active = False
        self.test_exam.save()
        
        response = self.client.get('/api/exams')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 0)
    
    def test_get_exams_ordered_by_creation_date(self):
        exam2 = Exam.objects.create(
            exam_name='Second Exam',
            category='Programming',
            description='Second exam',
            number_of_questions=3,
            passing_score=60,
            max_score=100,
            exam_timer=1800,
            is_active=True,
            created_by=self.test_user
        )
        
        exam3 = Exam.objects.create(
            exam_name='Third Exam',
            category='Programming',
            description='Third exam',
            number_of_questions=2,
            passing_score=50,
            max_score=100,
            exam_timer=900,
            is_active=True,
            created_by=self.test_user
        )
        
        response = self.client.get('/api/exams')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data['results']
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['exam_name'], 'Third Exam')
        self.assertEqual(results[1]['exam_name'], 'Second Exam')
        self.assertEqual(results[2]['exam_name'], 'Python Programming Test')
    
    def test_get_exams_response_structure(self):
        response = self.client.get('/api/exams')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)
        
        if data['results']:
            exam = data['results'][0]
            expected_fields = [
                'id', 'exam_name', 'category', 'description',
                'number_of_questions', 'passing_score', 'max_score',
                'exam_timer', 'is_active', 'created_at', 'updated_at',
                'created_by'
            ]
            
            for field in expected_fields:
                self.assertIn(field, exam, f"Field '{field}' missing from exam data")
    
    def test_get_exams_serialized_data(self):
        response = self.client.get('/api/exams')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data['results']
        
        if results:
            exam = results[0]
            
            self.assertEqual(exam['exam_name'], 'Python Programming Test')
            self.assertEqual(exam['category'], 'Programming')
            self.assertEqual(exam['description'], 'Test your Python knowledge')
            self.assertEqual(exam['number_of_questions'], 5)
            self.assertEqual(exam['passing_score'], 70)
            self.assertEqual(exam['max_score'], 100)
            self.assertEqual(exam['exam_timer'], 3600)
            self.assertTrue(exam['is_active'])
            self.assertEqual(exam['created_by'], self.test_user.id)
            
            self.assertIsInstance(exam['created_at'], str)
            self.assertIsInstance(exam['updated_at'], str)
            
            self.assertIsInstance(exam['id'], str)
            self.assertGreater(len(exam['id']), 30)