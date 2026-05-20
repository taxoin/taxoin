# TODO-0004I: Repository Strategy — Code vs Blockchain

## Проблема

Сейчас в GitHub и GitLab пушится только код.
Блокчейн (`/app/.taxoin/.git`) — только на VPS валидатора.
Если VPS сгорит — транзакции потеряны.

Также: новый валидатор не может быстро синхронизироваться,
потому что нет публичной копии блокчейна.

## Решение: два репозитория

```
github.com/taxoin/taxoin       ← КОД
  → src/, tests/, docs/
  → форкабельно, контрибьютабельно
  → ~5MB, клонируется за секунду

github.com/taxoin/mainnet      ← БЛОКЧЕЙН  
  → .taxoin/.git целиком
  → каждый блок = git commit
  → читабельно: git log, git show
```

## Как работает

```bash
# Валидатор, после каждого блока:
cd /app/.taxoin
git push https://github.com/taxoin/mainnet master

# Новый валидатор, при запуске:
git clone https://github.com/taxoin/mainnet /app/.taxoin

# Любой аудитор:
git clone https://github.com/taxoin/mainnet
cd mainnet
git log --oneline  # вся история транзакций
git show HEAD      # последний блок, балансы
```

## Почему два а не один

| Аспект | Один репо | Два репо |
|--------|-----------|----------|
| Вес | Код 5MB + блокчейн = жирно | Каждый лёгкий |
| Форкнуть код | Тащишь весь блокчейн | Только код |
| CI/CD | git pull тащит блоки | Быстро |
| Смысл | Смешаны код и данные | Разделены |

## Что сделать

- [ ] Создать `github.com/taxoin/mainnet` (пустой репо)
- [ ] Настроить валидатор: `git remote add chain https://...`
- [ ] Добавить `post-commit` hook для автопуша блоков
- [ ] Написать `SYNC.md` — как новому валидатору присоединиться
- [ ] Обновить `GETTING_STARTED.md`
- [ ] Документация: разница между кодом и блокчейном
