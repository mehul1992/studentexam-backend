from django.test import TestCase
from datetime import datetime
from .models import StudentExam, StudentExamResult
from core.test_utils import BaseTestCase
from .serializers import (
    StudentSerializer, StudentExamSerializer, StudentExamResultSerializer,
    ExamCompletionSerializer
)


class StudentSerializerTest(BaseTestCase):
    
    def test_student_to_dict(self):
        serialized = StudentSerializer.to_dict(self.test_student)
        
        expected_data = {
            'id': str(self.test_student.id),
            'first_name': self.test_student.first_name,
            'last_name': self.test_student.last_name,
            'email_address': self.test_student.email_address,
        }
        
        self.assertEqual(serialized, expected_data)
    
    def test_student_to_dict_with_none(self):
        with self.assertRaises(AttributeError):
            StudentSerializer.to_dict(None)


class StudentExamSerializerTest(BaseTestCase):
    
    def test_student_exam_to_dict(self):
        serialized = StudentExamSerializer.to_dict(self.student_exam)
        
        expected_data = {
            'student_exam_id': str(self.student_exam.id),
            'exam_id': str(self.student_exam.exam.id),
            'exam_name': self.student_exam.exam.exam_name,
            'start_time': self.student_exam.start_time.isoformat(),
            'status': self.student_exam.status,
            'max_exam_score': self.student_exam.max_exam_score,
            'exam_timer': self.student_exam.exam.exam_timer
        }
        
        self.assertEqual(serialized, expected_data)
    
    def test_student_exam_to_dict_with_none_start_time(self):
        self.student_exam.start_time = None
        self.student_exam.save()
        
        serialized = StudentExamSerializer.to_dict(self.student_exam)
        
        self.assertIsNone(serialized['start_time'])
    
    def test_student_exam_to_dict_with_none(self):
        with self.assertRaises(AttributeError):
            StudentExamSerializer.to_dict(None)


class StudentExamResultSerializerTest(BaseTestCase):
    
    def setUp(self):
        super().setUp()
        self.test_result = StudentExamResult.objects.create(
            student_exam=self.student_exam,
            exam_question=self.exam_question,
            answer=self.correct_answer,
            is_correct=True,
            score=20
        )
    
    def test_student_exam_result_to_dict(self):
        serialized = StudentExamResultSerializer.to_dict(self.test_result)
        
        expected_data = {
            'result_id': str(self.test_result.id),
            'student_exam_id': str(self.test_result.student_exam.id),
            'exam_question_id': str(self.test_result.exam_question.id),
            'answer_id': str(self.test_result.answer.id),
            'score': self.test_result.score,
            'is_correct': self.test_result.is_correct,
        }
        
        self.assertEqual(serialized, expected_data)
    
    def test_student_exam_result_to_dict_with_none(self):
        with self.assertRaises(AttributeError):
            StudentExamResultSerializer.to_dict(None)


class ExamCompletionSerializerTest(TestCase):
    
    def test_exam_completion_to_dict(self):
        student_exam_id = '12345678-1234-1234-1234-123456789012'
        completion_data = {
            'total_score': 85,
            'max_score': 100,
            'exam_result': 'pass',
            'end_time': '2023-01-01T12:00:00Z'
        }
        
        serialized = ExamCompletionSerializer.to_dict(student_exam_id, completion_data)
        
        expected_data = {
            'student_exam_id': student_exam_id,
            'total_score': 85,
            'max_score': 100,
            'exam_result': 'pass',
            'end_time': '2023-01-01T12:00:00Z'
        }
        
        self.assertEqual(serialized, expected_data)
    
    def test_exam_completion_to_dict_empty_completion_data(self):
        student_exam_id = '12345678-1234-1234-1234-123456789012'
        completion_data = {}
        
        serialized = ExamCompletionSerializer.to_dict(student_exam_id, completion_data)
        
        expected_data = {
            'student_exam_id': student_exam_id
        }
        
        self.assertEqual(serialized, expected_data)
    
    def test_exam_completion_to_dict_none_completion_data(self):
        student_exam_id = '12345678-1234-1234-1234-123456789012'
        completion_data = None
        
        with self.assertRaises(TypeError):
            ExamCompletionSerializer.to_dict(student_exam_id, completion_data)