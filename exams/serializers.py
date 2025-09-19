from typing import Dict, Any, List
from .models import Exam


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