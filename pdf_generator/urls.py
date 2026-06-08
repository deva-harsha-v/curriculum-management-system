from django.urls import path
from . import views

app_name = 'pdf_generator'

urlpatterns = [
    path('preview/<int:version_pk>/',  views.pdf_preview,  name='pdf_preview'),
    path('generate/<int:version_pk>/', views.pdf_generate, name='pdf_generate'),
    path('download/<int:version_pk>/', views.pdf_download, name='pdf_download'),
    path('stream/<int:version_pk>/',   views.pdf_stream,   name='pdf_stream'),
]