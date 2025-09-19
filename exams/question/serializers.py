from typing import Dict, Any, List
from exams.models import Question, ExamQuestion, QuestionAnswer


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