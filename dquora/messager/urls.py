from django.urls import path

from dquora.messager import views

app_name = "messager"
urlpatterns = [
    path('', views.MessagesListView.as_view(), name='messages_list'),
    path('send-message/', views.send_message, name='send_message'),
    path('receive_message/', views.receive_message, name='receive_message'),
    path('<username>/', views.ConversationListView.as_view(), name='conversation_detail'),



]
