from django.db import models
from django.conf import settings
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator


class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    number_of_questions = models.SmallIntegerField()
    passing_score = models.SmallIntegerField()
    max_score = models.SmallIntegerField()
    exam_timer = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(36000)], default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exams_created')

    class Meta:
        db_table = 'exams'
        indexes = [
            models.Index(fields=['exam_name']),
            models.Index(fields=['category']),
        ]

    def __str__(self) -> str:
        return self.exam_name


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_name = models.TextField()
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='questions_created')

    class Meta:
        db_table = 'questions'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        return (self.question_name or '')[:60]


class ExamQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='exam_questions')
    score = models.SmallIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exam_questions'
        unique_together = ('exam', 'question')
        indexes = [
            models.Index(fields=['exam']),
            models.Index(fields=['question']),
        ]

    def __str__(self) -> str:
        return f"ExamQuestion(exam={self.exam_id}, question={self.question_id})"


class QuestionAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer = models.TextField()
    is_correct = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'questions_answer'
        indexes = [
            models.Index(fields=['question']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        return f"Answer({self.id}) for Question({self.question_id})"

# Create your models here.
