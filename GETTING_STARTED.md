# Getting Started: Taxoin для бизнеса

> Как таксопарку, парикмахерской или бирже труда начать принимать Ⓣ
> за 5 минут.

---

## 1. Быстрый старт (Docker)

```bash
git clone https://xlab.z7n.top/bicrobot/taxoin.git
cd taxoin
docker compose up -d
```

Готово. Сеть из 3 валидаторов + API работает на `http://localhost:47780`.

## 2. Создать кошелёк

```bash
curl -X POST http://localhost:47780/api/wallet
```

Сохраните **private_key**. Это единственный способ доступа к кошельку.

## 3. Пополнить баланс

В тестовой сети genesis-монеты начисляются при первой транзакции.
В production — через Proof of Personhood.

```bash
curl http://localhost:47780/api/balance/0xВАШ_АДРЕС
```

## 4. Зарегистрировать услугу

```bash
curl -X POST http://localhost:47780/api/service/register \
  -H "Content-Type: application/json" \
  -d '{"provider":"0xВАШ_АДРЕС","service_type":"taxi",
       "price_per_unit":3.0,"description":"Поездка по городу"}'
```

## 5. Принять платёж

Клиент сканирует QR-код (см. `web/wallet.html` → вкладка «Получить»)
или отправляет Ⓣ напрямую:

```bash
curl -X POST http://localhost:47780/api/tx/send \
  -H "Content-Type: application/json" \
  -d '{"consumer":"0xОТПРАВИТЕЛЬ","provider":"0xПОЛУЧАТЕЛЬ",
       "amount":3.0,"consumer_sig":"...","provider_sig":"..."}'
```

## 6. Проверить репутацию

```bash
curl http://localhost:47780/api/reputation/0xАДРЕС
```

## Telegram Wallet

Откройте в браузере (или Telegram Mini App):

```
web/wallet.html
```

Или через HTTP:

```
http://localhost:47780/web/wallet.html
```

Создайте кошелёк, скачайте ключ, отправляйте и получайте Ⓣ.

---

## OpenAPI документация

```
http://localhost:47780/docs
```

---

## Примеры интеграций

### Таксопарк
1. Кассир регистрирует услугу `taxi` за X Ⓣ/км
2. Пассажир сканирует QR в машине
3. Оплачивает Ⓣ через Telegram Wallet
4. Водитель получает Ⓣ на кошелёк
5. Все транзакции — в открытой цепочке (аудит)

### Парикмахерская
1. Мастер регистрирует услугу `beauty` за 0.5 Ⓣ
2. Клиент платит через QR на визитке
3. После услуги обе стороны подписывают mutual attestation
4. Мастер получает +1 репутацию

### Биржа труда
1. Работодатель создаёт заказ за 10 Ⓣ
2. Работник выполняет → mutual attestation
3. Средства из Balance Hold переходят работнику
4. Споры — через Dispute Resolution

---

## Контакты

Репозиторий: https://xlab.z7n.top/bicrobot/taxoin
API: http://localhost:47780/docs
Wallet: web/wallet.html
