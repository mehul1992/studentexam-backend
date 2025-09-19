from core.base_views import BaseAPIView
from .models import Exam
from .serializers import ExamSerializer


class ExamListView(BaseAPIView):
    
    def get(self, request):
        try:
            exams = Exam.objects.filter(is_active=True).order_by('-created_at')
            
            exam_data = ExamSerializer.to_dict_list(exams)
            
            return self.success_response({'results': exam_data})
            
        except Exception as e:
            return self.handle_exception(e)