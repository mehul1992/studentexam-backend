from typing import Dict, Any, List
from .models import Student, StudentExam, StudentExamResult
from exams.models import Exam, Question, ExamQuestion, QuestionAnswer


class StudentSerializer:
    
    @staticmethod
    def to_dict(student: Student) -> Dict[str, Any]:
        return {
            'id': str(student.id),
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email_address': student.email_address,
        }


class ExamSerializer:
    
    @staticmethod
    def to_dict(exam: Exam) -> Dict[str, Any]:
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
        return [cls.to_dict(exam) for exam in exams]


class QuestionSerializer:
    
    @staticmethod
    def to_dict(question: Question) -> Dict[str, Any]:
        return {
            'id': str(question.id),
            'question_name': question.question_name,
            'category': question.category,
            'description': question.description,
        }


class QuestionAnswerSerializer:
    
    @staticmethod
    def to_dict(answer: QuestionAnswer) -> Dict[str, Any]:
        return {
            'id': str(answer.id),
            'answer': answer.answer,
        }
    
    @classmethod
    def to_dict_list(cls, answers: List[QuestionAnswer]) -> List[Dict[str, Any]]:
        return [cls.to_dict(answer) for answer in answers]


class ExamQuestionSerializer:
    
    @staticmethod
    def to_dict(exam_question: ExamQuestion) -> Dict[str, Any]:
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
        return [cls.to_dict(eq) for eq in exam_questions]


class StudentExamSerializer:
    
    @staticmethod
    def to_dict(student_exam: StudentExam) -> Dict[str, Any]:
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
    
    @staticmethod
    def to_dict(result: StudentExamResult) -> Dict[str, Any]:
        return {
            'result_id': str(result.id),
            'student_exam_id': str(result.student_exam.id),
            'exam_question_id': str(result.exam_question.id),
            'answer_id': str(result.answer.id),
            'score': result.score,
            'is_correct': result.is_correct,
        }


class ExamCompletionSerializer:
    
    @staticmethod
    def to_dict(student_exam_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'student_exam_id': str(student_exam_id),
            **completion_data
        }