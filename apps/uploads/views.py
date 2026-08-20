import os
import base64
import uuid
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.files.base import ContentFile
from django.conf import settings
from apps.accounts.permissions import IsOrganizationMember


class UploadView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        file_type = request.query_params.get('type', 'file')
        data = request.data.get('file')

        if not data:
            return Response({'success': False, 'message': 'No file provided'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Handle base64 data URL
        if isinstance(data, str) and data.startswith('data:'):
            import re
            match = re.match(r'data:([^;]+);base64,(.+)', data)
            if match:
                mime_type = match.group(1)
                file_data = match.group(2)
                extension = mime_type.split('/')[-1] if '/' in mime_type else 'bin'

                # Determine subdirectory
                if file_type == 'audio':
                    subdir = 'audio'
                elif file_type == 'image':
                    subdir = 'images'
                else:
                    subdir = 'files'

                filename = f"{uuid.uuid4().hex[:10]}.{extension}"
                file_path = os.path.join(settings.MEDIA_ROOT, subdir, filename)

                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'wb') as f:
                    f.write(base64.b64decode(file_data))

                file_url = f"{settings.MEDIA_URL}{subdir}/{filename}"

                return Response({
                    'success': True,
                    'data': {
                        'url': file_url,
                        'name': filename,
                        'mime_type': mime_type
                    }
                })

        # Handle regular file upload
        file_obj = request.FILES.get('file')
        if file_obj:
            subdir = file_type if file_type in ['audio', 'image'] else 'files'
            filename = f"{uuid.uuid4().hex[:10]}_{file_obj.name}"
            file_path = os.path.join(settings.MEDIA_ROOT, subdir, filename)

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'wb+') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

            file_url = f"{settings.MEDIA_URL}{subdir}/{filename}"

            return Response({
                'success': True,
                'data': {
                    'url': file_url,
                    'name': file_obj.name,
                    'mime_type': file_obj.content_type
                }
            })

        return Response({'success': False, 'message': 'Invalid file format'},
                        status=status.HTTP_400_BAD_REQUEST)