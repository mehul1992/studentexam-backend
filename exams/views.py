"""
Exam views following SOLID, DRY, and KISS principles.
"""
from core.base_views import BaseAPIView
from .models import Exam
from .serializers import ExamSerializer


class ExamListView(BaseAPIView):
    """
    Handles listing all active exams.
    Follows Single Responsibility Principle - only handles exam listing.
    """
    
    def get(self, request):
        try:
            # Get all active exams ordered by creation date
            exams = Exam.objects.filter(is_active=True).order_by('-created_at')
            
            # Serialize exam data
            exam_data = ExamSerializer.to_dict_list(exams)
            
            return self.success_response({'results': exam_data})
            
        except Exception as e:
            return self.handle_exception(e)