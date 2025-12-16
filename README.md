# Transport MCP Chat Agent

Этот проект представляет собой систему чата с AI-агентом, специализирующимся на транспортных задачах. Агент использует инструменты Model Context Protocol (MCP) для геокодирования адресов и построения маршрутов.

## Архитектура

Проект состоит из трех основных компонентов:

1. **MCP Server** (`MCP/`): Предоставляет инструменты для работы с геоданными
   - Геокодирование адресов (Nominatim)
   - Построение маршрутов (OpenRouteService)

2. **Agent Server** (`agent-server/`): FastAPI приложение с LangChain агентом
   - Подключается к MCP серверу для получения инструментов
   - Использует модель MiniMax через OpenRouter
   - Управляет сессиями чата

3. **Web App** (`web-app/`): Простой веб-интерфейс чата
   - HTML/CSS/JavaScript интерфейс
   - Поддержка Markdown в ответах
   - Очистка истории чата

## Требования

- Docker и Docker Compose
- API ключи:
  - OpenRouter API Key (для модели MiniMax)
  - OpenRouteService API Key (для маршрутов)

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd transportMCP
   ```

2. Настройте переменные окружения в файле `.env`:
   ```env
   OPENROUTER_API_KEY=ваш_openrouter_api_key
   ORS_API_KEY=ваш_ors_api_key
   ```

   Получите ключи API:
   - [OpenRouter](https://openrouter.ai/) - для доступа к моделям
   - [OpenRouteService](https://openrouteservice.org/) - для маршрутов

## Запуск

Запустите все сервисы с помощью Docker Compose:

```bash
docker-compose up --build
```

Сервисы будут доступны на следующих портах:
- Web App: http://localhost:8080
- Agent Server: http://localhost:8081
- MCP Server: http://localhost:8000

## Использование

1. Откройте браузер и перейдите на http://localhost:8080
2. Введите запрос в поле чата, например:
   - "Найди координаты Главного корпуса ТГУ в Томске"
   - "Построй маршрут от Москвы до Санкт-Петербурга на машине"
   - "Как добраться пешком от Красной площади до Большого театра?"

3. Агент использует доступные инструменты для ответа на вопросы, связанные с географией и маршрутами.

## API Endpoints

### Agent Server (порт 8081)

- `POST /chat` - Отправить сообщение агенту
  ```json
  {
    "message": "Ваш запрос",
    "session_id": "идентификатор_сессии"
  }
  ```

- `DELETE /history/{session_id}` - Очистить историю сессии

- `GET /health` - Проверка здоровья сервиса

## Разработка

Для локальной разработки каждого компонента:

### MCP Server
```bash
cd MCP
pip install -r requerement.txt
python server.py
```

### Agent Server
```bash
cd agent-server
pip install -r requerments.txt
python main.py
```

### Web App
Откройте `web-app/index.html` в браузере (требуется CORS для локального сервера).

## Зависимости

- **MCP Server**: fastmcp, routingpy, geopy
- **Agent Server**: langchain, langgraph, fastapi, uvicorn, langchain-mcp-adapters, langchain-openai
- **Web App**: marked.js (для рендеринга Markdown)

## Лицензия

[Укажите лицензию, если применимо]