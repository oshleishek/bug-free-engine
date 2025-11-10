"""
Діагностичний скрипт для перевірки Google Sheets підключення
Запустіть на Render.com через Shell або локально
"""

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

print("=" * 60)
print("🔍 ДІАГНОСТИКА GOOGLE SHEETS ПІДКЛЮЧЕННЯ")
print("=" * 60)

# Крок 1: Перевірка environment variables
print("\n📋 Крок 1: Перевірка environment variables")
print("-" * 60)

required_vars = {
    'GOOGLE_PROJECT_ID': os.environ.get('GOOGLE_PROJECT_ID'),
    'GOOGLE_PRIVATE_KEY_ID': os.environ.get('GOOGLE_PRIVATE_KEY_ID'),
    'GOOGLE_PRIVATE_KEY': os.environ.get('GOOGLE_PRIVATE_KEY'),
    'GOOGLE_CLIENT_EMAIL': os.environ.get('GOOGLE_CLIENT_EMAIL'),
    'GOOGLE_CLIENT_ID': os.environ.get('GOOGLE_CLIENT_ID'),
    'GOOGLE_CERT_URL': os.environ.get('GOOGLE_CERT_URL'),
    'GOOGLE_SHEET_NAME': os.environ.get('GOOGLE_SHEET_NAME', 'Leads - Divorce Bot')
}

all_present = True
for var_name, var_value in required_vars.items():
    if var_value:
        if 'KEY' in var_name:
            print(f"✅ {var_name}: присутня (довжина: {len(var_value)} символів)")
        elif 'EMAIL' in var_name:
            print(f"✅ {var_name}: {var_value}")
        else:
            print(f"✅ {var_name}: присутня")
    else:
        print(f"❌ {var_name}: ВІДСУТНЯ!")
        all_present = False

if not all_present:
    print("\n❌ ПРОБЛЕМА: Відсутні деякі environment variables!")
    print("Перейдіть в Render.com → Environment → додайте відсутні змінні")
    exit(1)

# Крок 2: Формування credentials
print("\n🔑 Крок 2: Формування credentials")
print("-" * 60)

try:
    # Форматуємо private key (заміна \\n на \n)
    private_key = required_vars['GOOGLE_PRIVATE_KEY'].replace('\\n', '\n')
    
    # Перевіряємо формат
    if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
        print("⚠️  УВАГА: Private key може бути неправильно відформатований")
        print(f"Початок: {private_key[:50]}...")
    else:
        print("✅ Private key правильно відформатований")
    
    creds_dict = {
        "type": "service_account",
        "project_id": required_vars['GOOGLE_PROJECT_ID'],
        "private_key_id": required_vars['GOOGLE_PRIVATE_KEY_ID'],
        "private_key": private_key,
        "client_email": required_vars['GOOGLE_CLIENT_EMAIL'],
        "client_id": required_vars['GOOGLE_CLIENT_ID'],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": required_vars['GOOGLE_CERT_URL']
    }
    
    print("✅ Credentials dictionary створено")
    
except Exception as e:
    print(f"❌ ПОМИЛКА при форматуванні credentials: {e}")
    exit(1)

# Крок 3: Авторизація
print("\n🔐 Крок 3: Авторизація в Google")
print("-" * 60)

try:
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    print("✅ Service Account credentials створено")
    
    client = gspread.authorize(creds)
    print("✅ Авторизація в Google пройшла успішно!")
    
except Exception as e:
    print(f"❌ ПОМИЛКА авторизації: {type(e).__name__}: {e}")
    print("\nМожливі причини:")
    print("1. Private key неправильно відформатований (перевірте \\n)")
    print("2. Service Account не існує або видалений")
    print("3. API не ввімкнено в Google Cloud Console")
    exit(1)

# Крок 4: Спроба відкрити таблицю
print("\n📊 Крок 4: Відкриття таблиці")
print("-" * 60)

sheet_name = required_vars['GOOGLE_SHEET_NAME']
print(f"Спроба відкрити таблицю: '{sheet_name}'")

try:
    sheet = client.open(sheet_name).sheet1
    print(f"✅ Таблиця '{sheet_name}' успішно відкрита!")
    
    # Перевіряємо заголовки
    headers = sheet.row_values(1)
    if headers:
        print(f"\n📋 Заголовки таблиці:")
        for i, header in enumerate(headers, 1):
            print(f"   {i}. {header}")
    else:
        print("⚠️  УВАГА: Таблиця порожня (немає заголовків)")
    
except gspread.SpreadsheetNotFound:
    print(f"❌ ТАБЛИЦЯ НЕ ЗНАЙДЕНА: '{sheet_name}'")
    print("\nМожливі причини:")
    print("1. Назва таблиці написана неправильно (перевірте регістр і пробіли)")
    print("2. Таблиця НЕ поділена з Service Account email")
    print(f"\nПеревірте, чи таблиця поділена з: {required_vars['GOOGLE_CLIENT_EMAIL']}")
    print("\nЯк поділитися:")
    print("1. Відкрийте таблицю в Google Sheets")
    print("2. Натисніть 'Share' (Поділитися)")
    print("3. Додайте email вище")
    print("4. Виберіть права: 'Editor' (Редактор)")
    exit(1)
    
except Exception as e:
    print(f"❌ ІНША ПОМИЛКА: {type(e).__name__}: {e}")
    exit(1)

# Крок 5: Тест запису
print("\n✍️  Крок 5: Тестовий запис")
print("-" * 60)

try:
    test_row = ["TEST", "діагностика", "успішна"]
    sheet.append_row(test_row)
    print("✅ Тестовий рядок успішно додано!")
    print("\nПеревірте таблицю - там має з'явитися новий рядок з 'TEST'")
    
except Exception as e:
    print(f"❌ ПОМИЛКА запису: {type(e).__name__}: {e}")
    print("\nМожлива причина: Service Account має права 'Viewer', а не 'Editor'")
    exit(1)

print("\n" + "=" * 60)
print("✅ ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
print("=" * 60)
print("\nGoogle Sheets підключення працює правильно!")
