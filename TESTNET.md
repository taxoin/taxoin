# Taxoin Testnet

> Публичная тестовая сеть для первых пользователей.

---

## Подключиться

```bash
docker pull taxoin/node:latest  # when published
# OR run from source:
git clone https://xlab.z7n.top/bicrobot/taxoin.git
cd taxoin
docker compose up -d
```

API доступен на `http://localhost:47780`.
Веб-кошелёк: открыть `web/wallet.html` в браузере.

## Получить тестовые Ⓣ

Отправьте запрос:

```bash
curl -X POST http://localhost:47780/api/testnet/faucet \
  -H "Content-Type: application/json" \
  -d '{"address": "0xВАШ_АДРЕС"}'
```

→ +100 Ⓣ на баланс (только testnet).

## Зарегистрировать услугу

```bash
curl -X POST http://localhost:47780/api/service/register \
  -H "Content-Type: application/json" \
  -d '{"provider":"0xВАШ_АДРЕС","service_type":"taxi",
       "price_per_unit":3.0,"description":"Поездка по городу"}'
```

## Отправить Ⓣ

Через Telegram Wallet (`web/wallet.html`) или API:

```bash
curl -X POST http://localhost:47780/api/tx/send \
  -H "Content-Type: application/json" \
  -d '{"consumer":"0xОТПРАВИТЕЛЬ","provider":"0xПОЛУЧАТЕЛЬ",
       "amount":3.0,"consumer_sig":"test_sig","provider_sig":"test_sig"}'
```

## Статус сети

```bash
curl http://localhost:47780/api/status
```
