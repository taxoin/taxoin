# TODO-0004A: Rating Formula — Bayesian Average

**Цель:** Заменить простое среднее арифметическое на Bayesian average
для защиты от накруток и холодного старта.

**Ссылка:** RESEARCH.md → Раздел 4

**Формула:**
```python
weighted_rating = (sum(ratings) + C * R0) / (total_tx + C)
# C = 10, R0 = 4.0 (default)
```

**Задачи:**
- [ ] Модифицировать `ReputationTracker._recalculate()` с Bayesian average
- [ ] Добавить time decay (старые отзывы теряют вес через N месяцев)
- [ ] Добавить dispute_rate как отдельную метрику
- [ ] Тесты: холодный старт, накрутка, сглаживание
