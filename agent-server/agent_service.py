import traceback
from typing import List, Dict, Optional

# Импорты LangChain / LangGraph
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_agent
from dotenv import load_dotenv
import os

load_dotenv()

MCP_SERVER_URL = "http://mcp:8000/sse"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "minimax/minimax-m2"

class AgentService:
    def __init__(self):
        self.mcp_url = MCP_SERVER_URL
        self.api_key = OPENROUTER_API_KEY
        self.agent_executor = None
        # Простая память сессий: {session_id: [messages]}
        self.sessions: Dict[str, List] = {}
        
        self.mcp_config = {
            "local-sse-server": {
                "url": self.mcp_url,
                "transport": "sse"
            }
        }
        self.client = MultiServerMCPClient(self.mcp_config)

    async def initialize(self):
        """Подключаемся к MCP и инициализируем агента"""
        print(f"🔄 [AgentService] Подключение к MCP серверу: {self.mcp_url}...")
        try:
            tools = await self.client.get_tools()
            print(f"✅ [AgentService] Успешно. Загружено инструментов: {len(tools)}")
            
            if not tools:
                print("⚠️ [AgentService] Внимание: Список инструментов пуст.")

            model = ChatOpenAI(
                model=MODEL_NAME,
                api_key=self.api_key,
                base_url=OPENROUTER_BASE_URL,
                default_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Local MCP Client"
                },
                temperature=0.7
            )

            # Создаем агента (граф)
            self.agent_executor = create_agent(model, tools)
            print("🤖 [AgentService] Агент готов к работе.")

        except Exception as e:
            print(f"❌ [AgentService] Ошибка инициализации: {e}")
            raise e

    async def chat(self, user_input: str, session_id: str = "default") -> str:
        """Основной метод общения"""
        if not self.agent_executor:
            raise RuntimeError("AgentService не инициализирован. Вызовите initialize()!")

        # 1. Получаем историю сессии
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        history = self.sessions[session_id]
        
        # 2. Формируем сообщения для модели
        messages = history + [HumanMessage(content=user_input)]

        try:
            # 3. Выполняем запрос
            result = await self.agent_executor.ainvoke({"messages": messages})
            
            # 4. Извлекаем ответ
            last_message = result["messages"][-1]
            response_text = last_message.content
            
            # 5. Обновляем историю (храним только сообщения пользователя и ассистента)
            # В реальном приложении можно хранить и промежуточные шаги, но для экономии контекста берем только User/AI
            self.sessions[session_id].append(HumanMessage(content=user_input))
            self.sessions[session_id].append(AIMessage(content=response_text))
            
            return response_text

        except Exception as e:
            print(f"❌ [AgentService] Ошибка в чате: {e}")
            traceback.print_exc()
            raise e

    def clear_history(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
