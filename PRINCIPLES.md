# PRINCIPLES — Gitchain Development Manifesto

> SIGNED NOT_FOR_COMPACTION. Священные принципы разработки для всех агентов.

---

## Core Principles: DRY-KISS-TDD-TODO-DONE

### 1. DRY (Don't Repeat Yourself)

**Правило:** Каждая часть знания должна иметь единственное, недвусмысленное, авторитетное представление в системе.

**Применение:**
- Переиспользуй существующий код вместо копирования
- Создавай утилиты для повторяющихся операций
- Один источник правды для данных
- Документация в одном месте (не дублируй в коде и README)

**Примеры:**
```python
# ❌ BAD: Дублирование логики
def validate_tx_in_mempool(tx):
    if tx.sender not in accounts:
        return False
    if accounts[tx.sender].balance < tx.value:
        return False
    return True

def validate_tx_in_block(tx):
    if tx.sender not in accounts:
        return False
    if accounts[tx.sender].balance < tx.value:
        return False
    return True

# ✅ GOOD: Единая функция
def validate_transaction(tx, accounts):
    if tx.sender not in accounts:
        return False
    if accounts[tx.sender].balance < tx.value:
        return False
    return True
```

---

### 2. KISS (Keep It Simple, Stupid)

**Правило:** Простота — высшая форма изощрённости. Сложность — враг надёжности.

**Применение:**
- Выбирай простейшее решение, которое работает
- Избегай преждевременной оптимизации
- Не добавляй функциональность "на будущее"
- Если можешь объяснить за 30 секунд — достаточно просто

**Примеры:**
```python
# ❌ BAD: Излишняя сложность
class AbstractTransactionValidatorFactory:
    def create_validator(self, type: str) -> AbstractValidator:
        if type == "utxo":
            return UTXOValidatorImpl()
        elif type == "account":
            return AccountValidatorImpl()

# ✅ GOOD: Прямолинейно
def validate_utxo_tx(tx): ...
def validate_account_tx(tx): ...
```

**Критерии простоты:**
- Меньше строк кода (но не в ущерб читаемости)
- Меньше уровней абстракции
- Меньше зависимостей
- Понятно новичку в проекте

---

### 3. TDD (Test-Driven Development)

**Правило:** Тесты пишутся ДО кода. Red → Green → Refactor.

**Цикл TDD:**
1. **Red**: Напиши тест, который падает
2. **Green**: Напиши минимальный код, чтобы тест прошёл
3. **Refactor**: Улучши код, сохраняя зелёные тесты

**Применение:**
```python
# Шаг 1: RED — тест падает
def test_create_branch():
    manager = BranchManager()
    branch = manager.create_branch("0xalice")
    assert branch.startswith("branch/0xalice/")

# Шаг 2: GREEN — минимальная реализация
class BranchManager:
    def create_branch(self, wallet):
        return f"branch/{wallet}/{int(time.time())}_001"

# Шаг 3: REFACTOR — улучшаем
class BranchManager:
    def create_branch(self, wallet: str) -> str:
        timestamp = int(time.time())
        sequence = self._get_next_sequence(wallet, timestamp)
        return f"branch/{wallet}/{timestamp}_{sequence:03d}"
```

**Преимущества:**
- Код покрыт тестами по определению
- Тесты — живая документация
- Рефакторинг безопасен
- Меньше багов в продакшене

**Правила:**
- Один тест = одна проверка
- Тесты должны быть быстрыми (< 1s)
- Тесты должны быть изолированными (не зависят друг от друга)
- Тесты должны быть детерминированными (всегда один результат)

---

### 4. TODO-DONE Workflow

**Правило:** Каждая задача проходит через формальный жизненный цикл с документацией.

#### TODO Structure

```
TODOs/
├── TODO.md                    # Список активных задач
├── DONE.md                    # История завершённых задач
├── TODO-0001/
│   └── DESCRIPTION.md         # Полная спецификация
├── TODO-0002/
│   └── DESCRIPTION.md
└── ...
```

#### TODO Lifecycle

```
1. CREATION
   ├─ Создай TODO-XXXX/DESCRIPTION.md
   ├─ Опиши: Problematic, Way to solve, Dependencies
   └─ Добавь в TODO.md

2. DESCRIPTION PHASE
   ├─ Детальное планирование
   ├─ Архитектурные решения
   ├─ TDD план (какие тесты писать)
   └─ Только после завершения → переход к реализации

3. IMPLEMENTATION
   ├─ Следуй TDD циклу
   ├─ Документируй проблемы в TODO-XXXX/
   └─ Коммить часто, осмысленные сообщения

4. COMPLETION
   ├─ Все тесты зелёные
   ├─ Код отрефакторен
   ├─ Документация обновлена
   └─ Closure stamp в DONE.md
```

#### DESCRIPTION.md Template

```markdown
# TODO-XXXX: Название задачи

## SIGNED NOT_FOR_COMPACTION.

---

## Problematic

Почему эта задача существует:
- Проблема 1
- Проблема 2
- Проблема 3

## Way to solve

Как будем решать:
- Подход
- Архитектура
- Ключевые решения

## Dependencies

System:
- Python 3.10+
- Git 2.30+

Python packages:
- package1 = "^1.0"
- package2 = "^2.0"

## TDD-KISS-DRY Plan

### Step 1: ...
- [ ] Test: test_feature_1()
- [ ] Implement: feature_1()

### Step 2: ...
- [ ] Test: test_feature_2()
- [ ] Implement: feature_2()

## SIGNED NOT_FOR_COMPACTION.
```

#### Closure Stamp Format

```markdown
**SIGNED NOT_FOR_COMPACTION. YYYY-MM-DD HH:MM model-id**

Example:
SIGNED NOT_FOR_COMPACTION. 2026-05-20 05:06 kr/claude-sonnet-4-5
```

---

## Git Workflow

### Branch Strategy

```
main (master)
  ├─ feature/parallel-branching    (TODO-0002)
  ├─ feature/smart-contracts        (TODO-0003)
  └─ bugfix/nonce-validation        (hotfix)
```

### Commit Messages

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: Новая функциональность
- `fix`: Исправление бага
- `test`: Добавление тестов
- `refactor`: Рефакторинг без изменения функциональности
- `docs`: Документация
- `chore`: Рутинные задачи (обновление зависимостей)

**Example:**
```
feat: Add branch creation to BranchManager

Implement create_branch() method with:
- Branch naming convention (branch/{wallet}/{timestamp}_{seq})
- State cloning from parent
- Git branch creation via GitBlockchain

Tests: test_create_branch(), test_branch_naming()

Refs: TODO-0002 Phase 1 Step 1.3
```

### Commit Frequency

- Коммить после каждого зелёного теста
- Коммить после рефакторинга
- Коммить в конце рабочего дня
- **НЕ** коммитить сломанный код (кроме WIP веток)

---

## Code Style

### Python (PEP 8 + расширения)

```python
# Imports: stdlib → third-party → local
import asyncio
import time
from dataclasses import dataclass

import aiohttp
from cryptography.hazmat.primitives import hashes

from .core import Account, Transaction
from .git_backend import GitBlockchain

# Type hints везде
def create_branch(self, wallet: str, parent: str = "main") -> str:
    ...

# Docstrings для публичных функций
def validate_transaction(tx: Transaction, state: BranchState) -> bool:
    """Validate transaction against branch state.
    
    Args:
        tx: Transaction to validate
        state: Current branch state
        
    Returns:
        True if valid, False otherwise
    """
    ...

# Константы в UPPER_CASE
VALIDATOR_COUNT = 7
QUORUM_SIZE = 5
GOSSIP_FANOUT = 3

# Классы в PascalCase
class BranchManager:
    ...

# Функции и переменные в snake_case
def get_branch_state(branch_name: str) -> BranchState:
    ...
```

### Naming Conventions

```python
# ✅ GOOD: Понятные имена
def detect_utxo_conflicts(branch: BranchState, main: BranchState) -> list[Conflict]:
    spent_in_branch = branch.spent_utxos
    spent_in_main = self._get_spent_utxos_since(main, branch.parent_hash)
    double_spends = spent_in_branch & spent_in_main
    ...

# ❌ BAD: Непонятные сокращения
def det_utxo_conf(b: BS, m: BS) -> list[C]:
    sib = b.su
    sim = self._gsus(m, b.ph)
    ds = sib & sim
    ...
```

---

## Testing Strategy

### Test Pyramid

```
        ┌─────────┐
        │   E2E   │  10% — полные сценарии
        └─────────┘
      ┌─────────────┐
      │ Integration │  20% — взаимодействие компонентов
      └─────────────┘
    ┌─────────────────┐
    │   Unit Tests    │  70% — отдельные функции/классы
    └─────────────────┘
```

### Test Naming

```python
# Format: test_<what>_<condition>_<expected>

def test_create_branch_valid_wallet_returns_branch_name():
    ...

def test_detect_conflicts_double_spend_returns_conflict():
    ...

def test_consensus_insufficient_votes_aborts_merge():
    ...
```

### Test Structure (AAA Pattern)

```python
def test_prevote_with_conflicts_votes_no():
    # ARRANGE
    validator = ValidatorNode(address="0xval1")
    proposal = MergeProposal(branch_name="branch/0xalice/001")
    conflicts = [Conflict(type=ConflictType.UTXO_DOUBLE_SPEND)]
    
    # ACT
    vote = validator.prevote(proposal, conflicts)
    
    # ASSERT
    assert vote.vote == Vote.NO
    assert "conflict" in vote.reason.lower()
```

---

## Documentation

### Code Comments

**Когда писать:**
- Сложная логика (не очевидная из кода)
- Workarounds и костыли (с объяснением почему)
- Ссылки на внешние спецификации
- TODO/FIXME/HACK метки

**Когда НЕ писать:**
- Очевидные вещи (`i += 1  # increment i`)
- Дублирование имени функции
- Устаревшие комментарии (удаляй!)

```python
# ✅ GOOD: Объясняет "почему"
# Use optimistic locking to avoid deadlocks between branches.
# Conflicts are detected at merge time, not during execution.
async with self._branch_locks[branch_name]:
    ...

# ❌ BAD: Объясняет "что" (видно из кода)
# Lock the branch
async with self._branch_locks[branch_name]:
    ...
```

### README Structure

```markdown
# Project Name

Brief description (1-2 sentences)

## Features

- Feature 1
- Feature 2

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
gitchain init
gitchain branch create 0xalice
```

## Architecture

Link to ARCHITECTURE.txt

## Development

```bash
pytest
```

## License

MIT
```

---

## Error Handling

### Принципы

1. **Fail fast**: Обнаруживай ошибки как можно раньше
2. **Explicit is better than implicit**: Явные проверки лучше неявных
3. **Don't catch what you can't handle**: Не глуши исключения
4. **Log before raising**: Логируй контекст перед выбросом

### Примеры

```python
# ✅ GOOD: Явная проверка + информативное сообщение
def merge_branches(self, source: str, target: str) -> bool:
    if source not in self.branches:
        raise ValueError(f"Source branch '{source}' does not exist")
    
    if target not in self.branches:
        raise ValueError(f"Target branch '{target}' does not exist")
    
    conflicts = self.detect_conflicts(source, target)
    if conflicts:
        logger.error(f"Merge conflicts detected: {conflicts}")
        raise MergeConflictError(
            f"Cannot merge {source} into {target}: {len(conflicts)} conflicts"
        )
    
    # ... merge logic

# ❌ BAD: Молчаливый провал
def merge_branches(self, source: str, target: str) -> bool:
    try:
        # ... merge logic
        return True
    except Exception:
        return False  # Что пошло не так?!
```

---

## Performance Guidelines

### Преждевременная оптимизация — корень всех зол

**Правило:** Сначала сделай работающим, потом быстрым.

**Процесс:**
1. Напиши простой код
2. Напиши тесты
3. Измерь производительность
4. Оптимизируй узкие места
5. Измерь снова

### Когда оптимизировать

- Профилирование показало узкое место
- Пользователи жалуются на скорость
- Не проходим SLA (Service Level Agreement)

### Когда НЕ оптимизировать

- "Мне кажется, это медленно"
- "Этот код выглядит неэффективно"
- "В теории можно быстрее"

---

## Security Principles

### Defense in Depth

Несколько уровней защиты:

1. **Input Validation**: Проверяй все входные данные
2. **Authentication**: Проверяй подписи транзакций
3. **Authorization**: Проверяй права доступа
4. **Encryption**: Шифруй чувствительные данные
5. **Audit Logging**: Логируй все критичные операции

### Примеры

```python
# ✅ GOOD: Валидация + проверка подписи
def submit_transaction(self, tx: AsyncTransaction) -> bool:
    # 1. Validate structure
    if not tx.sender or not tx.recipient:
        raise ValueError("Invalid transaction: missing sender/recipient")
    
    # 2. Verify signature
    if not self.crypto.verify(tx.sender, tx.serialize(), tx.signature):
        raise SecurityError("Invalid signature")
    
    # 3. Check balance
    if self.get_balance(tx.sender) < tx.value:
        raise ValueError("Insufficient balance")
    
    # 4. Log
    logger.info(f"Transaction submitted: {tx.tx_hash}")
    
    return True
```

---

## Collaboration Rules

### Code Review

**Что проверять:**
- [ ] Тесты проходят
- [ ] Код следует KISS
- [ ] Нет дублирования (DRY)
- [ ] Есть тесты для нового кода
- [ ] Документация обновлена
- [ ] Коммит-сообщения понятны

**Как давать фидбек:**
- Будь конструктивен
- Предлагай решения, не только критикуй
- Хвали хороший код
- Задавай вопросы вместо утверждений

### Для агентов

**Перед началом работы:**
1. Прочитай TODO.md
2. Прочитай PRINCIPLES.md (этот файл)
3. Прочитай DESCRIPTION.md текущей задачи
4. Прочитай DONE.md (база знаний)

**Во время работы:**
1. Следуй TDD циклу
2. Коммить часто
3. Документируй проблемы
4. Спрашивай, если неясно

**После завершения:**
1. Все тесты зелёные
2. Код отрефакторен
3. Документация обновлена
4. Closure stamp в DONE.md

---

## Заповеди разработчика Gitchain

1. **Не изобретай велосипеды** — используй существующий код
2. **Не ищи обходные пути** — делай правильно с первого раза
3. **Не сомневайся** — спроси, если неясно
4. **Не усложняй** — простота побеждает
5. **Не пропускай тесты** — TDD обязателен
6. **Не забывай документировать** — TODO-DONE workflow священен
7. **Не коммить сломанное** — только зелёные тесты
8. **Не молчи об ошибках** — fail fast, log everything
9. **Не оптимизируй рано** — сначала работающий код
10. **Не работай в одиночку** — переиспользуй знания из DONE.md

### 9. Error Handling Methodology

**Правило:** Каждая ошибка — возможность роста. Не игнорировать, не скрывать, не повторять.

**Классификация ошибок:**

| Класс | Причина | Реакция |
|-------|---------|---------|
| **A** | Недостаточно информации | Запрос уточнения; предложить альтернативы |
| **Б** | Технические ограничения | Оптимизировать; честно указать лимиты |
| **В** | Неоднозначность запроса | Предложить все интерпретации; запросить выбор |
| **Г** | Выход за границы компетенции | Признать; направить к эксперту |

**Приоритет точности:** Честность важнее полноты. При неопределённости — никаких спекуляций, указать границы, запросить уточнение.

**Цикл улучшения:** `Идентификация → Анализ причин → Решение → Проверка → Внедрение → Мониторинг → Документирование`

**Критерий успеха:** Ошибка не повторяется в аналогичных условиях. Урок задокументирован. Рекомендации внедрены.

### 10. Cognitive Reconstructor

**Правило:** Работай как когнитивный реконструктор, а не как генератор догадок.

**Применение:**
- При недостатке данных не заполняй пустоты выдумкой.
- Каждый вопрос должен уменьшать неопределённость.
- При любой неоднозначности показывай 2–5 сильнейших версий, объясняй чем они различаются, указывай лучший следующий шаг проверки.
- Строго отделяй подтверждённое от вероятного.

---

## SIGNED NOT_FOR_COMPACTION.

Эти принципы — фундамент Gitchain. Читай их как "Отче наш" перед каждой сессией разработки.

**Для агентов:** Этот файл — ваша Библия. Следуйте ему неукоснительно. Передавайте знания следующим агентам через DONE.md.

**Дата создания:** 2026-05-20  
**Версия:** 2.0  
**Автор:** kr/claude-sonnet-4-5 + claude-opus-4-7
