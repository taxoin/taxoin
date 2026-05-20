# Taxoin Java Port — Feasibility & Design

> SIGNED NOT_FOR_COMPACTION.
> Authored: 2026-05-20, based on Python codebase at tag `mvp-v1` + dev branch (233 tests).

---

## Вердикт: полностью реализуемо, блокеров нет

Все Git-операции Taxoin покрыты JGit 6.x. Все криптографические примитивы — Bouncy Castle.
Blockchain-протокол, форматы данных и консенсус не меняются — только язык реализации.

---

## Текущее состояние Python-кодобазы (после mvp-v1)

### Реализованные модули

| Файл | Компонент | Тестов |
|------|-----------|--------|
| `src/core.py` | TxInput, TxOutput, Transaction, UTXO, Account, Block | 17 |
| `src/crypto_utils.py` | ECDSA secp256k1, адреса | 7 |
| `src/git_backend.py` | Git-хранилище (14 операций) | 7 |
| `src/mempool.py` | Async mempool | 8 |
| `src/miner.py` | Proof of Work | 8 |
| `src/blockchain.py` | Движок блокчейна | 9 |
| `src/branch_state.py` | Изолированное состояние ветки | — |
| `src/branch_manager.py` | Оркестратор веток | — |
| `src/conflict_detector.py` | Детекция конфликтов | — |
| `src/consensus.py` | Tendermint consensus | — |
| `src/validator_network.py` | Сеть валидаторов (7 нод) | — |
| `src/gossip_protocol.py` | Gossip (fanout=3, TTL=5) | — |
| `src/genesis.py` | Proof of Personhood, 3-of-N, 420K×50Ⓣ | 11 |
| `src/service_registry.py` | Реестр сервисов | 9 |
| `src/attested_tx.py` | AttestedTransaction + BalanceHold | 13 |
| `src/cli.py` | CLI (Click) | — |

**Итого: 233 теста, все зелёные.**

### Что ещё не реализовано (из TODO-0003)
- `src/reputation.py` — рейтинговая система провайдеров
- `src/balance_hold.py` — эскроу вынесен в `attested_tx.py` (класс `BalanceHold`)
- Dispute resolution — арбитраж валидаторов при несогласии
- CLI команды: `genesis`, `service`, `tx attest`, `dispute`, `reputation`

---

## Git-операции в Taxoin → JGit маппинг

Все операции идут через `src/git_backend.py` (subprocess, без Python git-библиотек).

| Операция | Python (subprocess) | JGit API |
|----------|-------------------|----------|
| init | `git init` | `Git.init().setDirectory(dir).call()` |
| config | `git config user.name` | `StoredConfig.setString("user", null, "name", "taxoin")` |
| add | `git add <file>` | `Git.add().addFilepattern(path).call()` |
| commit (custom ts) | `GIT_AUTHOR_DATE=@ts git commit` | `CommitCommand.setAuthor(new PersonIdent(name, email, epochMs, 0))` |
| rev-parse HEAD | `git rev-parse HEAD` | `repo.resolve(Constants.HEAD)` |
| rev-list --count | `git rev-list --count HEAD` | `RevWalk` итерация с счётчиком |
| git show commit:path | `git show <sha>:<path>` | `TreeWalk.forPath(reader, path, commit.getTree())` + `ObjectReader.open(id).getBytes()` |
| git log --format | `git log --format=%H %P` | `Git.log().call()` → `RevCommit` с `getParents()` |
| branch create | `git branch <name> <from>` | `Git.branchCreate().setName(name).setStartPoint(from).call()` |
| checkout | `git checkout <branch>` | `Git.checkout().setName(branch).call()` |
| branch list | `git branch --list` | `Git.branchList().call()` |
| branch delete | `git branch -d/-D <name>` | `Git.branchDelete().setBranchNames(name).setForce(force).call()` |
| merge (-X theirs) | `git merge -X theirs` | `Git.merge().setStrategy(MergeStrategy.RECURSIVE).setContentMergeStrategy(ContentMergeStrategy.THEIRS).call()` ← **JGit 6.2+ обязательно** |
| merge --abort | `git merge --abort` | `repo.writeMergeHeads(null); repo.writeMergeCommitMsg(null)` |
| rev-list range | `git rev-list --count b..a` | Два `RevWalk` с `markStart/markUninteresting` |
| notes add | `git notes add -F tmpfile <sha>` | `NoteMap.read(reader, noteCommit)` + `map.set(id, content, inserter)` + коммит |
| notes show | `git notes show <sha>` | `NoteMap.getNote(id)` + `reader.open(note.getData()).getBytes()` |

### Критический нюанс: merge strategy

```
❌ НЕВЕРНО: MergeStrategy.THEIRS → это `-s theirs` (заменяет всё дерево)
✅ ВЕРНО:   MergeStrategy.RECURSIVE + ContentMergeStrategy.THEIRS → это `-X theirs`
```

`ContentMergeStrategy` появился в JGit 6.2. Использовать минимум `6.2.0`.

---

## Криптография: Python `cryptography` → Bouncy Castle

```java
// Генерация ключей
ECKeyPairGenerator gen = new ECKeyPairGenerator();
X9ECParameters params = SECNamedCurves.getByName("secp256k1");
ECDomainParameters domain = new ECDomainParameters(params.getCurve(), params.getG(), params.getN());
gen.init(new ECKeyGenerationParameters(domain, new SecureRandom()));
AsymmetricCipherKeyPair pair = gen.generateKeyPair();

// Подпись — КРИТИЧНО: Bouncy Castle принимает уже хэшированные байты
byte[] hash = MessageDigest.getInstance("SHA-256").digest(data.getBytes(UTF_8));
ECDSASigner signer = new ECDSASigner();
signer.init(true, privateKey);
BigInteger[] sig = signer.generateSignature(hash);  // ← передаём hash, не data!

// Адрес: совместим с Python
byte[] pubBytes = pubKeyParams.getQ().getEncoded(false);  // uncompressed
byte[] sha = MessageDigest.getInstance("SHA-256").digest(pubBytes);
String hex = bytesToHex(sha);
String address = "0x" + hex.substring(hex.length() - 40);
```

Python `ECDSA(SHA256)` хэширует данные внутри библиотеки. Если не хэшировать в Java вручную — подписи несовместимы между Python и Java цепочками.

---

## Асинхронность: Python asyncio → Java

| Python | Java |
|--------|------|
| `asyncio.Lock` | `ReentrantLock` / `ReentrantReadWriteLock` |
| `asyncio.Queue` | `LinkedBlockingQueue<T>` |
| `async def f()` | `CompletableFuture<T>` или virtual thread (Java 21+) |
| `await coroutine` | `.get()` или `Thread.ofVirtual().start(...)` |
| `asyncio.run(f())` | `CompletableFuture.get()` в main |

Рекомендуется Java 21 — virtual threads (`Thread.ofVirtual()`) — это 1:1 ментальная модель с asyncio корутинами без блокировки носителей.

---

## JSON-совместимость с Python цепочкой

Python: `json.dumps(asdict(self), sort_keys=True)`

Java (Jackson):
```java
ObjectMapper mapper = new ObjectMapper();
mapper.configure(MapperFeature.SORT_PROPERTIES_ALPHABETICALLY, true);
mapper.configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true);
```

Без `sort_keys` SHA256 блока будет другим → цепочки несовместимы.

---

## Маппинг модулей Python → Java

| Python | Java класс | Пакет | Сложность |
|--------|-----------|-------|-----------|
| `core.py` | `TxInput`, `TxOutput`, `Transaction`, `UTXO`, `Account`, `Block` | `com.taxoin.core` | Простой |
| `crypto_utils.py` | `CryptoUtils` | `com.taxoin.crypto` | Простой |
| `git_backend.py` | `JGitBlockchain implements BlockchainRepository` | `com.taxoin.storage` | Средний |
| `blockchain.py` | `BlockchainEngine` | `com.taxoin.engine` | Средний |
| `branch_state.py` | `BranchState` (POJO + `ReentrantLock`) | `com.taxoin.branch` | Простой |
| `branch_manager.py` | `BranchManager` | `com.taxoin.branch` | Средний |
| `mempool.py` | `Mempool` (`LinkedBlockingQueue`) | `com.taxoin.mempool` | Простой |
| `miner.py` | `ProofOfWorkMiner` | `com.taxoin.mining` | Простой |
| `conflict_detector.py` | `ConflictDetector` (static) | `com.taxoin.consensus` | Простой |
| `consensus.py` | `TendermintConsensus` | `com.taxoin.consensus` | Средний |
| `validator_network.py` | `ValidatorNode`, `ValidatorSet`, `ValidatorNetwork` | `com.taxoin.validator` | Простой |
| `gossip_protocol.py` | `GossipProtocol` | `com.taxoin.gossip` | Простой |
| `genesis.py` | `GenesisRegistry`, `GenesisAttestation` | `com.taxoin.contrib` | Простой |
| `service_registry.py` | `ServiceRegistry`, `ServiceRegistration` | `com.taxoin.contrib` | Простой |
| `attested_tx.py` | `AttestedTransaction`, `BalanceHold`, `HoldRecord` | `com.taxoin.contrib` | Простой |
| `cli.py` | `TaxoinCli` (Picocli `@Command`) | `com.taxoin.cli` | Простой |

### Заметки по новым модулям (mvp-v1)

**`BalanceHold`** — Python передаёт `balances: dict` по ссылке и мутирует его. Java `Map<String, Double>` тоже передаётся по ссылке — поведение идентично. НО: `Double` immutable, нужно `Map<String, Double>` с заменой значения через `put()`:
```java
balances.put(consumer, balances.getOrDefault(consumer, 0.0) - amount);
```

**`GenesisRegistry`** — кворум `>= 3` (не завязан на 7 валидаторов). В Java: `if (attestation.attestedBy.size() >= 3)`.

**`AttestedTransaction.tx_id`** — генерируется в `__post_init__` из `consumer + provider + amount + time.time()`. В Java: в конструкторе или фабричном методе. Не в Java record (records immutable).

---

## Зависимости (Maven)

```xml
<dependencies>
  <!-- JGit — минимум 6.2.0 для ContentMergeStrategy -->
  <dependency>
    <groupId>org.eclipse.jgit</groupId>
    <artifactId>org.eclipse.jgit</artifactId>
    <version>6.9.0.202403050737-r</version>
  </dependency>

  <!-- Bouncy Castle — secp256k1 ECDSA -->
  <dependency>
    <groupId>org.bouncycastle</groupId>
    <artifactId>bcprov-jdk18on</artifactId>
    <version>1.78.1</version>
  </dependency>

  <!-- Jackson — JSON с sort_keys -->
  <dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.17.1</version>
  </dependency>

  <!-- Picocli — CLI -->
  <dependency>
    <groupId>info.picocli</groupId>
    <artifactId>picocli</artifactId>
    <version>4.7.6</version>
  </dependency>

  <!-- JUnit 5 -->
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.2</version>
    <scope>test</scope>
  </dependency>
</dependencies>
```

**Java 21** (virtual threads + records + pattern matching).

---

## Фазы реализации

| # | Фаза | Источник | Дней |
|---|------|---------|------|
| 1 | Core data structures + HashUtils | `core.py` | 1-2 |
| 2 | CryptoUtils (Bouncy Castle, DER-encoding, адреса) | `crypto_utils.py` | 1 |
| 3 | JGitBlockchain (14 операций, FileRepository) | `git_backend.py` | 2-3 |
| 4 | Mempool + Miner | `mempool.py`, `miner.py` | 1 |
| 5 | BranchState + ConflictDetector | `branch_state.py`, `conflict_detector.py` | 1 |
| 6 | ValidatorNetwork + GossipProtocol | `validator_network.py`, `gossip_protocol.py` | 1 |
| 7 | TendermintConsensus | `consensus.py` | 1 |
| 8 | BranchManager (virtual threads) | `branch_manager.py` | 1-2 |
| 9 | BlockchainEngine | `blockchain.py` | 1 |
| 10 | Genesis + ServiceRegistry + AttestedTx + BalanceHold | `genesis.py`, `service_registry.py`, `attested_tx.py` | 2 |
| 11 | CLI (Picocli) + E2E тесты | `cli.py` | 1 |

**Итого: ~12-16 дней.** 233 Python теста портируются в JUnit 5.

---

## Критические файлы для реализации

| Файл | Важность | Причина |
|------|---------|---------|
| `src/git_backend.py` | Высшая | 14 git-операций — каждая маппится 1:1 на JGit |
| `src/crypto_utils.py` | Высшая | Формула адреса должна быть точно воспроизведена; DER-encoding |
| `src/branch_manager.py` | Высокая | Async + checkout + mine coupling; наиболее сложный оркестратор |
| `tests/test_git_branches.py` | Высокая | ~25 тестов — полная поведенческая спецификация для JGitBlockchain |
| `src/attested_tx.py` | Средняя | Mutation семантика BalanceHold — проверить при Java boxing |

---

## Что НЕ меняется при Java-порте

- Структура блоков и JSON-формат (байт-в-байт идентичен Python для совместимости цепочек)
- double SHA256 для хэша блока
- Схема именования веток: `branch/{wallet}/{timestamp}_{seq:03d}`
- Tendermint consensus: PROPOSE → PREVOTE → PRECOMMIT → COMMIT, 5/7 quorum
- Genesis: 3-of-N attestation, 420,000 × 50 Ⓣ = 21,000,000 Ⓣ max
- Mutual Attestation: обе подписи обязательны для validity
- Gossip: fanout=3, TTL=5
- PoW (deprecated в TODO-0003, но пока присутствует в Python)

---

## SIGNED NOT_FOR_COMPACTION.
