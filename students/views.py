"""
Views following SOLID, DRY, and KISS principles.
"""
from core.base_views import BaseAPIView, AuthenticatedAPIView
from core.exceptions import ExamAPIException
from .services import AuthenticationService, ExamService, AnswerSubmissionService, ExamCompletionService
from .serializers import (
    StudentSerializer, StudentExamSerializer, StudentExamResultSerializer, 
    ExamCompletionSerializer
)


class StudentLoginView(BaseAPIView):
    """
    Handles student authentication.
    Follows Single Responsibility Principle - only handles login.
    """
    
    def post(self, request):
        try:
            data = self.get_json_data(request)
            self.validate_required_fields(data, ['email', 'password'])
            
            # Authenticate student using service
            student = AuthenticationService.authenticate_student(
                data['email'], 
                data['password']
            )
            
            # Generate tokens using service
            tokens = AuthenticationService.generate_tokens(student)
            
            # Serialize student data
            student_data = StudentSerializer.to_dict(student)
            
            return self.success_response({
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'student': student_data
            })
            
        except ExamAPIException as e:
            return self.error_response(e.message, e.status_code)
        except Exception as e:
            return self.handle_exception(e)


class StartExamView(AuthenticatedAPIView):
    """
    Handles starting an exam for a student.
    Follows Single Responsibility Principle - only handles exam start.
    """
    
    def post(self, request):
        try:
            data = self.get_json_data(request)
            self.validate_required_fields(data, ['exam_id'])
            
            # Get exam using service
            exam = ExamService.get_exam_by_id(data['exam_id'])
            
            # Get or create student exam using service
            student_exam = ExamService.get_or_create_student_exam(request.student, exam)
            
            # Serialize response
            response_data = StudentExamSerializer.to_dict(student_exam)
            
            return self.success_response(response_data, 201)
            
        except ExamAPIException as e:
            return self.error_response(e.message, e.status_code)
        except Exception as e:
            return self.handle_exception(e)


class SubmitAnswerView(AuthenticatedAPIView):
    """
    Handles answer submission for exam questions.
    Follows Single Responsibility Principle - only handles answer submission.
    """
    
    def post(self, request):
        try:
            data = self.get_json_data(request)
            self.validate_required_fields(data, ['student_exam_id', 'exam_question_id', 'answer_id'])
            
            # Get student exam using service
            student_exam = ExamService.get_active_student_exam(
                request.student, 
                data['student_exam_id']
            )
            
            # Get exam question using service
            exam_question = ExamService.get_exam_question(
                data['exam_question_id'], 
                student_exam.exam
            )
            
            # Get question answer using service
            answer = ExamService.get_question_answer(
                data['answer_id'], 
                exam_question.question
            )
            
            # Submit answer using service
            result = AnswerSubmissionService.submit_answer(student_exam, exam_question, answer)
            
            # Serialize response
            response_data = StudentExamResultSerializer.to_dict(result)
            
            return self.success_response(response_data, 201)
            
        except ExamAPIException as e:
            return self.error_response(e.message, e.status_code)
        except Exception as e:
            return self.handle_exception(e)


class CompleteExamView(AuthenticatedAPIView):
    """
    Handles exam completion.
    Follows Single Responsibility Principle - only handles exam completion.
    """
    
    def post(self, request):
        try:
            data = self.get_json_data(request)
            self.validate_required_fields(data, ['student_exam_id'])
            
            # Get student exam using service
            student_exam = ExamService.get_active_student_exam(
                request.student, 
                data['student_exam_id']
            )
            
            # Complete exam using service
            completion_data = ExamCompletionService.complete_exam(student_exam)
            
            # Serialize response
            response_data = ExamCompletionSerializer.to_dict(data['student_exam_id'], completion_data)
            
            return self.success_response(response_data, 200)
            
        except ExamAPIException as e:
            return self.error_response(e.message, e.status_code)
        except Exception as e:
            return self.handle_exception(e)