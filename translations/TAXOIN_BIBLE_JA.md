# TAXOIN BIBLE (タクソインの聖典)

## 貢献証明 (Proof of Contribution) — サービスの真実

> SIGNED NOT_FOR_COMPACTION. Taxoin プロトコルの正規仕様書。

---

## 序文

初めに、作業証明 (Proof of Work) があった。マイナーは電気を燃やして
ハッシュを計算し、ネットワークは彼らにコインを報酬として与えた。
その仕事はセキュリティには有用だったが、人類には無用だった。

Taxoin は一つの根本的な問題を解決するために作られた：

> **無駄な計算を有用な貢献に置き換える。**

「1 CPU、1 票」(中本哲史、2008) ではない。
しかし **1 人の人間、1 つの貢献、1 つの価値。**

---

## 第I部: Taxoin とは何か？

### I.1 定義

**Taxoin (Ⓣ)** は Taxoin ネットワークへの**証明された貢献**の単位である。
採掘も鋳造も不可能で、無から生み出すこともできない。

流通している各 Ⓣ は、次の 2 つのゲートのいずれかを通じてネットワークに入った：

| ゲート | メカニズム | 最大供給量 |
|------|-----------|------------|
| **創世 (Genesis)** | 人間性の証明 (Proof of Personhood) — 一人の人間、一つの創世 | 21,000,000 Ⓣ (420,000 人 × 50Ⓣ) |
| **サービス (Service)** | 貢献の証明 (Proof of Contribution) — 実際のサービスの提供 | 無制限 (実際の経済活動によって制限される) |

### I.2 基本原則

> **対応する貢献なしに Taxoin は存在しない。**

これが基本法則である。各コインは以下によって裏付けられている：
- ユニークな人間 (創世)、または
- 検証済みの提供されたサービス (貢献)

電気からコインを抽出するマイナーはいない。受動的収入を得る
ステーカーはいない。あるのはただ、**誰かが支払う価値があると
評価した仕事**だけである。

---

## 第II部: 創世 (Genesis) — 人間性の証明 (Proof of Personhood)

### II.1 ブートストラップ問題

サービス経済はゼロからは始まれない：
- 誰もサービスに支払うコインを持っていない
- 誰もサービスを提供せずにコインを稼げない
- 行き詰まり

### II.2 解決策: 一人の人間、一つの創世

Taxoin は創世コインを「マイナー」や「投資家」に配布するのではなく、
バリデータセットによって検証された**ユニークな人間**に配布する。

```
グローバルパラメータ:
  GENESIS_REWARD     = 50 Ⓣ  (ユニークな人間あたり)
  MAX_GENESIS_SUPPLY = 21,000,000 Ⓣ
  MAX_PARTICIPANTS   = 420,000  (21M / 50)
```

---

## 第III部: サービス経済 — 貢献の証明 (Proof of Contribution)

```python
@dataclass
class ServiceRegistration:
    provider: str              # アドレス (0x...)
    service_type: str          # "sms", "gpu", "taxi", ...
    price_per_unit: float      # 単位あたり Ⓣ
    description: str           # 人間が読める説明
    endpoint: str              # 呼び出し方法 (URL, 連絡先, API)
    attested_by: list[str]     # 検証したバリデータ
    rating: float = 0.0
    total_tx: int = 0
    created_at: float
```

---

## 第IV部: トランザクションライフサイクル — 相互証明 (Mutual Attestation)

```python
@dataclass
class AttestedTransaction:
    tx_id: str
    consumer: str              # 支払う人
    provider: str              # 提供する人
    service_ref: str           # ServiceRegistration へのリンク
    amount: float              # このトランザクションの Ⓣ
    consumer_sig: str          # "サービスを受けました" (ECDSA)
    provider_sig: str          # "サービスを提供しました" (ECDSA)
    timestamp: float
    description: str           # 注文詳細 (オプション)
```

**トランザクションは両方の署名が存在する場合にのみ有効。**

---

## 第V部: バリデータ合意 (Validator Consensus)

```
  VALIDATOR_COUNT = 7
  BYZANTINE_FAULTS = 2       # f = floor((7-1)/3)
  QUORUM_SIZE = 5            # 2f + 1 = 5
```

Taxoin は Tendermint スタイルの合意を実装しています (フェーズ4で構築)：

```
  PROPOSE → PREVOTE → PRECOMMIT → COMMIT
```

---

## 第VI部: Git アーキテクチャ

| ブロックチェーン | Git |
|------------|-----|
| ブロック | コミット |
| 親ハッシュ | 親コミット SHA |
| マークルルート | Git ツリー SHA |
| チェーン | ブランチ履歴 |
| フォーク | ブランチ |
| マージ | マージコミット |
| ライトクライアント | git clone --depth=1 |

**データベース不要。インデックス不要。Git だけ。**

---

## 第VII部: トークノミクス (Tokenomics)

```
  MAX_GENESIS_SUPPLY   = 21,000,000 Ⓣ  (ハードキャップ)
  MAX_SERVICE_SUPPLY   = 無制限        (実際の経済によって制限)
```

```
  420,000 人 × 50 Ⓣ = 21,000,000 Ⓣ
  ──────────────────────────────────────
  プリマインなし。ICOなし。インサイダー割り当てなし。
  全員がまったく同じ金額を受け取る。
```

---

## 第VIII部: セキュリティモデル

| 脅威 | 緩和策 |
|--------|-----------|
| Sybil 攻撃 (偽の人間) | 人間性の証明 + 3/7 証明 |
| 二重支払い | 競合検出器 (フェーズ2) + 支出追跡 |
| 偽サービス (金を受け取り、提供しない) | 相互証明 + 紛争解決 |
| バリデータの共謀 (3/7 が悪意) | ビザンチン障害耐性 (f=2) |
| レジストリ操作 | Git 不変性 + バリデータ署名 |
| 残高偽造 | 全トランザクションの ECDSA 署名 |
| リプレイ攻撃 | アドレスごとの Nonce 追跡 |
| ネットワーク分割 | ゴシッププロトコル + タイムアウトベースの活性 |

---

## 第IX部: CLI リファレンス

```bash
  # アイデンティティ
  taxoin wallet new                  # キーペアを生成
  taxoin wallet address              # アドレスを表示
  taxoin wallet show                 # ウォレットの詳細を表示

  # 創世 (一人につき一回)
  taxoin genesis request             # 人間確認をリクエスト
  taxoin genesis status              # 創世ステータスを確認

  # サービス
  taxoin service register            # 新しいサービスを登録
       --type sms
       --price 0.1
       --endpoint "https://..."
       --description "SMS ゲートウェイ"
  taxoin service list                # 全サービスを一覧表示
       --type gpu
       --min-rating 4.0
  taxoin service show <address>      # サービス詳細を表示
  taxoin service rate <address>      # サービスを評価

  # トランザクション
  taxoin tx send <provider>          # サービスの支払い
       --amount 0.1
       --ref <service_id>
       --desc "+79123456789 に SMS"
  taxoin tx attest <tx_id>           # 相互証明に署名
  taxoin tx status <tx_id>           # トランザクションステータスを確認

  # 紛争
  taxoin dispute open <tx_id>        # 紛争を開始
  taxoin dispute list                # アクティブな紛争を一覧表示

  # 評判
  taxoin reputation <address>        # 評判を表示
  taxoin reputation leaderboard      # トッププロバイダー

  # ネットワーク
  taxoin validator list              # バリデータを表示
  taxoin status                      # ネットワークステータス
```

---

## 第X部: 全体像

### X.1 Taxoin が変えるもの

| 時代 | メカニズム | 浪費されるリソース |
|-----|-----------|----------------|
| **2008年以前** | 物々交換 / 法定通貨 | 信頼 |
| **2008年 (Bitcoin)** | 作業証明 (Proof of Work) | 電気 |
| **2015年 (Ethereum)** | 持分証明 (Proof of Stake) | 資本 |
| **2026年 (Taxoin)** | 貢献証明 (Proof of Contribution) | なし |

### X.2 最終目標

自律分散型サービス経済：

- **誰でも稼げる** — すでに持っているサービスを提供することで
- **誰でも支払える** — 貢献によって稼いだコインで
- **誰も不正できない** — 両者の証明が必要だから
- **誰も排除されない** — 唯一の要件は人間であること
- **エネルギーは無駄にならない** — 計算は人に仕え、ハッシュには仕えない

### X.3 名前の由来

**Taxoin** は *taxi* + *coin* に由来する。

ただ **サービス、支払い、そして証明。**

---

## SIGNED NOT_FOR_COMPACTION.

**バージョン:** 1.0  
**日付:** 2026-05-20  
**ステータス:** 有効
