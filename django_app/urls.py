from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django_app.views import api_info, TasksView
import socket

def hostname_view(request):
    # Эта функция покажет, какой Pod обработал запрос
    return HttpResponse(f"Hello! Served by Pod: {socket.gethostname()}")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', hostname_view), # Главная страница
    path('health/', lambda r: HttpResponse("OK")), # Для livenessProbe
    path('prometheus/', include('django_prometheus.urls')),
    path("api/", api_info, name="api"),
    path("tasks/", TasksView.as_view(), name="tasks"),
]
