# TAXOIN BIBLE (Bible du Taxoin)

## Preuve de Contribution (Proof of Contribution) — La Vérité du Service

> SIGNED NOT_FOR_COMPACTION. Spécification canonique du protocole Taxoin.

---

## Prologue

Au commencement, il y avait la preuve de travail. Les mineurs brûlaient de
l'électricité pour calculer des hashs, et le réseau les récompensait avec des
pièces. Le travail était utile pour la sécurité, mais inutile pour l'humanité.

Taxoin a été créé pour résoudre un problème fondamental :

> **Remplacer le calcul inutile par une contribution utile.**

Pas « un CPU, une voix » (Nakamoto, 2008).
Mais **un humain, une contribution, une valeur.**

---

## Partie I : Qu'est-ce qu'un Taxoin ?

### I.1 Définition

Un **Taxoin (Ⓣ)** est une unité de **contribution prouvée** au réseau Taxoin.
Il ne peut être miné, frappé ou créé à partir de rien.

Chaque Ⓣ en circulation est entré dans le réseau par l'une des deux portes :

| Porte | Mécanisme | Approvisionnement Maximal |
|------|-----------|------------|
| **Genèse (Genesis)** | Preuve d'Humanité (Proof of Personhood) — un humain, une genèse | 21 000 000 Ⓣ (420 000 personnes × 50Ⓣ) |
| **Service** | Preuve de Contribution (Proof of Contribution) — fournir un service réel | Illimité (limité par l'activité économique réelle) |

### I.2 Principe Fondamental

> **Pas de Taxoin sans contribution correspondante.**

C'est la loi fondamentale. Chaque pièce est adossée à :
- Un être humain unique (genèse), ou
- Un service vérifié rendu (contribution)

Il n'y a pas de mineur extrayant des pièces de l'électricité. Il n'y a pas
de stakeur gagnant un revenu passif. Il y a seulement **un travail que
quelqu'un a suffisamment valorisé pour payer.**

---

## Partie II : Genèse (Genesis) — Preuve d'Humanité (Proof of Personhood)

```
PARAMÈTRES GLOBAUX :
  GENESIS_REWARD     = 50 Ⓣ  (par personne unique)
  MAX_GENESIS_SUPPLY = 21 000 000 Ⓣ
  MAX_PARTICIPANTS   = 420 000  (21M / 50)
```

### II.3 La Cérémonie de la Genèse

```
  ┌──────────────────────────────────────────────────────────────┐
  │            CÉRÉMONIE DE LA GENÈSE (GENESIS CEREMONY)        │
  │                                                              │
  │  1. L'humain génère une paire de clés (secp256k1)            │
  │     → adresse : 0xdeadbeef...                                │
  │                                                              │
  │  2. L'humain contacte un validateur (en personne /           │
  │     appel vidéo / via un référent de confiance)              │
  │     → Prouve qu'il est un humain unique                      │
  │     → Signe un message avec sa clé : "Je suis réel"          │
  │                                                              │
  │  3. Le validateur vérifie :                                  │
  │     → La signature correspond à l'adresse déclarée           │
  │     → L'humain n'est pas déjà dans le registre de genèse     │
  │     → L'humain semble être une personne réelle et unique     │
  │                                                              │
  │  4. Le validateur signe une attestation :                    │
  │     "0xval1 atteste que 0xdeadbeef est un humain unique"     │
  │                                                              │
  │  5. Besoin de 3 attestations sur 7 validateurs → genèse      │
  │     approuvée                                                │
  │     → +50 Ⓣ crédités à 0xdeadbeef                           │
  │     → Adresse ajoutée au Registre de Genèse (immuable)       │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

---

## Partie III : Économie de Services — Preuve de Contribution (Proof of Contribution)

```python
@dataclass
class ServiceRegistration:
    provider: str              # adresse (0x...)
    service_type: str          # "sms", "gpu", "taxi", ...
    price_per_unit: float      # Ⓣ par unité
    description: str           # lisible par l'humain
    endpoint: str              # comment appeler (URL, contact, API)
    attested_by: list[str]     # validateurs ayant vérifié
    rating: float = 0.0
    total_tx: int = 0
    created_at: float
```

---

## Partie IV : Cycle de Vie d'une Transaction — Attestation Mutuelle (Mutual Attestation)

```python
@dataclass
class AttestedTransaction:
    tx_id: str
    consumer: str              # qui paie
    provider: str              # qui fournit
    service_ref: str           # lien vers ServiceRegistration
    amount: float              # Ⓣ pour cette transaction
    consumer_sig: str          # "J'ai reçu le service" (ECDSA)
    provider_sig: str          # "J'ai fourni le service" (ECDSA)
    timestamp: float
    description: str           # détails de la commande (optionnel)
```

**Une transaction est valide UNIQUEMENT si les deux signatures sont présentes.**

---

## Partie V : Consensus des Validateurs (Validator Consensus)

```
  VALIDATOR_COUNT = 7
  BYZANTINE_FAULTS = 2       # f = floor((7-1)/3)
  QUORUM_SIZE = 5            # 2f + 1 = 5
```

Taxoin implémente un consensus de style Tendermint (construit en Phase 4) :

```
  PROPOSER (PROPOSE) → PRÉVOTER (PREVOTE) → PRÉ-ENGAGER (PRECOMMIT) → VALIDER (COMMIT)
```

---

## Partie VI : L'Architecture Git

| Blockchains | Git |
|------------|-----|
| Bloc | Commit |
| Hash parent | SHA du commit parent |
| Racine de Merkle | SHA de l'arbre Git |
| Chaîne | Historique de branche |
| Fork | Branche |
| Fusion (Merge) | Commit de fusion |
| Client léger | git clone --depth=1 |

**Pas de base de données. Pas d'index. Seulement Git.**

---

## Partie VII : Tokenomics

```
  MAX_GENESIS_SUPPLY   = 21 000 000 Ⓣ  (plafond dur)
  MAX_SERVICE_SUPPLY   = illimité       (limité par l'économie réelle)
```

```
  420 000 humains × 50 Ⓣ = 21 000 000 Ⓣ
  ──────────────────────────────────────
  Pas de prémine. Pas d'ICO. Pas d'allocation d'initiés.
  Chaque humain reçoit exactement le même montant.
```

---

## Partie VIII : Modèle de Sécurité

| Menace | Atténuation |
|--------|-----------|
| Attaque Sybil (faux humains) | Preuve d'Humanité + attestation 3/7 |
| Double dépense | Détecteur de conflits (Phase 2) + suivi des dépenses |
| Faux service (prendre l'argent, ne pas livrer) | Attestation mutuelle + résolution des litiges |
| Collusion de validateurs (3 sur 7 malveillants) | Tolérance aux pannes byzantines (f=2) |
| Manipulation du registre | Immuabilité de Git + signatures des validateurs |
| Falsification de solde | Signatures ECDSA sur toutes les transactions |
| Attaque par rejeu | Suivi de nonce par adresse |
| Partition réseau | Protocole de rumeur + vivacité basée sur le timeout |

---

## Partie IX : Référence CLI

```bash
  # Identité
  taxoin wallet new                  # Générer une paire de clés
  taxoin wallet address              # Afficher votre adresse
  taxoin wallet show                 # Afficher le portefeuille complet

  # Genèse (une fois par humain)
  taxoin genesis request             # Demander une vérification humaine
  taxoin genesis status              # Vérifier le statut de la genèse

  # Services
  taxoin service register            # Enregistrer un nouveau service
       --type sms
       --price 0.1
       --endpoint "https://..."
       --description "Passerelle SMS"
  taxoin service list                # Lister tous les services
       --type gpu
       --min-rating 4.0
  taxoin service show <address>      # Afficher les détails du service
  taxoin service rate <address>      # Évaluer un service

  # Transactions
  taxoin tx send <provider>          # Payer pour un service
       --amount 0.1
       --ref <service_id>
       --desc "SMS au +79123456789"
  taxoin tx attest <tx_id>           # Signer l'attestation mutuelle
  taxoin tx status <tx_id>           # Vérifier le statut de la transaction

  # Litiges
  taxoin dispute open <tx_id>        # Ouvrir un litige
  taxoin dispute list                # Lister les litiges actifs

  # Réputation
  taxoin reputation <address>        # Afficher la réputation
  taxoin reputation leaderboard      # Meilleurs fournisseurs

  # Réseau
  taxoin validator list              # Afficher les validateurs
  taxoin status                      # État du réseau
```

---

## Partie X : La Vue d'Ensemble

### X.1 Ce que Taxoin change

| Ère | Mécanisme | Ressource gaspillée |
|-----|-----------|----------------|
| **Avant 2008** | Troc / Monnaie fiduciaire | Confiance |
| **2008 (Bitcoin)** | Preuve de Travail (Proof of Work) | Électricité |
| **2015 (Ethereum)** | Preuve d'Enjeu (Proof of Stake) | Capital |
| **2026 (Taxoin)** | Preuve de Contribution (Proof of Contribution) | Rien |

### X.2 L'Objectif Ultime

Une économie de services décentralisée et autosuffisante où :

- **N'importe qui peut gagner** en fournissant un service qu'il possède déjà
- **N'importe qui peut payer** avec des pièces gagnées en contribuant
- **Personne ne peut tricher** car les deux parties doivent attester
- **Personne n'est exclu** car la seule condition est d'être humain
- **Aucune énergie n'est gaspillée** car le calcul sert les personnes, pas les hashs

### X.3 Le Nom

**Taxoin** vient de *taxi* + *coin* (pièce).

Simplement **service, paiement et preuve.**

---

## SIGNED NOT_FOR_COMPACTION.

**Version :** 1.0  
**Date :** 2026-05-20  
**Statut :** Actif
