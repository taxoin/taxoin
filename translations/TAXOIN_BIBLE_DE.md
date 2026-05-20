# TAXOIN BIBLE (Taxoin-Bibel)

## Proof of Contribution (Beitragsnachweis) — Die Wahrheit der Dienstleistung

> SIGNED NOT_FOR_COMPACTION. Kanonische Spezifikation des Taxoin-Protokolls.

---

## Prolog

Am Anfang war der Proof of Work. Miner verbrannten Strom, um Hashes zu
berechnen, und das Netzwerk belohnte sie mit Münzen. Die Arbeit war
nützlich für die Sicherheit, aber nutzlos für die Menschheit.

Taxoin wurde geschaffen, um ein grundlegendes Problem zu lösen:

> **Ersetze nutzlose Berechnung durch nützlichen Beitrag.**

Nicht "eine CPU, eine Stimme" (Nakamoto, 2008).
Sondern **ein Mensch, ein Beitrag, ein Wert.**

---

## Teil I: Was ist ein Taxoin?

### I.1 Definition

Ein **Taxoin (Ⓣ)** ist eine Einheit des **nachgewiesenen Beitrags** zum Taxoin-Netzwerk.
Es kann nicht geschürft, geprägt oder aus dem Nichts erschaffen werden.

Jedes Ⓣ im Umlauf gelangte durch eines von zwei Toren ins Netzwerk:

| Tor | Mechanismus | Maximales Angebot |
|------|-----------|------------|
| **Genesis** | Proof of Personhood (Menschlichkeitsnachweis) — ein Mensch, eine Genesis | 21.000.000 Ⓣ (420.000 Menschen × 50Ⓣ) |
| **Dienstleistung (Service)** | Proof of Contribution (Beitragsnachweis) — Erbringung einer echten Dienstleistung | Unbegrenzt (begrenzt durch reale Wirtschaftstätigkeit) |

### I.2 Kernprinzip

> **Kein Taxoin ohne entsprechenden Beitrag.**

Dies ist das grundlegende Gesetz. Jede Münze ist gedeckt durch:
- Einen einzigartigen Menschen (Genesis), oder
- Eine verifizierte erbrachte Dienstleistung (Beitrag)

Es gibt keinen Miner, der Münzen aus Elektrizität gewinnt. Es gibt keinen
Staker, der passives Einkommen erzielt. Es gibt nur **Arbeit, die jemand
genug wertschätzte, um dafür zu bezahlen.**

---

## Teil II: Genesis — Proof of Personhood (Menschlichkeitsnachweis)

```
GLOBALE PARAMETER:
  GENESIS_REWARD     = 50 Ⓣ  (pro einzigartigem Menschen)
  MAX_GENESIS_SUPPLY = 21.000.000 Ⓣ
  MAX_PARTICIPANTS   = 420.000  (21M / 50)
```

### II.3 Die Genesis-Zeremonie

```
  ┌──────────────────────────────────────────────────────────────┐
  │              GENESIS-ZEREMONIE (GENESIS CEREMONY)            │
  │                                                              │
  │  1. Ein Mensch erzeugt ein Schlüsselpaar (secp256k1)         │
  │     → Adresse: 0xdeadbeef...                                 │
  │                                                              │
  │  2. Der Mensch kontaktiert einen Validator (persönlich /     │
  │     Videoanruf / durch vertrauenswürdigen Referenten)        │
  │     → Beweist, dass er ein einzigartiger Mensch ist          │
  │     → Unterschreibt eine Nachricht mit seinem Schlüssel:     │
  │       "Ich bin echt"                                         │
  │                                                              │
  │  3. Der Validator überprüft:                                 │
  │     → Die Signatur stimmt mit der angegebenen Adresse überein│
  │     → Der Mensch ist noch nicht im Genesis-Register          │
  │     → Der Mensch scheint eine echte, einzigartige Person     │
  │                                                              │
  │  4. Der Validator unterschreibt eine Bestätigung:            │
  │     "0xval1 bestätigt, dass 0xdeadbeef ein einzigartiger     │
  │      Mensch ist"                                             │
  │                                                              │
  │  5. 3-von-7 Validator-Bestätigungen nötig → Genesis bestätigt│
  │     → +50 Ⓣ gutgeschrieben an 0xdeadbeef                    │
  │     → Adresse zum Genesis-Register hinzugefügt (unveränderbar)│
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

---

## Teil III: Dienstleistungsökonomie — Proof of Contribution (Beitragsnachweis)

```python
@dataclass
class ServiceRegistration:
    provider: str              # Adresse (0x...)
    service_type: str          # "sms", "gpu", "taxi", ...
    price_per_unit: float      # Ⓣ pro Einheit
    description: str           # menschenlesbar
    endpoint: str              # Aufrufmethode (URL, Kontakt, API)
    attested_by: list[str]     # Validatoren, die geprüft haben
    rating: float = 0.0
    total_tx: int = 0
    created_at: float
```

---

## Teil IV: Transaktionslebenszyklus — Mutual Attestation (Gegenseitige Bestätigung)

```python
@dataclass
class AttestedTransaction:
    tx_id: str
    consumer: str              # wer zahlt
    provider: str              # wer bereitstellt
    service_ref: str           # Verweis auf ServiceRegistration
    amount: float              # Ⓣ für diese Transaktion
    consumer_sig: str          # "Ich habe die Dienstleistung erhalten" (ECDSA)
    provider_sig: str          # "Ich habe die Dienstleistung erbracht" (ECDSA)
    timestamp: float
    description: str           # optionale Bestelldetails
```

**Eine Transaktion ist NUR gültig, wenn beide Unterschriften vorhanden sind.**

---

## Teil V: Validatorkonsens (Validator Consensus)

```
  VALIDATOR_COUNT = 7
  BYZANTINE_FAULTS = 2       # f = floor((7-1)/3)
  QUORUM_SIZE = 5            # 2f + 1 = 5
```

Taxoin implementiert Tendermint-artigen Konsens (gebaut in Phase 4):

```
  VORSCHLAG (PROPOSE) → VORABSTIMMUNG (PREVOTE) → VORVERPFLICHTUNG (PRECOMMIT) → BESTÄTIGUNG (COMMIT)
```

---

## Teil VI: Die Git-Architektur

| Blockchain | Git |
|------------|-----|
| Block | Commit |
| Eltern-Hash | Eltern-Commit SHA |
| Merkle-Wurzel | Git-Tree SHA |
| Kette | Branch-Verlauf |
| Fork | Branch |
| Merge | Merge-Commit |
| Leichtclient | git clone --depth=1 |

**Keine Datenbank. Kein Index. Nur Git.**

---

## Teil VII: Tokenomics

```
  MAX_GENESIS_SUPPLY   = 21.000.000 Ⓣ  (harte Obergrenze)
  MAX_SERVICE_SUPPLY   = unbegrenzt     (begrenzt durch reale Wirtschaft)
```

```
  420.000 Menschen × 50 Ⓣ = 21.000.000 Ⓣ
  ──────────────────────────────────────
  Kein Premine. Kein ICO. Keine Insider-Zuteilung.
  Jeder Mensch erhält exakt den gleichen Betrag.
```

---

## Teil VIII: Sicherheitsmodell

| Bedrohung | Abschwächung |
|--------|-----------|
| Sybil-Angriff (gefälschte Menschen) | Menschlichkeitsnachweis + 3/7 Bestätigung |
| Doppelausgabe | Konflikterkennung (Phase 2) + Ausgabenverfolgung |
| Falsche Dienstleistung (Geld nehmen, nicht liefern) | Gegenseitige Bestätigung + Streitbeilegung |
| Validator-Kollusion (3 von 7 böswillig) | Byzantinische Fehlertoleranz (f=2) |
| Register-Manipulation | Git-Unveränderlichkeit + Validator-Signaturen |
| Saldo-Fälschung | ECDSA-Signaturen auf allen Transaktionen |
| Replay-Angriff | Nonce-Verfolgung pro Adresse |
| Netzwerk-Teilung | Klatschprotokoll + timeout-basierte Lebendigkeit |

---

## Teil IX: CLI-Referenz

```bash
  # Identität
  taxoin wallet new                  # Schlüsselpaar generieren
  taxoin wallet address              # Adresse anzeigen
  taxoin wallet show                 # Vollständige Wallet anzeigen

  # Genesis (einmalig pro Mensch)
  taxoin genesis request             # Menschliche Verifizierung beantragen
  taxoin genesis status              # Genesis-Status prüfen

  # Dienstleistungen
  taxoin service register            # Neue Dienstleistung registrieren
       --type sms
       --price 0.1
       --endpoint "https://..."
       --description "SMS-Gateway"
  taxoin service list                # Alle Dienstleistungen auflisten
       --type gpu
       --min-rating 4.0
  taxoin service show <address>      # Dienstleistungsdetails anzeigen
  taxoin service rate <address>      # Dienstleistung bewerten

  # Transaktionen
  taxoin tx send <provider>          # Für Dienstleistung bezahlen
       --amount 0.1
       --ref <service_id>
       --desc "SMS an +79123456789"
  taxoin tx attest <tx_id>           # Gegenseitige Bestätigung unterschreiben
  taxoin tx status <tx_id>           # Transaktionsstatus prüfen

  # Streitigkeiten
  taxoin dispute open <tx_id>        # Streitigkeit eröffnen
  taxoin dispute list                # Aktive Streitigkeiten auflisten

  # Reputation
  taxoin reputation <address>        # Reputation anzeigen
  taxoin reputation leaderboard      # Top-Anbieter

  # Netzwerk
  taxoin validator list              # Validatoren anzeigen
  taxoin status                      # Netzwerkstatus
```

---

## Teil X: Das große Ganze

### X.1 Was Taxoin verändert

| Ära | Mechanismus | Verschwendete Ressource |
|-----|-----------|----------------|
| **Vor 2008** | Tauschhandel / Fiatgeld | Vertrauen |
| **2008 (Bitcoin)** | Proof of Work | Elektrizität |
| **2015 (Ethereum)** | Proof of Stake | Kapital |
| **2026 (Taxoin)** | Proof of Contribution | Nichts |

### X.2 Das ultimative Ziel

Eine selbsttragende, dezentralisierte Dienstleistungsökonomie, in der:

- **Jeder verdienen kann**, indem er eine Dienstleistung anbietet, die er bereits besitzt
- **Jeder bezahlen kann** mit Münzen, die er durch Beiträge verdient hat
- **Niemand betrügen kann**, weil beide Parteien bestätigen müssen
- **Niemand ausgeschlossen wird**, weil die einzige Voraussetzung ist, Mensch zu sein
- **Keine Energie verschwendet wird**, weil Berechnung Menschen dient, nicht Hashes

### X.3 Der Name

**Taxoin** kommt von *Taxi* + *Coin* (Münze).

Nur **Dienstleistung, Zahlung und Nachweis.**

---

## SIGNED NOT_FOR_COMPACTION.

**Version:** 1.0  
**Datum:** 2026-05-20  
**Status:** Aktiv
