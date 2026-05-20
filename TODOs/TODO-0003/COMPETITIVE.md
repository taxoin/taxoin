# Competitive Landscape: Proof of Contribution

> Исследование рынка проектов, концептуально близких к Taxoin.
> Дата: 2026-05-20

---

## DePIN (Decentralized Physical Infrastructure Networks)

Самый близкий жанр. Все эти проекты заменяют майнинг на предоставление
реального оборудования/услуг. Но каждый — только одну услугу.

| Проект | Тикер | Услуга | Верификация |
|--------|-------|--------|-------------|
| Helium | HNT | WiFi/LoRaWAN покрытие | Proof of Coverage |
| Akash Network | AKT | GPU-вычисления для AI/ML | Proof of Compute |
| Render Network | RNDR | 3D-рендеринг GPU | Proof of Render |
| io.net | IO | GPU-кластеры для AI | Proof of Compute |
| Livepeer | LPT | Видеотранскодинг | Proof of Transcoding |
| Filecoin | FIL | Хранение файлов | Proof of Replication |
| Golem | GLM | CPU-вычисления | Proof of Computation |

**Ограничение:** каждая сеть завязана на один тип ресурса.

## Proof of Useful Work (PoUW)

Академические попытки заменить SHA256-хэши на полезные вычисления:
- HEPchain — майнинг = вычисления физики высоких энергий (CERN)
- PoUW for Route Planning — майнинг = оптимизация маршрутов
- SudokuCoin — майнинг = решение судоку

**Проблема:** полезная работа сложна для on-chain верификации.
**Ни один проект не взлетел** — CERN не будет ждать 10 мин подтверждения.

## Sharing Economy на блокчейне

| Проект | Суть |
|--------|------|
| Origin Protocol (OGN) | p2p-маркетплейс жилья, товаров, услуг на Ethereum |
| Braintrust (BTRST) | p2p-фриланс-биржа |
| Sylo | p2p-коммуникация + платёжный слой |

**Проблема:** всё завязано на Ethereum (газ, масштабирование, сложность).

---

## Сравнительная таблица: Taxoin vs ближайшие конкуренты

| Аспект | Helium | Akash | Filecoin | Origin | **Taxoin** |
|--------|--------|-------|----------|--------|------------|
| Услуг | 1 (WiFi) | 1 (GPU) | 1 (storage) | много | **Любые** |
| Верификация | on-chain | on-chain | on-chain | Oracle | **Mutual Attestation** |
| Консенсус | migrated to Solana | Tendermint | собств. | Ethereum | **Tendermint (свой)** |
| Порог входа | хотспот $500 | GPU $10K | HDD | $0 | **Мобила** |
| Бэкенд | Solana | Cosmos SDK | собств. | EVM | **Git** |
| Майнинг | был PoW | нет | нет | нет | **Нет (убрали)** |

---

## Вывод: Taxoin уникален

**Реально похожего проекта нет.** Сочетание:

```
Proof of Contribution + Multi-service p2p + Git backend + Tendermint consensus
```

Ближайшие родственники:
- **Helium** — за реальное оборудование (но только WiFi)
- **Akash** — за полезные вычисления (но только GPU)
- **Origin Protocol** — p2p-маркетплейс (но на Ethereum)

**Наше уникальное преимущество:**
- Любая услуга (не привязаны к одному оборудованию)
- Mutual Attestation (люди подтверждают, блокчейн не гадает)
- Git как бэкенд (простота, прозрачность, дешевизна)
- Никакого майнинга (CPU → полезная работа)

---

## Источники

- Helium: https://www.helium.com/
- Akash: https://akash.network/
- Render Network: https://gpumarketdepin.com
- Filecoin: https://www.gemini.com/cryptopedia/helium-network-token-map-helium-hotspot-hnt-coin
- Livepeer: https://www.coinage.media/s2/how-ai-is-supercharging-decentralized-computing-projects-akash-and-livepeer
- PoUW Survey: https://www.sciencedirect.com/science/article/pii/S2096720925001149
- DePIN Comparison: https://io.net/blog/io-net-vs-akash-vs-render-network-which-decentralized-platform-actually-delivers

## SIGNED NOT_FOR_COMPACTION.
