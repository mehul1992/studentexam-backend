from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=100)
    email_address = models.EmailField(max_length=128, unique=True)
    password = models.CharField(max_length=128, blank=True, default='')
    date_of_brith = models.DateField()
    country_code = models.CharField(max_length=5)
    mobile_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'students'
        indexes = [
            models.Index(fields=['email_address']),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_') and not self.password.startswith('argon2$') and not self.password.startswith('bcrypt$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class StudentExam(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    
    EXAM_RESULT_CHOICES = [
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_exams')
    exam = models.ForeignKey('exams.Exam', on_delete=models.CASCADE, related_name='student_exams')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_score = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
        default=0
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    exam_result = models.CharField(max_length=10, choices=EXAM_RESULT_CHOICES, null=True, blank=True)
    max_exam_score = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_exams'
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['exam']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f"StudentExam({self.student_id}, {self.exam_id})"


class StudentExamResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE, related_name='results')
    exam_question = models.ForeignKey('exams.ExamQuestion', on_delete=models.CASCADE, related_name='student_results')
    answer = models.ForeignKey('exams.QuestionAnswer', on_delete=models.CASCADE, related_name='student_results')
    is_correct = models.BooleanField(default=False)
    score = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10000)],
        default=0
    )

    class Meta:
        db_table = 'student_exam_results'
        indexes = [
            models.Index(fields=['student_exam']),
            models.Index(fields=['exam_question']),
        ]

    def __str__(self) -> str:
        return f"StudentExamResult({self.student_exam_id}, {self.exam_question_id})"

# Create your models here.
