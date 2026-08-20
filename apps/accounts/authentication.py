from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from .models import User, Organization


class CustomJWTAuthentication(JWTAuthentication):
    """
    Standart JWTAuthentication har doim Django'ning ichki auth.User
    modelidan (butun sonli id) foydalanuvchini qidiradi. Bu loyihada esa
    maxsus User/Organization modellari (matnli id, masalan "support_1")
    ishlatiladi — shuning uchun standart klass 500 xato berardi
    (ValueError: invalid literal for int()).

    Bu klass token ichidagi "role" claim'iga qarab to'g'ri modeldan
    (CEO uchun Organization, qolган hamma uchun User) foydalanuvchini
    qidiradi.
    """

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        role = validated_token.get("role")

        if user_id is None:
            raise InvalidToken("Token contained no recognizable user identification")

        if role == "ceo":
            try:
                account = Organization.objects.get(id=user_id)
            except Organization.DoesNotExist:
                raise AuthenticationFailed("User not found", code="user_not_found")
            account.role = "ceo"
        else:
            try:
                account = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise AuthenticationFailed("User not found", code="user_not_found")

        # DRF'ning IsAuthenticated tekshiruvi shu maydonga tayanadi;
        # custom modellarimizda standart holda mavjud emas.
        account.is_authenticated = True
        return account
