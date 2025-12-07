import socket
import psycopg2
import sys
import platform
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from .models import Comic
import json


def api_info(request):
    hostname = socket.gethostname()
    now = datetime.utcnow().isoformat() + "Z"

    db_status = "ok"
    try:
        conn = psycopg2.connect(
            dbname=settings.DATABASES["default"]["NAME"],
            user=settings.DATABASES["default"]["USER"],
            password=settings.DATABASES["default"]["PASSWORD"],
            host=settings.DATABASES["default"]["HOST"],
            port=settings.DATABASES["default"]["PORT"],
            connect_timeout=2,
        )
        conn.close()
    except Exception as e:
        db_status = f"error: {e}"

    total_comics = Comic.objects.count()
    comics_by_status = {
        "reading": Comic.objects.filter(status="reading").count(),
        "completed": Comic.objects.filter(status="completed").count(),
        "wishlist": Comic.objects.filter(status="wishlist").count(),
    }

    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = "unknown"

    return JsonResponse({
        "service": "django-comic-collection",
        "version": "1.0.0",
        "hostname": hostname,
        "ip_address": ip_address,
        "time": now,
        "system": {
            "platform": platform.system(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "django_version": "4.2.7"
        },
        "database": {
            "name": str(settings.DATABASES['default']['NAME']),
            "user": str(settings.DATABASES['default']['USER']),
            "host": str(settings.DATABASES['default']['HOST']),
            "port": str(settings.DATABASES['default']['PORT']),
            "engine": settings.DATABASES['default']['ENGINE'].split('.')[-1],
            "status": db_status
        },
        "statistics": {
            "total_comics": total_comics,
            "comics_by_status": comics_by_status
        },
        "endpoints": {
            "health_check": "/health/",
            "api_info": "/api/",
            "comics": "/tasks/"
        }
    })


def health(request):
    return JsonResponse({"status": "ok"})


@method_decorator(csrf_exempt, name='dispatch')
class TasksView(View):
    def get(self, request):
        comics = Comic.objects.all().order_by('-created_at')

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            from django.shortcuts import render
            context = {
                'comics': comics,
                'total_comics': comics.count(),
                'reading_count': comics.filter(status='reading').count(),
                'completed_count': comics.filter(status='completed').count(),
                'wishlist_count': comics.filter(status='wishlist').count(),
            }
            return render(request, 'tasks.html', context)

        data = [
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "author": c.author,
                "status": c.status,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat()
            }
            for c in comics[:20]
        ]
        return JsonResponse({"comics": data})

    def post(self, request):
        try:
            body = json.loads(request.body)
            title = body.get("title")
            if not title:
                return JsonResponse({"error": "title field required"}, status=400)

            description = body.get("description", "")
            author = body.get("author", "")
            status = body.get("status", "wishlist")

            if status not in ['reading', 'completed', 'wishlist']:
                return JsonResponse({"error": "invalid status value"}, status=400)

            comic = Comic.objects.create(
                title=title,
                description=description,
                author=author,
                status=status
            )
            return JsonResponse({
                "id": comic.id,
                "title": comic.title,
                "description": comic.description,
                "author": comic.author,
                "status": comic.status,
                "created_at": comic.created_at.isoformat(),
                "updated_at": comic.updated_at.isoformat()
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid JSON"}, status=400)

