```markdown
# Sieportal Parser 🚀

Асинхронный парсер для Siemens Sieportal API на Python с полной типизацией и проверкой код-стайла.

## 📦 Особенности

- ✅ Полная асинхронность (aiohttp)
- ✅ Строгая типизация (Python 3.10+)
- ✅ Проверка код-стайла (Ruff)
- ✅ Пагинация данных
- ✅ Обработка ошибок и ретраи
- ✅ Конфигурация через .env

## ⚡ Быстрый старт

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/alikegorplay-afk/SieportalParser.git
cd SieportalParser
```

### 2. Установите зависимости
```bash
# Создаем виртуальное окружение
python -m venv venv

# Активируем (Windows)
venv\Scripts\activate

# Активируем (Linux/Mac)
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 3. Настройка окружения
```bash
# Копируем пример файла настроек
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

### 4. Получение client_secret
1. Перейдите на [Sieportal](https://sieportal.siemens.com)
2. Откройте DevTools (F12)
3. Перейдите в Network → XHR
4. Найдите запрос с токеном
5. Скопируйте `client_secret` из запроса
6. Вставьте в файл `.env`:

```env
CLIENT_SECRET=your_actual_client_secret_here
PROXY=http://user:pass@proxy_ip:port  # опционально
```

### 5. Запуск парсера
```bash
python start.py --language en --region us --input ids.csv
```

## 🛠 Настройка

### Аргументы командной строки
```bash
python start.py \
  --language en      # Язык (en, ru, de, etc)
  --region us        # Регион (us, eu, cn, etc)  
  --input ids.csv    # Файл с ID для парсинга
```

### Пример файла ids.csv
```
12345
67890
11223
```

## 🎯 Пример использования

```python
from src.SieportalGetTreeApi import SieportalTreeAPI
import aiohttp
import asyncio

async def main():
    async with aiohttp.ClientSession() as session:
        api = SieportalTreeAPI(session, "en", "us")
        
        # Получить информацию о категории
        info = await api.get_tree_information(12345)
        print(f"Category info: {info}")
        
        # Получить продукты
        products = await api.get_products(12345)
        print(f"Products: {len(products)} items")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔧 Разработка

### Проверка код-стайла
```bash
# Запуск линтера
ruff check --select=ALL

# Автоисправление
ruff check --select=ALL --fix
```

### Тестирование
```bash
# Создайте тесты в tests/ директории
pytest tests/
```

## 📄 Лицензия

MIT License - смотрите файл [LICENSE](LICENSE)

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку: `git checkout -b feature/new-feature`
3. Закоммитьте: `git commit -m 'Add new feature'`
4. Запушите: `git push origin feature/new-feature`
5. Откройте Pull Request

---

⭐ Если проект полезен, поставьте звезду на GitHub!
```

## 🔐 Дополнительно создайте:

### 1. **.env.example**
```env
# Sieportal API Configuration
CLIENT_SECRET=your_client_secret_here

# Proxy Configuration (optional)
PROXY=http://username:password@proxy_ip:port

# API Settings
LANGUAGE=en
REGION=us
```

### 2. **requirements.txt** (обновленный)
```txt
aiohttp==3.9.1
aiofiles==23.2.1
aiocsv==1.2.4
python-dotenv==1.0.0
```