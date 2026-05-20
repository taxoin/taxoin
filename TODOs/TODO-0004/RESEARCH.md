# TODO-0004: Research & Analysis — Taxoin in the Ecosystem

> Сводка исследований, анализов и предложений по улучшению Taxoin.
> Сгенерировано из обсуждений с Grok (AI-ассистент).

---

## 1. Competitive Analysis: Taxoin vs Аналоги

### Proof of Personhood (Genesis-механика)

| Проект | Метод | Отличие от Taxoin |
|--------|-------|-------------------|
| **Proof of Humanity** (Kleros) | Видео + поручители + арбитраж | PoH — для UBI/governance. Taxoin — стартовый капитал для экономики услуг |
| **Worldcoin / World ID** | Биометрия (Orb-скан радужки) + ZK | Масштабный, но спорный. Taxoin — социальная верификация |
| **Humanode** | Биометрия + гомоморфное шифрование | "Один человек = одна нода". Taxoin — 3/7 аттестаций |
| **Idena** | Синхронные flip-пазлы (human-only) | Не-биометрический PoP |
| **BrightID, Gitcoin Passport** | Web of trust, attestations | Только верификация, нет экономики услуг |

### Proof of Contribution / Service Economy

| Проект | Механизм | Отличие от Taxoin |
|--------|----------|-------------------|
| **iExec (RLC)** | Proof of Contribution (PoCo) + TEE | Только compute, сложнее. Taxoin — любые услуги |
| **EAS (Ethereum Attestation Service)** | On-chain attestations | Без привязки к платежу. Taxoin — mutual attestation + payment |
| **Akash / Render / io.net** | Децентрализованный cloud/GPU | Только специфические услуги. Taxoin — произвольные |
| **Helium** | Proof of Coverage | Только физическая инфраструктура (WiFi/LoRaWAN) |
| **OpenBazaar** | P2P marketplace | Нет встроенной криптовалюты |

### Итог: Прямых клонов Taxoin нет

Сочетание PoP + Mutual Attestation + Service Registry + анти-спекуляция — уникально.
Ближайшая комбинация: PoH (верификация) + iExec (PoCo) + EAS (attestations).

---

## 2. Mutual Attestation — Технический разбор

### Структура
```
AttestedTransaction:
  consumer_sig  — "Я получил услугу" (ECDSA)
  provider_sig  — "Я предоставил услугу" (ECDSA)
  Транзакция валидна ТОЛЬКО с обеими подписями
```

### Сильные стороны
- Простота, аудируемость, ECDSA secp256k1
- Двусторонняя ответственность
- Нет нужды в Oracle для большинства услуг

### Уязвимости
- Off-chain trust window (мошенничество до подписи)
- Dispute resolution не детализирован
- UX: обмен подписями должен быть seamless

### Сравнение
| Система | Сложность | Применимость |
|---------|-----------|-------------|
| iExec PoCo | Высокая (TEE + staking) | Только compute |
| EAS | Средняя | Любые attestations |
| Taxoin MA | Низкая | Любые услуги |

---

## 3. Dispute Resolution — Механизмы споров

### Сценарии

| Ситуация | Решение |
|----------|---------|
| Consumer подписал, provider нет | Timeout → возврат hold |
| Provider выполнил, consumer не подписывает | Provider открывает dispute → 5/7 |
| Оба подписали, услуга фейк | Валидаторы → штраф репутации |
| Provider взял деньги, не выполнил | Consumer открывает dispute → возврат |

### Риски
- Субъективность валидаторов при сложных услугах
- Масштабирование: 7 валидоров = bottleneck

### Сравнение
| Система | Механизм |
|---------|---------|
| Kleros | Jurors + staking + апелляции |
| iExec | TEE + slashing |
| Taxoin | Reputation-based arbitration |

---

## 4. Reputation System — Репутация

### Роли
1. Фильтр доверия при поиске (`--min-rating 4.0`)
2. Ценообразование (высокая цена + низкий рейтинг = нет клиентов)
3. Наказание за нарушения (штраф репутации)
4. Защита от Sybil
5. Лидерборд

### Текущая математика
```
rating = 0.0–5.0 (простое среднее арифметическое)
total_tx — количество транзакций
```

### Уязвимости
- Нет Bayesian average (холодный старт)
- Уязвимость к накруткам
- Нет time decay

### Рекомендуемые улучшения
```python
# Bayesian average (как IMDb)
weighted_rating = (sum(ratings) + C * R0) / (total_tx + C)
# где C = 10-50, R0 = 3.5-4.0
```
- Вес по объёму транзакции
- Вес по репутации оценивающего
- Time decay (старые отзывы теряют вес)
- Отдельные метрики: rating, total_tx, dispute_rate

---

## 5. ZK-Reputation — Приватная репутация

### Концепция
Вместо публичного рейтинга 4.8/5 с 942 tx → ZK-proof:
- "Мой рейтинг >= 4.5"
- "У меня >= 500 tx"
- "У меня < 3% споров"
- Без раскрытия истории

### Технические варианты
| Технология | Pros | Cons |
|-----------|------|------|
| ZK-SNARKs (Groth16/Plonk) | Быстрая верификация | Trusted setup |
| ZK-STARKs | Quantum-resistant, transparent | Больше размер proof |
| UniRep | Приватная репутация | Сложность |
| Semaphore | Приватные сигналы | Ограниченный |

### Рекомендация
Гибридный подход: публичный реестр (старт) + опциональный ZK-layer.
Circuits для: `prove_rating_above()`, `prove_tx_count_above()`, `prove_no_recent_disputes()`.

### Существующие решения
- **UniRep** — приватная репутация на ZK
- **zkMe** — ZK Soulbound Tokens
- **Semaphore** — приватные сигналы (Privacy & Scaling Explorations)
- **Aztec/Noir** — private state rollup

---

## Выводы по всем направлениям

1. **Taxoin уникален** — сочетание PoP + MA + Service Registry + анти-спекуляция
2. **Mutual Attestation — самый сильный механизм** — решает Oracle Problem без сложных систем
3. **Dispute Resolution — самое слабое место** — нужна детализация
4. **Rating Formula — самое простое улучшение** — Bayesian average
5. **ZK-Reputation — самое перспективное** — приватность без потери доверия
