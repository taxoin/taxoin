# TODO-0005C: PWA — Progressive Web App для Taxoin

**Цель:** Заменить простой web-интерфейс на PWA, который можно
установить на телефон как приложение. Работает без Telegram,
без App Store, без Google Play.

## Что даёт PWA вместо обычного web

| Обычный web | PWA |
|------------|-----|
| Открывается в браузере | Устанавливается на экран как приложение |
| Нет иконки на телефоне | Иконка на home screen |
| Нет push-уведомлений | Push-уведомления о disputes |
| Не работает офлайн | Service Worker + кэш |
| Нет доступа к камере | Доступ к камере (сканировать QR) |

## Технически

PWA = обычный HTML/JS/CSS + 2 файла:

```
web/
├── wallet.html          ← уже есть (Telegram Mini App)
├── dashboard.html       ← TODO-0005B
├── manifest.json        ← НОВЫЙ (PWA манифест)
└── sw.js                ← НОВЫЙ (Service Worker)
```

### manifest.json

```json
{
  "name": "Taxoin Wallet",
  "short_name": "Taxoin",
  "description": "Proof of Contribution wallet",
  "start_url": "/web/wallet.html",
  "display": "standalone",
  "background_color": "#0a0a0a",
  "theme_color": "#f0b90b",
  "icons": [
    { "src": "/web/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/web/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

### sw.js (Service Worker)

```javascript
// Кэширует статику для офлайн-режима
// Показывает push-уведомления:
self.addEventListener('push', event => {
  const data = event.data.json();
  self.registration.showNotification(data.title, {
    body: data.body,
    icon: '/web/icons/icon-192.png'
  });
});
```

## Функционал PWA

```
📱 Главная — баланс, кнопка отправить/получить
📱 Кошелёк — создать/импортировать, баланс, история
📱 Оплата — отсканировать QR, подтвердить, отправить
📱 Услуги — список, поиск, оплата в один клик
📱 Dashboard — для валидаторов (зелёная лампочка)
📱 Уведомления — push, когда кто-то хочет тебе заплатить
```

## Что сделать

- [ ] Создать `manifest.json`
- [ ] Создать `sw.js`
- [ ] Иконки 192x192 и 512x512 (Ⓣ символ)
- [ ] Подключить PWA к API (те же эндпоинты)
- [ ] Push-уведомления через Web Push API
- [ ] QR-сканирование через камеру телефона
- [ ] Offline-режим (кэш основных страниц)
- [ ] Деплой: static files через FastAPI (уже готово)

## Почему PWA, а не нативное приложение

| Аспект | PWA | React Native | Kotlin/Swift |
|--------|-----|-------------|-------------|
| Время разработки | 1 день | 2 недели | 2 месяца |
| App Store | Не нужен | Нужен | Нужен |
| Обновления | Мгновенно | Через сто́ры | Через сто́ры |
| Push | ✅ | ✅ | ✅ |
| QR scan | ✅ | ✅ | ✅ |
| Offline | ✅ | ✅ | ✅ |
| Доступ к камере | ✅ | ✅ | ✅ |

**PWA даёт 90% функционала нативного приложения за 5% времени.**
