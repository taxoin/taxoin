# TODO-0004D: ZK-Reputation — Private Reputation Layer

**Цель:** Добавить опциональный ZK-слой для приватной репутации.

**Ссылка:** RESEARCH.md → Раздел 5

**Концепция:** Вместо публичного рейтинга 4.8/5 с 942 tx → ZK-proof:
- `prove_rating_above(threshold)` — рейтинг >= N
- `prove_tx_count_above(N)` — не менее N транзакций
- `prove_dispute_rate_below(N)` — менее N% споров
- Без раскрытия конкретных транзакций, контрагентов, сумм

**Технические варианты:**

| Технология | Pros | Cons |
|-----------|------|------|
| ZK-SNARKs (Groth16/Plonk) | Быстрая верификация | Trusted setup |
| ZK-STARKs | Без setup, quantum-resistant | Больше размер proof |
| UniRep | Готовая приватная репутация | Сложность интеграции |
| Semaphore | Приватные сигналы | Ограниченный |

**Рекомендуемый подход:** Гибрид
- Публичный реестр для базового доверия (MVP v3)
- Опциональный ZK-layer через UniRep или Noir
- Selective disclosure: раскрытие деталей только при спорах

**Задачи:**
- [ ] Исследовать UniRep для интеграции
- [ ] Написать circuit на Noir: `prove_rating_above.circom`
- [ ] Web-клиент для генерации proof на устройстве
- [ ] Верификация proof валидаторами при consensus
- [ ] Документация: как использовать ZK-репутацию
- [ ] Интеграционные тесты

**Существующие проекты:**
- UniRep: https://github.com/UniRep
- zkMe: https://zk.me
- Semaphore: https://semaphore.pse.dev
- Aztec/Noir: https://noir-lang.org
