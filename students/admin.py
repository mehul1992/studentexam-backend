from django.contrib import admin
from .models import Student, StudentExam, StudentExamResult
from .forms import StudentAdminForm


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email_address',
        'mobile_number',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'email_address', 'mobile_number')
    ordering = ('-created_at',)


@admin.register(StudentExam)
class StudentExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'exam', 'status', 'exam_result', 'total_score', 'max_exam_score', 'start_time', 'end_time', 'created_at')
    list_filter = ('status', 'exam_result', 'created_at')
    search_fields = ('student__first_name', 'student__last_name', 'exam__exam_name')
    ordering = ('-created_at',)


@admin.register(StudentExamResult)
class StudentExamResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_exam', 'exam_question', 'answer', 'is_correct', 'score')
    list_filter = ('is_correct',)
    search_fields = ('student_exam__student__first_name', 'student_exam__student__last_name')
    ordering = ('-student_exam__created_at',)

# Register your models here.
