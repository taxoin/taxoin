# Taxoin Java Port — Feasibility & Design

> SIGNED NOT_FOR_COMPACTION.
> v2.0 — обновлено 2026-05-20 на основе mvp-v3 (256 тестов).
> Фреймворк: **Quarkus 3.x** (если не взлетит → Spring Boot 3.x, архитектура та же).

---

## Вердикт: полностью реализуемо, блокеров нет

Все Git-операции покрыты JGit 6.x. Вся криптография — Bouncy Castle.
Blockchain-протокол, форматы данных и консенсус не меняются.
Quarkus берёт на себя REST API + статику. Если понадобится — меняем
`@Path` на `@RestController`, `@Inject` на `@Autowired` — и Spring Boot готов.

---

## Текущее состояние Python (mvp-v3, 256 тестов)

| Файл | Компонент | Новое с v1 |
|------|-----------|-----------|
| `src/core.py` | TxInput, TxOutput, Transaction, UTXO, Account, Block | — |
| `src/crypto_utils.py` | ECDSA secp256k1, sign + **verify** | ← verify теперь обязателен |
| `src/git_backend.py` | Git-хранилище (14 операций) | — |
| `src/mempool.py` | Async mempool | — |
| `src/miner.py` | Proof of Work (deprecated, но остаётся) | — |
| `src/blockchain.py` | Движок блокчейна | — |
| `src/branch_state.py` | Изолированное состояние ветки | — |
| `src/branch_manager.py` | Оркестратор веток | +async complexity |
| `src/conflict_detector.py` | Детекция конфликтов | — |
| `src/consensus.py` | Tendermint consensus | — |
| `src/validator_network.py` | Сеть валидаторов (7 нод) | — |
| `src/gossip_protocol.py` | Gossip (fanout=3, TTL=5) | — |
| `src/genesis.py` | Proof of Personhood + **JSON persistence** | ← persistence |
| `src/service_registry.py` | Реестр сервисов + **JSON persistence** | ← persistence |
| `src/attested_tx.py` | AttestedTransaction + BalanceHold | — |
| `src/reputation.py` | Рейтинг провайдеров + **JSON persistence** | ← новый модуль |
| `src/api.py` | **FastAPI REST (13 эндпоинтов)** | ← новый модуль |
| `src/cli.py` | Click CLI (25+ команд) | ← вырос |
| `web/wallet.html` | **Браузерный кошелёк (vanilla JS)** | ← новый модуль |

---

## Архитектура Java-порта

```
┌─────────────────────────────────────────────────────┐
│              TAXOIN JAVA (Quarkus 3.x)              │
├──────────────┬──────────────────┬───────────────────┤
│  REST API    │   CLI (Picocli)  │  Web UI           │
│  @Path /api  │   taxoin <cmd>   │  /web/wallet.html │
├──────────────┴──────────────────┴───────────────────┤
│           Application Services                       │
│  BlockchainEngine │ BranchManager │ ValidatorNetwork │
│  GenesisRegistry  │ ServiceRegistry│ ReputationTracker│
├─────────────────────────────────────────────────────┤
│           Storage Layer                              │
│  JGitBlockchain (JGit 6.x) │ JsonStore<T> (Jackson) │
├─────────────────────────────────────────────────────┤
│           Crypto                                     │
│  CryptoUtils (Bouncy Castle secp256k1)              │
└─────────────────────────────────────────────────────┘
```

---

## Маппинг Python → Java (полный, v2)

| Python | Java класс | Пакет | Сложность |
|--------|-----------|-------|-----------|
| `core.py` | `TxInput`, `TxOutput`, `Transaction`, `UTXO`, `Account`, `Block` | `com.taxoin.core` | Простой |
| `crypto_utils.py` | `CryptoUtils` (sign **+ verify**) | `com.taxoin.crypto` | Простой |
| `git_backend.py` | `JGitBlockchain` | `com.taxoin.storage` | Средний |
| `blockchain.py` | `BlockchainEngine` | `com.taxoin.engine` | Средний |
| `branch_state.py` | `BranchState` + `ReentrantLock` | `com.taxoin.branch` | Простой |
| `branch_manager.py` | `BranchManager` (virtual threads) | `com.taxoin.branch` | **Высокий** |
| `mempool.py` | `Mempool` (`LinkedBlockingQueue`) | `com.taxoin.mempool` | Простой |
| `miner.py` | `ProofOfWorkMiner` | `com.taxoin.mining` | Простой |
| `conflict_detector.py` | `ConflictDetector` (static) | `com.taxoin.consensus` | Простой |
| `consensus.py` | `TendermintConsensus` | `com.taxoin.consensus` | Средний |
| `validator_network.py` | `ValidatorNode`, `ValidatorSet`, `ValidatorNetwork` | `com.taxoin.validator` | Простой |
| `gossip_protocol.py` | `GossipProtocol` | `com.taxoin.gossip` | Простой |
| `genesis.py` | `GenesisRegistry` + `JsonStore` | `com.taxoin.contrib` | Средний |
| `service_registry.py` | `ServiceRegistry` + `JsonStore` | `com.taxoin.contrib` | Средний |
| `attested_tx.py` | `AttestedTransaction`, `BalanceHold` | `com.taxoin.contrib` | Средний |
| `reputation.py` | `ReputationTracker` + `JsonStore` | `com.taxoin.contrib` | Средний |
| `api.py` | `TaxoinApi` (`@Path`, Quarkus REST) | `com.taxoin.api` | **Высокий** |
| `cli.py` | `TaxoinCli` (Picocli `@Command`) | `com.taxoin.cli` | **Высокий** |
| `web/wallet.html` | static resource (Quarkus serves as-is) | `resources/web/` | Простой |

---

## Критические технические детали

### 1. ECDSA: sign + verify (Bouncy Castle)

```java
// SIGN — данные хэшируем ВРУЧНУЮ (BC не хэшит сам!)
byte[] hash = MessageDigest.getInstance("SHA-256").digest(data.getBytes(UTF_8));
ECDSASigner signer = new ECDSASigner();
signer.init(true, privateKeyParams);
BigInteger[] sig = signer.generateSignature(hash);

// VERIFY — то же правило
byte[] hash = MessageDigest.getInstance("SHA-256").digest(data.getBytes(UTF_8));
ECDSASigner verifier = new ECDSASigner();
verifier.init(false, publicKeyParams);  // false = verification mode
boolean valid = verifier.verifySignature(hash, r, s);
```

**Форматы подписей в Taxoin:**
- Consumer подписывает: `"{consumer}:{provider}:{amount}:{service_ref}"`
- Provider подписывает: `"attest:{tx_id}:{provider}"`
- Обе подписи ОБЯЗАТЕЛЬНЫ для `AttestedTransaction.isValid()`

**Адрес:**
```java
byte[] pubBytes = pubKeyParams.getQ().getEncoded(false); // uncompressed
byte[] sha = MessageDigest.getInstance("SHA-256").digest(pubBytes);
String hex = HexFormat.of().formatHex(sha);
String address = "0x" + hex.substring(hex.length() - 40);
```

### 2. JGit merge strategy (ЛОВУШКА!)

```java
// ❌ НЕВЕРНО: заменяет всё дерево (-s theirs)
MergeStrategy.THEIRS

// ✅ ВЕРНО: recursive + prefer source (-X theirs). Требует JGit 6.2+!
git.merge()
   .include(repo.resolve(sourceBranch))
   .setStrategy(MergeStrategy.RECURSIVE)
   .setContentMergeStrategy(ContentMergeStrategy.THEIRS)
   .call();
```

### 3. Кастомные timestamps в коммитах

```java
long epochMs = (long)(blockTimestamp * 1000L);
PersonIdent ident = new PersonIdent("taxoin", "taxoin@localhost", epochMs, 0);
git.commit().setAuthor(ident).setCommitter(ident)
   .setAllowEmpty(true).setMessage(msg).call();
```

### 4. JSON совместимость с Python

```java
// Python: json.dumps(asdict(self), sort_keys=True)
// Java — обязательно, иначе SHA256 блока будет другим:
ObjectMapper mapper = new ObjectMapper()
    .configure(MapperFeature.SORT_PROPERTIES_ALPHABETICALLY, true)
    .configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true);
```

### 5. JsonStore — общий паттерн персистентности

Genesis, ServiceRegistry, ReputationTracker используют одинаковый паттерн.
Одна абстракция на всех:

```java
public class JsonStore<T> {
    private final Path path;
    private final ObjectMapper mapper;
    private final ReadWriteLock lock = new ReentrantReadWriteLock();

    public void save(T data) {
        lock.writeLock().lock();
        try { mapper.writeValue(path.toFile(), data); }
        finally { lock.writeLock().unlock(); }
    }

    public T load(Class<T> type) {
        if (!Files.exists(path)) return null;
        lock.readLock().lock();
        try { return mapper.readValue(path.toFile(), type); }
        finally { lock.readLock().unlock(); }
    }
}
```

### 6. Async: Python asyncio → Java virtual threads (Java 21)

```java
// async def submit_tx_to_branch(...)
Thread.ofVirtual().start(() -> branchManager.submitTx(tx));

// asyncio.Lock → ReentrantLock
private final ReentrantLock lock = new ReentrantLock();

// asyncio.Queue → LinkedBlockingQueue
private final LinkedBlockingQueue<Transaction> queue = new LinkedBlockingQueue<>(1000);
```

### 7. REST API — Quarkus

```java
@Path("/api")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class TaxoinApi {

    @Inject BlockchainEngine engine;
    @Inject ServiceRegistry services;
    @Inject ReputationTracker reputation;

    @POST @Path("/wallet")
    public WalletResponse createWallet() { ... }

    @GET @Path("/balance/{address}")
    public BalanceResponse getBalance(@PathParam("address") String address) { ... }

    @POST @Path("/tx/send")
    public TxResponse sendTx(TxRequest req) { ... }

    @GET @Path("/services")
    public List<ServiceRegistration> listServices(
        @QueryParam("type") String type,
        @QueryParam("min_rating") double minRating) { ... }

    @POST @Path("/testnet/faucet")
    public FaucetResponse faucet(FaucetRequest req) { ... }
}
```

`application.properties`:
```properties
quarkus.http.cors=true
quarkus.http.cors.origins=*
quarkus.http.port=47780
```

`wallet.html` → кладём в `src/main/resources/META-INF/resources/web/wallet.html`
Quarkus сервит автоматически по `/web/wallet.html`.

### 8. Reputation — формула рейтинга

```java
// Python: min(5.0, successful_tx * 0.1) - disputes * 0.5
double base    = Math.min(5.0, record.successfulTx * 0.1);
double penalty = record.disputes * 0.5;
record.rating  = Math.max(0.0, base - penalty);
```

---

## Зависимости Maven

```xml
<properties>
  <quarkus.platform.version>3.9.0</quarkus.platform.version>
  <java.version>21</java.version>
</properties>

<dependencies>
  <!-- Quarkus REST + Jackson -->
  <dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-rest</artifactId>
  </dependency>
  <dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-rest-jackson</artifactId>
  </dependency>

  <!-- JGit — минимум 6.2.0! -->
  <dependency>
    <groupId>org.eclipse.jgit</groupId>
    <artifactId>org.eclipse.jgit</artifactId>
    <version>6.9.0.202403050737-r</version>
  </dependency>

  <!-- Bouncy Castle — secp256k1 -->
  <dependency>
    <groupId>org.bouncycastle</groupId>
    <artifactId>bcprov-jdk18on</artifactId>
    <version>1.78.1</version>
  </dependency>

  <!-- CLI -->
  <dependency>
    <groupId>info.picocli</groupId>
    <artifactId>picocli</artifactId>
    <version>4.7.6</version>
  </dependency>

  <!-- HTTP клиент для внешних сервисов -->
  <dependency>
    <groupId>com.squareup.okhttp3</groupId>
    <artifactId>okhttp</artifactId>
    <version>4.11.0</version>
  </dependency>

  <!-- Тесты -->
  <dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-junit5</artifactId>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>io.rest-assured</groupId>
    <artifactId>rest-assured</artifactId>
    <scope>test</scope>
  </dependency>
</dependencies>
```

---

## Фазы реализации

| # | Фаза | Источник | Дней |
|---|------|---------|------|
| 1 | Core data structures + HashUtils | `core.py` | 1–2 |
| 2 | CryptoUtils (sign + verify, адреса) | `crypto_utils.py` | 2 |
| 3 | JsonStore<T> — персистентность | новое | 1 |
| 4 | JGitBlockchain (14 операций) | `git_backend.py` | 2–3 |
| 5 | Mempool + Miner | `mempool.py`, `miner.py` | 1 |
| 6 | BranchState + ConflictDetector | `branch_state.py`, `conflict_detector.py` | 1 |
| 7 | ValidatorNetwork + GossipProtocol | `validator_network.py`, `gossip_protocol.py` | 1 |
| 8 | TendermintConsensus | `consensus.py` | 1–2 |
| 9 | BranchManager (virtual threads) | `branch_manager.py` | 2–3 |
| 10 | BlockchainEngine | `blockchain.py` | 1 |
| 11 | Genesis + ServiceRegistry + AttestedTx + Reputation | новые модули | 3 |
| 12 | **Quarkus REST API (13 эндпоинтов)** | `api.py` | 3–4 |
| 13 | Статика + wallet.html | `web/` | 1 |
| 14 | CLI Picocli (25+ команд) | `cli.py` | 2–3 |
| 15 | E2E + API тесты (rest-assured) | `tests/` | 2 |

**Итого: 25–30 дней, 350+ JUnit тестов.**

---

## Spring Boot — план Б (замена за ~2 часа)

JGit, Bouncy Castle, Jackson, Picocli, OkHttp — **не меняются вообще**.

| Quarkus | Spring Boot |
|---------|------------|
| `@Path` | `@RestController` + `@RequestMapping` |
| `@GET`, `@POST` | `@GetMapping`, `@PostMapping` |
| `@Inject` | `@Autowired` |
| `@QueryParam` | `@RequestParam` |
| `@PathParam` | `@PathVariable` |
| `quarkus-junit5` | `spring-boot-starter-test` |
| `rest-assured` | `MockMvc` / `TestRestTemplate` |

---

## Что НЕ меняется при Java-порте

- JSON-формат блоков (байт-в-байт совместим с Python)
- double SHA256 для хэша блока
- Схема веток: `branch/{wallet}/{timestamp}_{seq:03d}`
- Tendermint: PROPOSE → PREVOTE → PRECOMMIT → COMMIT, 5/7 quorum
- Genesis: 3-of-N, 420 000 × 50 Ⓣ = 21 000 000 Ⓣ max
- Mutual Attestation: обе подписи обязательны
- Gossip: fanout=3, TTL=5
- REST API порт: **47780**
- Wallet JSON: `~/.taxoin/wallet.json`

---

## Верификация

```bash
# Юнит-тесты
mvn test

# API-тесты (rest-assured)
mvn verify -Pintegration

# Cross-language: Python пишет → Java читает
python3 -c "..."   # создаём блок
java -jar taxoin.jar status  # видим тот же блок

# UI
java -jar taxoin.jar api --port 47780
# открыть http://localhost:47780/web/wallet.html
```

---

## SIGNED NOT_FOR_COMPACTION.

**Версия:** 2.0 | **Дата:** 2026-05-20 | **Фреймворк:** Quarkus 3.x → Spring Boot 3.x (план Б)
