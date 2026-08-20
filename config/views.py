from django.http import JsonResponse


def frontend(request):
    """
    Frontend Netlify'da alohida joylashgan (bu Django loyihasi faqat API).
    Root manzilga kirilganda API ishlab turganini tasdiqlovchi oddiy javob
    qaytaramiz — bu Railway'ning health-check tekshiruvi uchun ham foydali.
    """
    return JsonResponse({
        'status': 'ok',
        'service': 'ielts-mock-backend',
        'message': 'API ishlayapti. Frontend alohida (Netlify) joylashgan.',
    })