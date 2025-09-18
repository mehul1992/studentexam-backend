"""
Serializers for data transformation.
Follows Open/Closed Principle by providing extensible data transformation.
"""
from typing import Dict, Any, List
from .models import Student, StudentExam, StudentExamResult
from exams.models import Exam, Question, ExamQuestion, QuestionAnswer


class StudentSerializer:
    """Serializer for Student model data."""
    
    @staticmethod
    def to_dict(student: Student) -> Dict[str, Any]:
        """Convert Student instance to dictionary."""
        return {
            'id': str(student.id),
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email_address': student.email_address,
        }


class ExamSerializer:
    """Serializer for Exam model data."""
    
    @staticmethod
    def to_dict(exam: Exam) -> Dict[str, Any]:
        """Convert Exam instance to dictionary."""
        return {
            'id': str(exam.id),
            'exam_name': exam.exam_name,
            'category': exam.category,
            'description': exam.description,
            'number_of_questions': exam.number_of_questions,
            'passing_score': exam.passing_score,
            'max_score': exam.max_score,
            'exam_timer': exam.exam_timer,
            'is_active': exam.is_active,
            'created_at': exam.created_at.isoformat(),
            'updated_at': exam.updated_at.isoformat(),
            'created_by': exam.created_by_id,
        }
    
    @classmethod
    def to_dict_list(cls, exams: List[Exam]) -> List[Dict[str, Any]]:
        """Convert list of Exam instances to list of dictionaries."""
        return [cls.to_dict(exam) for exam in exams]


class QuestionSerializer:
    """Serializer for Question model data."""
    
    @staticmethod
    def to_dict(question: Question) -> Dict[str, Any]:
        """Convert Question instance to dictionary."""
        return {
            'id': str(question.id),
            'question_name': question.question_name,
            'category': question.category,
            'description': question.description,
        }


class QuestionAnswerSerializer:
    """Serializer for QuestionAnswer model data."""
    
    @staticmethod
    def to_dict(answer: QuestionAnswer) -> Dict[str, Any]:
        """Convert QuestionAnswer instance to dictionary."""
        return {
            'id': str(answer.id),
            'answer': answer.answer,
        }
    
    @classmethod
    def to_dict_list(cls, answers: List[QuestionAnswer]) -> List[Dict[str, Any]]:
        """Convert list of QuestionAnswer instances to list of dictionaries."""
        return [cls.to_dict(answer) for answer in answers]


class ExamQuestionSerializer:
    """Serializer for ExamQuestion model data with related question and answers."""
    
    @staticmethod
    def to_dict(exam_question: ExamQuestion) -> Dict[str, Any]:
        """Convert ExamQuestion instance with related data to dictionary."""
        question = exam_question.question
        answers = QuestionAnswer.objects.filter(question=question, is_active=True)
        
        return {
            'id': str(question.id),
            'exam_question_id': str(exam_question.id),
            'question_name': question.question_name,
            'category': question.category,
            'description': question.description,
            'score': exam_question.score,
            'answers': QuestionAnswerSerializer.to_dict_list(answers),
        }
    
    @classmethod
    def to_dict_list(cls, exam_questions: List[ExamQuestion]) -> List[Dict[str, Any]]:
        """Convert list of ExamQuestion instances to list of dictionaries."""
        return [cls.to_dict(eq) for eq in exam_questions]


class StudentExamSerializer:
    """Serializer for StudentExam model data."""
    
    @staticmethod
    def to_dict(student_exam: StudentExam) -> Dict[str, Any]:
        """Convert StudentExam instance to dictionary."""
        return {
            'student_exam_id': str(student_exam.id),
            'exam_id': str(student_exam.exam.id),
            'exam_name': student_exam.exam.exam_name,
            'start_time': student_exam.start_time.isoformat() if student_exam.start_time else None,
            'status': student_exam.status,
            'max_exam_score': student_exam.max_exam_score,
            'exam_timer': student_exam.exam.exam_timer
        }


class StudentExamResultSerializer:
    """Serializer for StudentExamResult model data."""
    
    @staticmethod
    def to_dict(result: StudentExamResult) -> Dict[str, Any]:
        """Convert StudentExamResult instance to dictionary."""
        return {
            'result_id': str(result.id),
            'student_exam_id': str(result.student_exam.id),
            'exam_question_id': str(result.exam_question.id),
            'answer_id': str(result.answer.id),
            'score': result.score,
            'is_correct': result.is_correct,
        }


class ExamCompletionSerializer:
    """Serializer for exam completion results."""
    
    @staticmethod
    def to_dict(student_exam_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert exam completion data to dictionary."""
        return {
            'student_exam_id': str(student_exam_id),
            **completion_data
        }
