# Taxoin — Dev Environment Setup

> От чистой машины до работающего кластера.

---

## Требования

| Инструмент | Версия | Зачем |
|-----------|--------|-------|
| Docker | 20+ | Всё запускается в контейнерах |
| Docker Compose | v2+ | Кластер из 4 сервисов |
| Python | 3.10+ | Запуск тестов и CLI напрямую |
| git | 2.30+ | Хранилище блокчейна |

Java и Maven **не нужны** локально — Java-порт собирается внутри Docker.

---

## Репозитории

```
/home/oclo/git/
  taxoin/          ← Python (основной, этот репо)
  taxoin-java/     ← Java port (Quarkus)
```

### Клонировать с нуля

```bash
# Python (GitLab — основной)
git clone https://xlab.z7n.top/bicrobot/taxoin.git
cd taxoin
git checkout dev        # основная рабочая ветка

# Java port (GitLab)
git clone https://xlab.z7n.top/bicrobot/taxoin-java.git
```

### GitHub mirrors (для публичного доступа)

```
github.com/taxoin/taxoin        ← Python
github.com/taxoin/taxoin-java   ← Java
```

---

## Python — запуск тестов

```bash
cd /home/oclo/git/taxoin

# Установить зависимости
pip install -r requirements.txt

# Все тесты (256, все зелёные)
python -m pytest tests/ -v

# Конкретный модуль
python -m pytest tests/test_integration.py -v

# CLI напрямую
python src/cli.py --help
python src/cli.py wallet new
python src/cli.py wallet address
```

### Зависимости Python

```
click>=8.0
cryptography>=3.4
fastapi>=0.100
uvicorn>=0.20
httpx>=0.24
```

---

## Java — запуск через Docker

### Шаг 1: Собрать образ

```bash
cd /home/oclo/git/taxoin-java
./scripts/build.sh
```

Первый раз ~5 минут (Maven качает зависимости).  
Повторные сборки — секунды (Docker кеш).

### Шаг 2а: Одиночный сервер (минимум RAM, ~256 MB)

```bash
./scripts/start.sh           # порт 47780
./scripts/start.sh 8080      # кастомный порт
```

```
API:     http://localhost:47780
Health:  http://localhost:47780/health
Wallet:  http://localhost:47780/web/wallet.html
Swagger: http://localhost:47780/q/swagger-ui
```

### Шаг 2б: Полный кластер (3 валидатора + API, ~1 GB RAM)

```bash
./scripts/start-cluster.sh
```

```
Validator-1: http://localhost:47701
Validator-2: http://localhost:47702
Validator-3: http://localhost:47703
API:         http://localhost:47780
```

### Проверить статус

```bash
./scripts/status.sh
```

### Остановить

```bash
./scripts/stop.sh            # одиночный
./scripts/stop-cluster.sh    # кластер
```

### Тесты Java (без локальной Java)

```bash
docker volume create taxoin-mvn-cache
docker run --rm \
  -v $(pwd):/workspace \
  -v taxoin-mvn-cache:/root/.m2 \
  -w /workspace \
  maven:3.9-eclipse-temurin-21 \
  mvn test
```

224 теста, все зелёные.

---

## API — быстрая проверка

```bash
# Health
curl http://localhost:47780/health

# Создать кошелёк
curl -X POST http://localhost:47780/api/wallet

# Получить тестовые монеты (testnet)
curl -X POST http://localhost:47780/api/testnet/faucet \
  -H "Content-Type: application/json" \
  -d '{"address":"0xВАШ_АДРЕС"}'

# Баланс
curl http://localhost:47780/api/balance/0xВАШ_АДРЕС

# Список сервисов
curl http://localhost:47780/api/services

# Статус сети
curl http://localhost:47780/api/status
```

---

## Архитектура локального энва

```
  Python тесты / CLI
  ┌─────────────────┐
  │  pytest / CLI   │  python -m pytest | python src/cli.py
  └────────┬────────┘
           │  import
           ▼
  ┌─────────────────┐
  │   src/ (Python) │  18 модулей, git как хранилище
  └─────────────────┘

  Java (Docker)
  ┌──────────────────────────────────────────────────┐
  │  taxoin-api :47780   (одиночный или в кластере)  │
  │                                                  │
  │  validator-1 :47701                              │
  │  validator-2 :47702  ← docker-compose.yml        │
  │  validator-3 :47703                              │
  └──────────────────────────────────────────────────┘
           │
           │  данные персистентны в Docker volumes:
           │  taxoin-java-data-1/2/3/api
           ▼
  /app/.taxoin/.git   ← блокчейн как git репо внутри контейнера
```

---

## Ветки

### taxoin (Python)

| Ветка | Назначение |
|-------|-----------|
| `dev` | Основная рабочая ветка |
| `main` | Стабильные релизы |
| `feature/path-to-public` | TODO-0004G (Telegram Mini App, QR) |
| `java-port` | Документация Java-порта |

### taxoin-java

| Ветка | Назначение |
|-------|-----------|
| `main` | Единственная ветка, всегда стабильна |

---

## Теги

### taxoin (Python)

| Тег | Что зафиксировано |
|-----|------------------|
| `mvp-v1` | Базовый UTXO блокчейн |
| `mvp-v2` | Параллельные ветки + консенсус |
| `mvp-v3` | Proof of Contribution (genesis, services, attestation) |
| `architecture-v1` | Архитектурная документация |
| `research-v1` | TODO-0004 research phase |
| `telegram-v1` | Telegram архитектура в TODO-0004G |

### taxoin-java

| Тег | Что зафиксировано |
|-----|------------------|
| `java-mvp-v1` | Полный Java-порт: 224 теста, Docker, REST API |

---

## Переменные окружения (Java)

| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `TAXOIN_DIR` | `/app/.taxoin` | Путь к данным |
| `TAXOIN_VALIDATOR` | — | Номер валидатора (1–7) |
| `TAXOIN_PORT` | `47780` | Порт ноды |

---

## Что запущено сейчас в локальном энве

На этой машине параллельно работают другие проекты:

| Контейнер | Порт | Проект |
|---|---|---|
| `honcho-api-1` | `8000` | Honcho |
| `honcho-database-1` | `5432` | PostgreSQL (pgvector) |
| `honcho-redis-1` | `6379` | Redis |
| `mirofish` | `33003`, `33051` | Mirofish |
| `mindsight-iq` | `11100` | MindsightIQ |
| `mirofish-neo4j` | `37474`, `37687` | Neo4j |
| `taxi24x7-tgbot-1` | — | taxi24x7 Telegram bot |
| `proxy-*` | разные | OpenClaw proxy stack |

Taxoin Java **не запущен** по умолчанию — запускать вручную через `./scripts/start.sh`.

---

## Следующие шаги (TODO-0004G)

```
Осталось ~4 часа работы до публичного MVP:

❌ Telegram Mini App — адаптировать wallet.html под Telegram WebApp SDK
❌ QR-платежи        — генерация QR в Mini App

Всё остальное (Docker, REST API, web wallet, docs) — уже готово (java-mvp-v1).
```

Детали: `TODOs/TODO-0004/TODO-0004G_PATH_TO_PUBLIC.md`
