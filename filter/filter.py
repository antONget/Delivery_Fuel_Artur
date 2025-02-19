import re
import logging


def validate_russian_phone_number(phone_number: str) -> bool:
    """
    Валидация номера телефона
    :param phone_number:
    :return:
    """
    logging.info('validate_russian_phone_number')
    # Паттерн для российских номеров телефона
    # Российские номера могут начинаться с +7, 8, или без кода страны
    pattern = re.compile(r'^(\+7|8|7)?(\d{10})$')
    # Проверка соответствия паттерну
    match = pattern.match(phone_number)
    return bool(match)


def validate_date_birthday(date: str) -> bool:
    """
    Валидация на формат даты дд-мм-гггг
    :param date:
    :return:
    """
    logging.info('validate_date_birthday')
    # Паттерн для даты рождения дд-мм-гггг
    pattern = re.compile(r'\b(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-([0-9]{4})\b')
    # Проверка соответствия паттерну
    match = pattern.match(date)
    return bool(match)


def validate_email(email: str):
    """
    Валидация на формат электронной почты
    :param email:
    :return:
    """
    logging.info('validate_email')
    pattern = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    # Проверка соответствия паттерну
    match = pattern.match(email)
    return bool(match)
