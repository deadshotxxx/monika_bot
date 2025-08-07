#!/bin/bash

# Создаём виртуальное окружение
python3 -m venv venv

# Активируем окружение
source venv/bin/activate

# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости из requirements.txt
pip install -r requirements.txt

# Запускаем бота
python3 main.py
