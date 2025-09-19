from core.base_views import BaseAPIView, AuthenticatedAPIView
from core.exceptions import ExamAPIException
from .services import AuthenticationService, ExamService, AnswerSubmissionService, ExamCompletionService
from .serializers import (
    StudentSerializer, StudentExamSerializer, StudentExamResultSerializer, 
    ExamCompletionSerializer
)


class StudentLoginView(BaseAPIView):
    
    def post(self, request):
        try:
            data = self.get_json_data(request)
            self.validate_required_fields(data, ['email', 'password'])
            
            student = AuthenticationService.authenticate_student(
                data['email'], 
                data['password']
            )
            
            tokens = AuthenticationService.generate_tokens(student)
            
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
    
    def post(self, request):
        try:
            data = self.get_json_data(request)
            self.validate_required_fields(data, ['exam_id'])
            
            exam = ExamService.get_exam_by_id(data['exam_id'])
            
            student_exam = ExamService.get_or_create_student_exam(request.student, exam)
            
            response_data = StudentExamSerializer.to_dict(student_exam)
            
            return self.success_response(response_data, 201)
            
        except ExamAPIException as e:
            return self.error_response(e.message, e.status_code)
        except Exception as e:
            return self.handle_exception(e)


class SubmitAnswerView(AuthenticatedAPIView):
    
    def post(self, request):
        try:
            data = self.get_json_data(request)
            self.validate_required_fields(data, ['student_exam_id', 'exam_question_id', 'answer_id'])
            
            student_exam = ExamService.get_active_student_exam(
                request.student, 
                data['student_exam_id']
            )
            
            exam_question = ExamService.get_exam_question(
                data['exam_question_id'], 
                student_exam.exam
            )
            
            answer = ExamService.get_question_answer(
                data['answer_id'], 
                exam_question.question
            )
            
            result = AnswerSubmissionService.submit_answer(student_exam, exam_question, answer)
            
            response_data = StudentExamResultSerializer.to_dict(result)
            
            return self.success_response(response_data, 201)
            
        except ExamAPIException as e:
            return self.error_response(e.message, e.status_code)
        except Exception as e:
            return self.handle_exception(e)


class CompleteExamView(AuthenticatedAPIView):
    
    def post(self, request):
        try:
            data = self.get_json_data(request)
            self.validate_required_fields(data, ['student_exam_id'])
            
            student_exam = ExamService.get_active_student_exam(
                request.student, 
                data['student_exam_id']
            )
            
            completion_data = ExamCompletionService.complete_exam(student_exam)
            
            response_data = ExamCompletionSerializer.to_dict(data['student_exam_id'], completion_data)
            
            return self.success_response(response_data, 200)
            
        except ExamAPIException as e:
            return self.error_response(e.message, e.status_code)
        except Exception as e:
            return self.handle_exception(e)