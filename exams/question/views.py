from core.base_views import AuthenticatedAPIView
from core.exceptions import ExamAPIException
from exams.models import Exam, ExamQuestion
from .serializers import ExamQuestionSerializer


class QuestionListView(AuthenticatedAPIView):

    def get(self, request):
        try:
            # Get exam_id from query parameters
            exam_id = request.GET.get('exam_id')
            if not exam_id:
                return self.error_response('exam_id is required', 400)
            
            # Get exam using service
            exam = self._get_exam_by_id(exam_id)
            
            # Get exam questions using optimized query
            exam_questions = (
                ExamQuestion.objects
                .select_related('question')
                .filter(exam=exam, is_active=True, question__is_active=True)
                .order_by('created_at')
            )
            
            # Serialize exam questions data
            questions_data = ExamQuestionSerializer.to_dict_list(exam_questions)
            
            return self.success_response({'results': questions_data})
            
        except ExamAPIException as e:
            return self.error_response(e.message, e.status_code)
        except Exception as e:
            return self.handle_exception(e)
    
    def _get_exam_by_id(self, exam_id: str) -> Exam:
        """Get an active exam by ID."""
        try:
            return Exam.objects.get(id=exam_id, is_active=True)
        except Exam.DoesNotExist:
            raise ExamAPIException('Exam not found', 404)