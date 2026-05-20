# TODO-0004H: Throughput Improvements

**Проблема:** git commit (~30ms) = 33 TPS потолок.
**Решение:** batch commits (N tx → 1 git commit).

## Batch commits (P1)

```python
# Текущий: каждый блок = git commit
mine_block_on_branch():
    git.add_block(block)  # ~30ms

# После: батч
mine_block_on_branch_batch():
    for block in blocks:
        write_block_file(block)
    git.commit()  # ~30ms for N blocks
```

**Ожидаемый прирост:** 33 → 100+ TPS
**Сложность:** 🟢 Низкая

## LevelDB/SQLite замена git (P4)

**Когда:** когда 100 TPS станет мало
**Что:** заменить `GitBlockchain` на LevelDB для writes, git только для audit
**Прирост:** 100 → 10,000+ TPS
**Сложность:** 🔴 Высокая

## Async git (P2)

Вынести git commit в фоновый процесс (celery/rq).
**Прирост:** 33 → 200 TPS
**Сложность:** 🟡 Средняя

## Убрать state snapshot из блока (P3)

Каждый блок хранит полный snapshot всех балансов.
Можно хранить только diff (incremental).
**Прирост:** +50% (меньше данных → быстрее commit)
**Сложность:** 🟢 Низкая

---

**Ссылка:** `CAPACITY.md` — полный анализ пропускной способности
