from django.contrib import admin
from .models import Exam, Question, ExamQuestion, QuestionAnswer


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam_name', 'category', 'number_of_questions', 'passing_score', 'max_score', 'exam_timer', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('exam_name', 'category')
    ordering = ('-created_at',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_name', 'category', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('question_name', 'category')
    ordering = ('-created_at',)

    def short_name(self, obj):
        return (obj.question_name or '')[:60]
    short_name.short_description = 'question_name'


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam', 'question', 'score', 'is_active', 'created_at')
    list_filter = ('is_active', 'exam', 'created_at')
    search_fields = ('exam__exam_name', 'question__question_name')
    ordering = ('-created_at',)


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'is_correct', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_correct', 'created_at')
    search_fields = ('question__question_name', 'answer')
    ordering = ('-created_at',)

# Register your models here.
