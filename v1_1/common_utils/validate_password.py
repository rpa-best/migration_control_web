import re

def validate_password(password):
    # Минимальная длина пароля
    if len(password) < 8:
        return False, 'Пароль должен содержать минимум 8 символов'

    # Проверка наличия цифр в пароле
    if not re.search(r'\d', password):
        return False, 'Пароль должен содержать хотя бы одну цифру'

    # Проверка наличия букв в верхнем и нижнем регистре
    if not re.search(r'[a-z]', password) or not re.search(r'[A-Z]', password):
        return False, 'Пароль должен содержать буквы верхнего и нижнего регистра'

    return True, 'Пароль прошел валидацию'