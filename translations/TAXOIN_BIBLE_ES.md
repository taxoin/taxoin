# TAXOIN BIBLE (Biblia de Taxoin)

## Prueba de Contribución (Proof of Contribution) — La Verdad del Servicio

> SIGNED NOT_FOR_COMPACTION. Especificación canónica del protocolo Taxoin.

---

## Prólogo

En el principio, existía la prueba de trabajo. Los mineros quemaban electricidad
para computar hashes, y la red los recompensaba con monedas. El trabajo era
útil para la seguridad, pero inútil para la humanidad.

Taxoin fue creado para resolver un problema fundamental:

> **Reemplazar el cálculo inútil con contribución útil.**

No "una CPU, un voto" (Nakamoto, 2008).
Sino **un humano, una contribución, un valor.**

---

## Parte I: ¿Qué es un Taxoin?

### I.1 Definición

Un **Taxoin (Ⓣ)** es una unidad de **contribución probada** a la red Taxoin.
No puede ser minado, acuñado ni creado de la nada.

Cada Ⓣ en circulación entró a la red por una de dos puertas:

| Puerta | Mecanismo | Suministro Máximo |
|------|-----------|------------|
| **Génesis (Genesis)** | Prueba de Humanidad (Proof of Personhood) — un humano, un génesis | 21,000,000 Ⓣ (420,000 personas × 50Ⓣ) |
| **Servicio (Service)** | Prueba de Contribución (Proof of Contribution) — proveer un servicio real | Ilimitado (limitado por la actividad económica real) |

### I.2 Principio Fundamental

> **No existe Taxoin sin una contribución correspondiente.**

Esta es la ley fundamental. Cada moneda está respaldada por:
- Un ser humano único (génesis), o
- Un servicio verificado prestado (contribución)

No hay minero extrayendo monedas de la electricidad. No hay staker
ganando ingresos pasivos. Solo hay **trabajo que alguien valoró lo
suficiente como para pagar por él.**

### I.3 No-Principios (Lo que Taxoin NO es)

| ❌ No es esto | ✅ Sino esto |
|------------|------------|
| Activo de inversión | Medio de intercambio por servicios |
| Reserva de valor | Unidad de contribución |
| Recompensa de minería | Pago por servicio |
| Ingreso pasivo | Ingreso por trabajo activo |
| Token especulativo | Prueba de trabajo realizado |

---

## Parte II: Génesis (Genesis) — Prueba de Humanidad (Proof of Personhood)

### II.1 El Problema de Arranque

Una economía de servicios no puede comenzar desde cero:
- Nadie tiene monedas para pagar servicios
- Nadie puede ganar monedas sin proveer servicios
- Punto muerto

### II.2 Solución: Un Humano, Un Génesis

Taxoin distribuye monedas de génesis no a "mineros" o "inversores"
sino a **seres humanos únicos** verificados por el conjunto de validadores.

```
PARÁMETROS GLOBALES:
  GENESIS_REWARD     = 50 Ⓣ  (por persona única)
  MAX_GENESIS_SUPPLY = 21,000,000 Ⓣ
  MAX_PARTICIPANTS   = 420,000  (21M / 50)
```

### II.3 La Ceremonia de Génesis

```
  ┌──────────────────────────────────────────────────────────────┐
  │              CEREMONIA DE GÉNESIS (GENESIS CEREMONY)         │
  │                                                              │
  │  1. El humano genera un par de claves (secp256k1)            │
  │     → dirección: 0xdeadbeef...                               │
  │                                                              │
  │  2. El humano contacta a un validador (en persona /          │
  │     videollamada / a través de un referente de confianza)    │
  │     → Prueba que es un humano único                          │
  │     → Firma un mensaje con su clave: "Soy real"              │
  │                                                              │
  │  3. El validador verifica:                                   │
  │     → La firma coincide con la dirección declarada           │
  │     → El humano no está ya en el registro de génesis         │
  │     → El humano parece ser una persona real y única          │
  │                                                              │
  │  4. El validador firma una atestación:                       │
  │     "0xval1 atestigua que 0xdeadbeef es un humano único"     │
  │                                                              │
  │  5. Se necesitan 3 de 7 atestaciones de validadores          │
  │     → génesis aprobado                                       │
  │     → +50 Ⓣ acreditados a 0xdeadbeef                        │
  │     → Dirección agregada al Registro de Génesis (inmutable)  │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

### II.4 Resistencia Sybil

Un ataque Sybil (una persona creando 1000 carteras) se previene mediante:

| Capa | Protección |
|-------|-----------|
| **Prueba de Humanidad (Proof of Personhood)** | Los validadores verifican humanos, no carteras |
| **Atestación 3-de-7** | Se necesitan 3 validadores independientes para confirmar |
| **Registro inmutable** | Cada dirección puede recibir génesis solo una vez |
| **Reputación** | Los validadores que aprueban Sybils pierden reputación |

Esto no es perfecto. Requiere confianza social. Pero es la única
forma conocida de distribuir monedas de manera justa sin:
- Prueba de Trabajo (PoW) (centralización ASIC)
- Prueba de Participación (PoS) (los ricos se hacen más ricos)
- Oferta Inicial de Moneda (ICO) (ventaja para iniciados)
- Airdrop (granjas Sybil)

### II.5 El Límite de Génesis

```
MAX_GENESIS_SUPPLY = 21,000,000 Ⓣ
```

Este es el **máximo absoluto** de monedas de génesis. Una vez que
420,000 humanos hayan sido atestiguados, no se pueden crear más
monedas de génesis.

Después de agotado el génesis, todos los nuevos Ⓣ en circulación
provienen exclusivamente de transacciones de servicio (una persona
pagando a otra por un servicio).

---

## Parte III: Economía de Servicios — Prueba de Contribución (Proof of Contribution)

### III.1 ¿Qué es un Servicio?

Un servicio es cualquier contribución que un participante de la red
provee a otro. El servicio se **registra en la cadena** y tiene un
**precio fijado por el proveedor.**

Ejemplos:
```
  Tipo de Servicio      Proveedor           Precio
  ─────────────────────────────────────────────────
  Pasarela SMS          Teléfono de Alice   0.1 Ⓣ/SMS
  Cómputo GPU           Granja de Bob      5.0 Ⓣ/hora
  Acceso API            Modelo de Carol    0.5 Ⓣ/llamada
  Viaje (taxi)          Auto de Dave       3.0 Ⓣ/km
  Almacenamiento        Servidor de Eve    0.01 Ⓣ/MB/mes
  Ciclo CPU             Escritorio de Frank 0.001 Ⓣ/CPU-hora
  Retransmisión         Router de Grace    0.05 Ⓣ/GB
  Revisión humana       Expertise de Hank  10.0 Ⓣ/revisión
```

No hay límite en lo que puede ser un servicio. El mercado decide
qué servicios tienen valor y a qué precio.

### III.2 Registro de Servicios (Service Registry)

Cada servicio se registra en la cadena como un commit de git:

```python
@dataclass
class ServiceRegistration:
    provider: str              # dirección (0x...)
    service_type: str          # "sms", "gpu", "taxi", ...
    price_per_unit: float      # Ⓣ por unidad
    description: str           # legible por humanos
    endpoint: str              # cómo llamarlo (URL, contacto, API)
    attested_by: list[str]     # validadores que verificaron
    rating: float = 0.0
    total_tx: int = 0
    created_at: float
```

El registro de servicios se almacena en git notes (infraestructura existente).
Cualquiera puede consultar: "muéstrame todas las pasarelas SMS con
calificación > 4.0."

Los validadores verifican que un servicio sea real antes de aprobar
el registro:
- Para una pasarela SMS: enviar un SMS de prueba, verificar entrega
- Para cómputo GPU: ejecutar un benchmark, verificar resultado
- Para un viaje en taxi: verificar licencia de conducir y vehículo

### III.3 Precios

El proveedor fija el precio. El mercado lo regula.

```
  Precio alto + mal servicio → sin clientes → proveedor baja el precio
  Precio bajo + buen servicio → muchos clientes → proveedor gana reputación
  Fraude (tomar dinero, no dar servicio) → disputa → arbitraje de validador
                                           → penalización de reputación
                                           → posible prohibición
```

Ninguna autoridad central fija los precios. Ningún algoritmo ajusta
las tarifas. Mercado puramente libre.

### III.4 Descubrimiento

Los consumidores descubren servicios a través del registro:

```
  taxoin service list --type sms --min-rating 4.0
  → 0xalice: 0.1 Ⓣ/SMS, calificación 4.8 (942 transacciones)
  → 0xbob:   0.15 Ⓣ/SMS, calificación 4.2 (312 transacciones)
```

---

## Parte IV: Ciclo de Vida de la Transacción — Atestación Mutua (Mutual Attestation)

### IV.1 El Problema Central

> ¿Cómo sabe la cadena de bloques que un servicio fue realmente entregado?

En las cadenas de bloques tradicionales, esto se llama el **Problema del Oráculo (Oracle Problem).**
La respuesta de Taxoin: **Atestación Mutua (Mutual Attestation)** — ambas partes firman.

### IV.2 La Transacción Atestiguada (AttestedTransaction)

```python
@dataclass
class AttestedTransaction:
    tx_id: str
    consumer: str              # quién paga
    provider: str              # quién provee
    service_ref: str           # enlace a ServiceRegistration
    amount: float              # Ⓣ por esta transacción
    consumer_sig: str          # "Recibí el servicio" (ECDSA)
    provider_sig: str          # "Proveí el servicio" (ECDSA)
    timestamp: float
    description: str           # detalles del pedido (opcional)
```

**Una transacción es válida SOLO si ambas firmas están presentes.**

### IV.3 El Ciclo de Vida

```
  ┌─────────────────────────────────────────────────────────────────┐
  │            CICLO DE VIDA DE LA TRANSACCIÓN                       │
  │                                                                 │
  │  1. EL CONSUMIDOR EXPLORA EL REGISTRO                           │
  │     → Encuentra un servicio que necesita                        │
  │     → Revisa precio, calificación, reputación del proveedor     │
  │                                                                 │
  │  2. EL CONSUMIDOR ENVÍA UNA SOLICITUD                           │
  │     → Llama al endpoint del servicio (fuera de cadena)          │
  │     → "Quiero 1 SMS al +79123456789"                           │
  │                                                                 │
  │  3. EL PROVEEDOR EJECUTA EL SERVICIO (fuera de cadena)          │
  │     → Envía el SMS                                              │
  │     → Espera confirmación de entrega                            │
  │                                                                 │
  │  4. ATESTACIÓN MUTUA (Mutual Attestation)                       │
  │     → El consumidor firma: "Confirmo, SMS recibido"             │
  │     → El proveedor firma: "Confirmo, SMS entregado"             │
  │     → Ambas firmas → AttestedTransaction creada                 │
  │                                                                 │
  │  5. TRANSFERENCIA DE SALDO (en cadena mediante consenso)        │
  │     → Los validadores verifican ambas firmas (ECDSA)            │
  │     → Los validadores verifican que el consumidor tenía saldo   │
  │     → 5 de 7 validadores confirman → transacción confirmada     │
  │     → -0.1 Ⓣ consumidor, +0.1 Ⓣ proveedor                     │
  │     → +1 reputación para ambas partes                           │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘
```

### IV.4 Retención de Saldo (Balance Hold)

Durante la ejecución del servicio, las monedas del consumidor están
**retenidas** (reservadas) pero no gastadas aún:

```
  Saldo del consumidor ANTES:   100.0 Ⓣ
    ├── disponible:              99.9 Ⓣ
    ├── retenido:                 0.1 Ⓣ  (SMS en progreso)
    └── bloqueado:                0.0 Ⓣ

  Después de atestación mutua → retenido gastado, acreditado al proveedor
  Después de 10 bloques de tiempo → retenido devuelto al consumidor
                                    (servicio fallido)
```

### IV.5 Resolución de Disputas (Dispute Resolution)

¿Qué pasa si una parte hace trampa?

| Escenario | Resolución |
|----------|-----------|
| El consumidor firma, el proveedor no | Tiempo muerto → retención devuelta al consumidor |
| El proveedor entrega, el consumidor se niega a firmar | El proveedor abre disputa → validadores revisan evidencia → regla 5/7 |
| Ambos firman, pero el servicio era falso | Los validadores detectan patrón → disputa → penalización de reputación |
| El proveedor toma el dinero y no entrega | El consumidor abre disputa → validadores deciden → fondos devueltos |

Los validadores son los árbitros finales. Con 7 validadores y quórum
de 5/7, se pueden tolerar hasta 2 validadores maliciosos
(tolerancia a fallos bizantinos).

---

## Parte V: Consenso de Validadores (Validator Consensus)

### V.1 El Conjunto de Validadores (Validator Set)

Taxoin utiliza un **conjunto de validadores autorizados** de 7 nodos.

```
  VALIDATOR_COUNT = 7
  BYZANTINE_FAULTS = 2       # f = floor((7-1)/3)
  QUORUM_SIZE = 5            # 2f + 1 = 5
```

Esto significa: hasta 2 validadores pueden ser maliciosos o fallar,
y la red sigue funcionando correctamente.

### V.2 Qué Hacen los Validadores

| Rol | Descripción |
|------|------------|
| **Atestación de génesis (Genesis attestation)** | Verificar nuevos humanos (3/7) |
| **Verificación de servicios (Service verification)** | Verificar nuevos registros de servicios |
| **Validación de transacciones (Transaction validation)** | Verificar firmas, saldo, doble gasto |
| **Arbitraje de disputas (Dispute arbitration)** | Resolver conflictos entre partes |
| **Consenso de fusión (Merge consensus)** | Finalizar transiciones de estado (Fase 4 existente) |

### V.3 Protocolo de Consenso

Taxoin implementa consenso estilo Tendermint (construido en la Fase 4):

```
  PROPONER (PROPOSE) → PREVOTAR (PREVOTE) → PRE-COMPROMETER (PRECOMMIT) → CONFIRMAR (COMMIT)
```

Cada ronda:
1. Un validador propone un lote de transacciones atestiguadas
2. Los 7 validadores validan independientemente (quórum 5/7)
3. El lote validado se fusiona en la cadena principal mediante git
4. El estado se actualiza (saldos, reputación, registro de servicios)

El consenso Tendermint está completamente implementado y probado
(200 pruebas, todas exitosas).

### V.4 Honestidad de los Validadores

Los validadores no son anónimos. Son entidades conocidas que:
- Participaron en el génesis (Prueba de Humanidad)
- Tienen reputación en juego
- Pueden ser reemplazados por voto de 5/7 si son maliciosos

Un validador deshonesto:
1. Pierde reputación
2. Puede ser expulsado por voto de 5/7
3. Un validador de reemplazo es atestiguado

---

## Parte VI: La Arquitectura Git

### VI.1 ¿Por Qué Git?

Taxoin está construido sobre Git porque Git es un DAG (Grafo Acíclico Dirigido) probado:

| Cadenas de Bloques | Git |
|------------|-----|
| Bloque | Commit |
| Hash padre | SHA del commit padre |
| Raíz Merkle | SHA del árbol Git |
| Cadena | Historial de rama |
| Bifurcación | Rama |
| Fusión | Commit de fusión |
| Cliente ligero | git clone --depth=1 |

### VI.2 Cómo Funciona

```
  .taxoin/
  └── .git/
      ├── objects/       # bloques como commits git
      ├── refs/heads/    # ramas + cadena principal
      └── NOTES_MERGE/   # registro de servicios, metadatos
```

Cada lote de transacciones es un commit de git. Cada registro de
servicio es una nota de git. Cada cambio de estado es una fusión de git.

**Sin base de datos. Sin índice. Solo Git.**

### VI.3 Ventajas

| Propiedad | Cómo lo Provee Git |
|----------|-------------------|
| Inmutabilidad | Direccionamiento de contenido basado en SHA |
| Historial | git log — rastro de auditoría completo |
| Distribución | git clone — nodo completo en segundos |
| Cliente ligero | git clone --depth=1 |
| Respaldo | git push — respaldo instantáneo a cualquier remoto |
| Verificación | git verify — verificación de firmas |
| Bifurcación | git branch — experimentación en paralelo |

---

## Parte VII: Tokenómica (Tokenomics)

### VII.1 Suministro Total

```
  MAX_GENESIS_SUPPLY   = 21,000,000 Ⓣ  (límite duro)
  MAX_SERVICE_SUPPLY   = ilimitado      (limitado por la economía real)
```

El suministro de génesis tiene un límite de 21 millones. El suministro
de servicios es ilimitado, pero cada Ⓣ en el suministro de servicios
es **ganado**, no creado.

### VII.2 Distribución de Génesis

```
  420,000 humanos × 50 Ⓣ = 21,000,000 Ⓣ
  ──────────────────────────────────────
  Sin premineo. Sin ICO. Sin asignación interna.
  Cada humano recibe exactamente la misma cantidad.
```

### VII.3 Velocidad

Los Ⓣ están diseñados para circular, no para acumularse:

```
  Génesis:  50 Ⓣ → gastar en servicios
  Proveedor: Ⓣ ganados → gastar en otros servicios
  Consumidor: paga por servicios → proveedor gana → gasta de nuevo
```

Taxoin no es una reserva de valor. Es un **medio de intercambio**
para una economía de servicios peer-to-peer.

### VII.4 Comisiones

No hay comisiones de transacción a nivel de protocolo. Los validadores
no reciben recompensas de bloque (no hay bloques en el sentido tradicional).

Los validadores pueden cobrar comisiones voluntarias por:
- Atestación de génesis
- Arbitraje de disputas
- Verificación de servicios

El mercado de comisiones es libre: los validadores compiten en precio
y confiabilidad.

---

## Parte VIII: Modelo de Seguridad

### VIII.1 Matriz de Amenazas

| Amenaza | Mitigación |
|--------|-----------|
| Ataque Sybil (humanos falsos) | Prueba de Humanidad + atestación 3/7 |
| Doble gasto | Detector de conflictos (Fase 2) + seguimiento de gasto |
| Servicio falso (toma dinero, no entrega) | Atestación mutua + resolución de disputas |
| Colusión de validadores (3 de 7 maliciosos) | Tolerancia a fallos bizantinos (f=2) |
| Manipulación del registro | Inmutabilidad de Git + firmas de validadores |
| Falsificación de saldo | Firmas ECDSA en todas las transacciones |
| Ataque de repetición | Seguimiento de nonce por dirección |
| Partición de red | Protocolo de chismorreo + vivacidad basada en tiempo de espera |

### VIII.2 Supuestos de Confianza

Taxoin no es sin confianza. Es **confianza minimizada:**

| Debes confiar en | No necesitas confiar en |
|---------------|-------------------|
| 5 de 7 validadores son honestos | Ningún validador individual |
| Tu clave privada es segura | La red sea "justa" |
| Los validadores verifican humanos correctamente | Mineros (no existen) |
| | Apostadores (no existen) |
| | Oráculo (la atestación es mutua) |

---

## Parte IX: Referencia CLI

La interfaz de usuario principal:

```bash
  # Identidad
  taxoin wallet new                  # Generar par de claves
  taxoin wallet address              # Mostrar tu dirección
  taxoin wallet show                 # Mostrar cartera completa

  # Génesis (una vez por humano)
  taxoin genesis request             # Solicitar verificación humana
  taxoin genesis status              # Verificar estado de génesis

  # Servicios
  taxoin service register            # Registrar un nuevo servicio
       --type sms
       --price 0.1
       --endpoint "https://..."
       --description "Pasarela SMS"
  taxoin service list                # Listar todos los servicios
       --type gpu
       --min-rating 4.0
  taxoin service show <address>      # Mostrar detalles del servicio
  taxoin service rate <address>      # Calificar un servicio

  # Transacciones
  taxoin tx send <provider>          # Pagar por un servicio
       --amount 0.1
       --ref <service_id>
       --desc "SMS a +79123456789"
  taxoin tx attest <tx_id>           # Firmar atestación mutua
  taxoin tx status <tx_id>           # Verificar estado de transacción

  # Disputas
  taxoin dispute open <tx_id>        # Abrir una disputa
  taxoin dispute list                # Listar disputas activas

  # Reputación
  taxoin reputation <address>        # Mostrar reputación
  taxoin reputation leaderboard      # Mejores proveedores

  # Red
  taxoin validator list              # Mostrar validadores
  taxoin status                      # Estado de la red
```

---

## Parte X: El Panorama General

### X.1 Lo que Taxoin Cambia

| Era | Mecanismo | Recurso Derrochado |
|-----|-----------|----------------|
| **Pre-2008** | Trueque / Dinero fiduciario | Confianza |
| **2008 (Bitcoin)** | Prueba de Trabajo (Proof of Work) | Electricidad |
| **2015 (Ethereum)** | Prueba de Participación (Proof of Stake) | Capital |
| **2026 (Taxoin)** | Prueba de Contribución (Proof of Contribution) | Nada |

### X.2 El Objetivo Final

Una economía de servicios descentralizada y autosostenible donde:

- **Cualquiera puede ganar** proporcionando un servicio que ya posee
- **Cualquiera puede pagar** con monedas que ganó contribuyendo
- **Nadie puede hacer trampa** porque ambas partes deben atestiguar
- **Nadie es excluido** porque el único requisito es ser humano
- **No se derrocha energía** porque el cómputo sirve a personas, no a hashes

### X.3 El Nombre

**Taxoin** proviene de *taxi* + *coin* (*moneda*).

Un taxista provee un servicio real y valioso — transporte.
El pasajero paga por ese servicio. Ambas partes atestiguan que
el viaje ocurrió. Sin minería. Sin participación. Sin especulación.

Solo **servicio, pago y prueba.**

---

## SIGNED NOT_FOR_COMPACTION.

Este documento es la especificación canónica del protocolo Taxoin.
Todas las implementaciones deben ajustarse a esta especificación.

**Versión:** 1.0  
**Fecha:** 2026-05-20  
**Estado:** Activo
