# TODO-0005A: Telegram Bot для Валидаторов

**Цель:** Валидатор получает уведомления и может управлять нодой
через Telegram. Не нужен SSH, не нужен терминал.

## Возможности

```
/start          — приветствие, проверка статуса
/status         — здоровье ноды (блоки, пиры, диск)
/validators     — список всех валидоров
/disputes       — открытые споры
/vote <id> yes  — проголосовать по спору
/genesis <addr> — аттестовать нового человека
/alert on/off   — включить уведомления о критических событиях
```

## Уведомления (push)

Бот сам пишет валидатору, когда нужно действие:

```
🔴 Dispute #42 открыт!
    Потребитель: 0xalice
    Поставщик:   0xbob
    Сумма: 1.0 Ⓣ
    → /vote 42 consumer
    → /vote 42 provider

🟡 Новый genesis-запрос:
    Адрес: 0xnewbie
    → /genesis_approve newbie
```

## Технически

```python
# python-telegram-bot или aiogram
# Хэндлеры на каждый /command
# Вызовы через существующий API (localhost:47780)

class TaxoinBot:
    def __init__(self, token: str, api_url: str):
        self.api = api_url  # http://localhost:47780
    
    async def status(self, update, context):
        resp = await fetch(f"{self.api}/api/status")
        await update.message.reply_text(f"Блоков: {resp['blocks']}")
```

## Задачи

- [ ] Регистрация бота в @BotFather
- [ ] Команда /status
- [ ] Команда /disputes + /vote
- [ ] Команда /genesis
- [ ] Push-уведомления о новых disputes
- [ ] Деплой: 1 Docker-контейнер рядом с API
- [ ] Документация: как валидатору подключиться
