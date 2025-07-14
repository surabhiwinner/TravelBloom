from django.urls import path

from . import views


urlpatterns = [
    path('create/', views.DiaryEntryWriteView.as_view(), name= 'create'),
    path('entries/',views.DiaryListView.as_view(), name='diary-list'), 
    path('entries-detail/<str:uuid>/', views.DiaryEntryDetailView.as_view(), name='diary_detail'),
    path('home/', views.HomeView.as_view(), name= 'home'),
    path('diary-delete/<str:uuid>', views.DiaryentryDeleteView.as_view(), name= 'diary-entry-delete'),
    path('chat/',views.ChatView.as_view(), name='chatbot'),
    path('chat/message/', views.ChatMessageView.as_view(), name='chat_message'),
    path('contact/', views.ContactView.as_view(),name='contact'),
    path('gallery/', views.GalleryView.as_view(), name='gallery'),
    path('about/', views.AboutPageView.as_view(), name='about'),

]