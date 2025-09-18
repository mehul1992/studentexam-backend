"""
Serializers for question-related data transformation.
"""
from typing import Dict, Any, List
from exams.models import Question, ExamQuestion, QuestionAnswer


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
