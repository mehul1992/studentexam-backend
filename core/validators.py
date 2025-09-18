import re
from typing import Any, List, Optional
from core.exceptions import ValidationError


class InputValidator:
    """Utility class for input validation."""
    
    @staticmethod
    def validate_email(email: str) -> str:
 
        if not email:
            raise ValidationError('Email is required')
        
        email = email.strip().lower()
        
        # Basic email regex validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError('Invalid email format')
        
        return email
    
    @staticmethod
    def validate_password(password: str) -> str:
 
        if not password:
            raise ValidationError('Password is required')
        
        if len(password) < 6:
            raise ValidationError('Password must be at least 6 characters long')
        
        return password
    
    @staticmethod
    def validate_uuid(uuid_string: str, field_name: str = 'ID') -> str:
 
        if not uuid_string:
            raise ValidationError(f'{field_name} is required')
        
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, uuid_string, re.IGNORECASE):
            raise ValidationError(f'Invalid {field_name} format')
        
        return uuid_string
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: List[str]) -> None:
 
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                empty_fields.append(field)
        
        if missing_fields:
            raise ValidationError(f'Missing required fields: {", ".join(missing_fields)}')
        
        if empty_fields:
            raise ValidationError(f'Empty required fields: {", ".join(empty_fields)}')
    
    @staticmethod
    def validate_string_length(value: str, field_name: str, min_length: int = 1, max_length: Optional[int] = None) -> str:
 
        if not isinstance(value, str):
            raise ValidationError(f'{field_name} must be a string')
        
        value = value.strip()
        
        if len(value) < min_length:
            raise ValidationError(f'{field_name} must be at least {min_length} characters long')
        
        if max_length and len(value) > max_length:
            raise ValidationError(f'{field_name} must be no more than {max_length} characters long')
        
        return value
    
    @staticmethod
    def validate_positive_integer(value: Any, field_name: str) -> int:

        try:
            int_value = int(value)
            if int_value < 0:
                raise ValidationError(f'{field_name} must be a positive integer')
            return int_value
        except (ValueError, TypeError):
            raise ValidationError(f'{field_name} must be a valid integer')


class ExamValidator:
 
    @staticmethod
    def validate_exam_id(exam_id: str) -> str:
        """Validate exam ID format."""
        return InputValidator.validate_uuid(exam_id, 'Exam ID')
    
    @staticmethod
    def validate_student_exam_id(student_exam_id: str) -> str:
        """Validate student exam ID format."""
        return InputValidator.validate_uuid(student_exam_id, 'Student Exam ID')
    
    @staticmethod
    def validate_question_id(question_id: str) -> str:
        """Validate question ID format."""
        return InputValidator.validate_uuid(question_id, 'Question ID')
    
    @staticmethod
    def validate_answer_id(answer_id: str) -> str:
        """Validate answer ID format."""
        return InputValidator.validate_uuid(answer_id, 'Answer ID')
