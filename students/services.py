import datetime as dt
import jwt
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from typing import Dict, Any, Optional

from core.exceptions import AuthenticationError, ValidationError, NotFoundError, BusinessLogicError
from .models import Student, StudentExam, StudentExamResult
from exams.models import Exam, ExamQuestion, QuestionAnswer


class AuthenticationService:
    
    @staticmethod
    def _get_jwt_secret() -> str:
        return getattr(settings, 'JWT_AUTH', {}).get('JWT_SECRET_KEY', 'dev-secret-change-me')
    
    @staticmethod
    def _get_jwt_settings() -> Dict[str, Any]:
        jwt_settings = getattr(settings, 'JWT_AUTH', {})
        return {
            'access_lifetime': jwt_settings.get('JWT_ACCESS_TOKEN_LIFETIME', dt.timedelta(days=5)),
            'refresh_lifetime': jwt_settings.get('JWT_REFRESH_TOKEN_LIFETIME', dt.timedelta(days=7))
        }
    
    @classmethod
    def authenticate_student(cls, email: str, password: str) -> Student:
        email = email.strip().lower()
        
        try:
            student = Student.objects.get(email_address=email, is_active=True)
        except Student.DoesNotExist:
            raise AuthenticationError('Invalid credentials')
        
        if not student.check_password(password):
            raise AuthenticationError('Invalid credentials')
        
        return student
    
    @classmethod
    def generate_tokens(cls, student: Student) -> Dict[str, str]:
        now = dt.datetime.utcnow()
        jwt_settings = cls._get_jwt_settings()
        secret = cls._get_jwt_secret()
        
        access_payload = {
            'sub': str(student.id),
            'email': student.email_address,
            'iat': int(now.timestamp()),
            'exp': int((now + jwt_settings['access_lifetime']).timestamp()),
            'type': 'access',
        }
        
        refresh_payload = {
            'sub': str(student.id),
            'iat': int(now.timestamp()),
            'exp': int((now + jwt_settings['refresh_lifetime']).timestamp()),
            'type': 'refresh',
        }
        
        access_token = jwt.encode(access_payload, secret, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, secret, algorithm='HS256')
        
        return {
            'access': access_token,
            'refresh': refresh_token
        }


class ExamService:
    
    @staticmethod
    def get_exam_by_id(exam_id: str) -> Exam:
        try:
            return Exam.objects.get(id=exam_id, is_active=True)
        except Exam.DoesNotExist:
            raise NotFoundError('Exam not found')
    
    @staticmethod
    def get_or_create_student_exam(student: Student, exam: Exam) -> StudentExam:
        existing_exam = StudentExam.objects.filter(
            student=student,
            exam=exam,
            status__in=['pending', 'in_progress']
        ).first()
        
        if existing_exam:
            return existing_exam
        
        return StudentExam.objects.create(
            student=student,
            exam=exam,
            start_time=timezone.now(),
            status='in_progress',
            max_exam_score=exam.max_score
        )
    
    @staticmethod
    def get_active_student_exam(student: Student, student_exam_id: str) -> StudentExam:
        try:
            return StudentExam.objects.get(
                id=student_exam_id,
                student=student,
                status='in_progress'
            )
        except StudentExam.DoesNotExist:
            raise NotFoundError('Student exam not found or not in progress')
    
    @staticmethod
    def get_exam_question(exam_question_id: str, exam: Exam) -> ExamQuestion:
        try:
            return ExamQuestion.objects.get(
                id=exam_question_id,
                exam=exam,
                is_active=True
            )
        except ExamQuestion.DoesNotExist:
            raise NotFoundError('Exam question not found')
    
    @staticmethod
    def get_question_answer(answer_id: str, question) -> QuestionAnswer:
        try:
            return QuestionAnswer.objects.get(
                id=answer_id,
                question=question,
                is_active=True
            )
        except QuestionAnswer.DoesNotExist:
            raise NotFoundError('Answer not found')


class AnswerSubmissionService:
    
    @staticmethod
    def submit_answer(student_exam: StudentExam, exam_question: ExamQuestion, answer: QuestionAnswer) -> StudentExamResult:
        is_correct = answer.is_correct
        score = exam_question.score if is_correct else 0
        
        existing_result = StudentExamResult.objects.filter(
            student_exam=student_exam,
            exam_question=exam_question
        ).first()
        
        if existing_result:
            existing_result.answer = answer
            existing_result.is_correct = is_correct
            existing_result.score = score
            existing_result.save()
            return existing_result
        else:
            return StudentExamResult.objects.create(
                student_exam=student_exam,
                exam_question=exam_question,
                answer=answer,
                is_correct=is_correct,
                score=score
            )


class ExamCompletionService:
    
    @staticmethod
    def complete_exam(student_exam: StudentExam) -> Dict[str, Any]:
        total_score = StudentExamResult.objects.filter(
            student_exam=student_exam
        ).aggregate(total=Sum('score'))['total'] or 0
        
        passing_score = student_exam.exam.passing_score
        max_score = student_exam.exam.max_score
        exam_result = 'pass' if total_score >= passing_score else 'fail'
        
        student_exam.end_time = timezone.now()
        student_exam.status = 'done'
        student_exam.total_score = total_score
        student_exam.exam_result = exam_result
        student_exam.max_exam_score = max_score
        student_exam.save()
        
        return {
            'total_score': total_score,
            'max_score': max_score,
            'exam_result': exam_result,
            'end_time': student_exam.end_time.isoformat()
        }