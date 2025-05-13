from django.urls import path
from .views import CognitiveTestView

urlpatterns = [
    path('', CognitiveTestView().start_test, name='start_first_sequence'),
    path('start-second-sequence/', CognitiveTestView().start_second_sequence, name='start_second_sequence'),
    path('test/<uuid:session_id>/state/<str:state>/', CognitiveTestView().test_state, name='test_state'),
    path('submit-answer/<uuid:session_id>/<int:state_attempt_id>/', CognitiveTestView().submit_answer, name='submit_answer'),
    path('timer/<uuid:session_id>/', CognitiveTestView().timer_state, name='timer_state'),
]