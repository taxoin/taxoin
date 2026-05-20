# TODO-0004B: Dispute Resolution — Детализация

**Цель:** Расписать и имплементировать механизм разрешения споров.

**Ссылка:** RESEARCH.md → Раздел 3

**Сценарии:**
1. Consumer подписал, provider нет → timeout, возврат hold
2. Provider выполнил, consumer не подписывает → dispute, 5/7
3. Оба подписали, услуга фейк → валидаторы, штраф репутации
4. Provider взял деньги, не выполнил → dispute, возврат

**Задачи:**
- [ ] `DisputeManager` класс (src/disputes.py)
- [ ] `dispute open <tx_id>` — создание спора с доказательствами
- [ ] `dispute list` — список активных споров
- [ ] `dispute vote <dispute_id> <verdict>` — голосование валидаторов
- [ ] Автоматический таймаут (10 блоков) для зависших hold
- [ ] Интеграция с ReputationTracker: штраф при guilty
- [ ] Интеграция с BalanceHold: возврат / списание по вердикту
