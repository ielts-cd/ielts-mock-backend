from django.http import FileResponse
from pathlib import Path
from django.conf import settings


def frontend(request):
    index_file = Path(settings.BASE_DIR) / 'frontend' / 'index.html'
    return FileResponse(open(index_file, 'rb'), content_type='text/html')