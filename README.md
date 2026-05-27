# Batch vs Realtime Lab

Educational lab for demonstrating:
- Batch processing
- Realtime systems
- Event streams
- Fraud detection
- Data pipelines

## Run

```bash
docker compose up
```

## Components

- generator -> creates fake payment events
- realtime -> processes events immediately
- batch -> generates 30-second windowed reports every 30 seconds

## View data

```bash
tail -f data/payments.csv
```


# Batch vs Realtime Lab

Educational Docker lab for teaching:

- Big Data
- Distributed systems
- Batch processing
- Realtime systems
- Event-driven architecture
- Fraud detection
- Data pipelines
- Event streams
- Scaling tradeoffs


# Overview

This lab simulates a simplified payment platform similar to:

- Swish
- Stripe
- Klarna
- PayPal

Students will work with:

- realtime fraud detection
- batch analytics
- event streams
- distributed consumers
- scaling problems
- data quality issues

The goal is to understand the architectural differences between:

- batch systems
- realtime systems
- queues
- streams
- analytics systems
- operational systems

# Architecture

```text
                +----------------+
                |   Generator    |
                | payment events |
                +--------+-------+
                         |
                         v
               payments.csv
                         |
         +---------------+---------------+
         |                               |
         v                               v
+----------------+          +----------------------+
| Realtime       |          | Batch Processing     |
| Fraud Detection|          | Analytics & Reports  |
+----------------+          +----------------------+
```


# Components

## Generator

Continuously generates fake payment events.

Example:

```json
{
  "timestamp": "2025-05-27T09:00:01",
  "user": "alice",
  "amount": 4200
}
```


## Realtime Service

Processes events immediately.

Detects:
- suspicious payments
- fraud patterns
- high transaction frequency

Examples:
- payment > 3000
- many payments within short time


## Batch Service

Processes historical data periodically.

Creates:
- analytics reports
- user statistics
- revenue summaries
- top spender reports

Runs every 30 seconds.


# Getting Started

## Requirements

- Docker
- Docker Compose


# Run the Lab

```bash
docker compose up
```


# Watch Events

```bash
tail -f data/payments.csv
```


# Stop the Lab

```bash
docker compose down
```


# Goals

Students should understand:

- why realtime systems are expensive
- why batch still exists
- why distributed systems are difficult
- eventual consistency
- event streams
- backpressure
- scaling tradeoffs
- data quality problems

---

# Exercise 1 — Fraud Team

## Goal

Detect suspicious payments in realtime.

## Tasks

Implement detection for:
- payments over 3000
- multiple payments within 10 seconds
- repeated payment amounts

## Bonus

Add:
- blacklisted users
- fraud score
- suspicious country detection

## Concepts

- realtime processing
- stateful systems
- event windows

## Vad hände i denna övningen

Generatorn skapade fake-betalningar varje sekund och skickade dem till payments.csv.
realtime.py läste filen kontinuerligt och analyserade varje ny rad direkt — det kallas realtidsbearbetning.

Tre fraud-detekteringar implementerades:

**1. Höga belopp (> 3000)**
Varje betalning över 3 000 kr flaggades direkt med `🚨 ALERT: High amount payment!`.
I verkligheten kan detta indikera kortbedrägeri eller ett komprometterat konto.

**2. Hög frekvens (3+ betalningar inom 10 sekunder)**
Systemet håller koll på hur många betalningar varje användare gör inom ett 10-sekunders fönster.
Om samma person betalade 3 eller fler gånger på kort tid flaggades det.
Detta är ett klassiskt mönster vid stulna kort — angriparen testar kortet snabbt med många små transaktioner.

**3. Upprepade belopp**
Om samma användare skickade exakt samma belopp tre gånger i rad flaggades det som misstänkt.
Detta kan tyda på ett automatiserat attack-skript som kör samma transaktion i en loop.

**Viktig skillnad mot batch:** Beslut fattades per millisekund, per event, utan att vänta.
Det är dyrt beräkningsmässigt men nödvändigt när man vill stoppa bedrägerier *innan* pengarna är borta.

---

# Exercise 2 — Data Quality Team

## Goal

Handle bad events safely.

## Tasks

Inject broken events:

```python
{
    "user": None,
    "amount": "INVALID"
}
```

Students must:
- validate events
- reject invalid data
- create error logs

## Concepts

- schema validation
- garbage in → garbage out
- defensive programming

## Vad hände i denna övningen

generator.py skickade medvetet trasiga events ungefär var 5:e betalning (20% chans).
Det simulerar verkligheten — i riktiga system är data alltid smutsig ibland, oavsett om det beror på buggar, nätverksfel eller dåliga klienter.

Tre typer av trasiga events injicerades:

**1. Null user** — användaren var tom/saknades.
Terminalen visade: `❌ REJECTED: Missing or null user`

**2. Invalid amount** — beloppet var textsträngen "INVALID" istället för ett tal.
Terminalen visade: `❌ REJECTED: Invalid amount (not a number): INVALID`

**3. Missing field** — raden hade fel antal kolumner (saknat fält).
Terminalen visade: `❌ REJECTED: Wrong number of fields`

**Vad realtime.py gjorde med dem:**
Istället för att krascha eller bearbeta skräpdata kastades ogiltiga events bort.
De skrevs till `data/errors.log` med tidsstämpel och anledning — det kallas defensive programming.

**Principen "garbage in → garbage out":**
Om man inte validerar data smyger sig felaktiga siffror in i rapporter och beslut.
En errors.log gör det möjligt att senare analysera hur många events som förkastades och varför.

---

# Exercise 3 — Batch Analytics Team

## Goal

Improve batch reporting.

## Tasks

Add:
- revenue per user
- average transaction
- top spender
- hourly transaction volume

## Bonus

Export reports to:
- JSON
- CSV

## Concepts

- batch processing
- OLAP systems
- analytics workloads

## Vad hände i denna övningen

batch.py vaknade var 30:e sekund och analyserade alla betalningar som skett i det fönstret.
Det är kärnan i batch-bearbetning — ingen realtid, ingen kontinuerlig övervakning.
Istället samlade man ihop data och bearbetade det i ett svep.

Fyra analytics-funktioner lades till:

**1. Revenue per user**
Total intäkt per användare i batch-fönstret, sorterad högst till lägst.
I verkligheten används detta för fakturering och kundanalys.

**2. Average transaction per user**
Snittet per användare avslöjar beteendemönster — gör en användare många små köp eller få stora?

**3. Top spender 🏆**
Vem spenderade mest i batch-fönstret?
Enkelt men kraftfullt för marknadsföring och VIP-program.

**4. Hourly transaction volume**
Hur många transaktioner och hur mycket pengar som rörde sig per timme.
Det här är OLAP-tänk — historisk analys istället för operationell.

**Export till JSON och CSV:**
Varje batch-körning sparade en rapport i `data/reports/`.
JSON används för att skicka vidare till andra system.
CSV används för att öppna i Excel eller ladda upp till ett datalager.

**Viktig skillnad mot Exercise 1:**
Realtidssystemet fattar beslut per millisekund men vet ingenting om historik.
Batch-systemet ser hela bilden men är alltid lite "gammalt".
I verkligheten behöver man oftast båda.

---

# Exercise 4 — Backpressure

## Goal

Simulate overloaded systems.

## Tasks

Increase event generation speed:

```python
time.sleep(0.01)
```

Observe:
- lagging consumers
- growing files
- delayed processing

## Discussion

What happens when:
- producers are faster than consumers?
- systems cannot keep up?

### Svar: Vad händer när producenter är snabbare än konsumenter?

Det observerades direkt i lag.log — kön låg konstant på ~84 obearbetade rader
och events var redan 3 sekunder gamla när de bearbetades.
Konsumenten hann aldrig ikapp producenten.

I ett riktigt system fylls bufferten tills minnet eller disken tar slut,
och till slut kraschar hela tjänsten eller börjar tappa data.

### Svar: Vad händer när system inte hinner med?

Tre saker hände samtidigt i labben:

1. **Data blev inaktuell** — en 3-sekunders gammal fraud-alert är värdelös i ett betalningssystem.
2. **Felprocenten ökade** — fraud-logiken triggade på normalt beteende eftersom den inte var designad för 100 events/sekund.
3. **Felaktiga beslut** — systemet såg mönster som inte existerade i verkligheten, t.ex. "bob made 221 payments in 10 seconds".

I ett riktigt betalningssystem kan det betyda att bedrägliga transaktioner godkänns
för att varningen kom för sent.

## Concepts

- backpressure
- buffering
- queues
- scaling

---

# Key Concepts
- batch vs realtime
- event-driven systems
- streams vs queues
- scaling
- partitioning
- replication
- eventual consistency
- OLTP vs OLAP
- backpressure
- distributed failures


# Discussion Questions

### Why not process everything realtime?
> **Gäller främst: Exercise 1 och Exercise 4**

Realtid är extremt dyrt. Varje event kräver omedelbar bearbetning, tillståndshantering i minnet
och snabba beslut — det kräver kraftfull hårdvara som körs konstant.
I Exercise 4 kollapsade realtidssystemet redan vid 100 events/sekund.
Batch (Exercise 3) körde bara var 30:e sekund och kunde göra tung analys när belastningen var låg.
De flesta beslut behöver inte fattas på millisekunder — en månadsrapport behöver inte vara realtid.

---

### Why does Big Data require distributed systems?
> **Gäller främst: Exercise 4**

En enda maskin har begränsat minne, CPU och disk.
I Exercise 4 såg vi hur snabbt en fil och en kö växer vid bara 100 events/sekund.
I verkligheten genererar ett betalningssystem som Swish miljontals events per sekund.
Det går inte att bearbeta på en maskin — data måste delas upp och bearbetas
parallellt på många maskiner (partitionering och replikering).

---

### When is eventual consistency acceptable?
> **Gäller främst: Exercise 1 och Exercise 3**

Batch-rapporten i Exercise 3 visade data som var upp till 30 sekunder gammal — det var acceptabelt
för analytics och statistik. Ingen tar skada av att en rapport är 30 sekunder sen.
Men fraud-detektionen i Exercise 1 måste vara konsistent direkt, annars godkänns
bedrägliga betalningar innan systemet reagerar.
Tumregel: om en fördröjning kostar pengar eller skadar användare krävs stark konsistens.
Om det handlar om statistik och rapporter är eventual consistency ofta tillräckligt.

---

### Why are queues useful?
> **Gäller främst: Exercise 4**

I labben hade vi ingen kö — bara en CSV-fil som växte okontrollerat.
En riktig kö (som Kafka) låter konsumenten styra sin egen takt, lagrar events säkert
tills de är bearbetade, och kan fördela events till flera konsumenter parallellt.
Det löser exakt det backpressure-problem vi observerade i Exercise 4 —
om kön är full blockas producenten istället för att data förloras.

---

### Why do companies separate OLTP and OLAP?
> **Gäller främst: Exercise 1 och Exercise 3**

realtime.py (OLTP) fattade snabba beslut per event — det kräver låg latens och enkla operationer.
batch.py (OLAP) räknade summor, snitt och top spenders över hela dataset —
det kräver komplexa beräkningar men tål fördröjning.
Om man körde batch-analysen direkt i realtidssystemet skulle det sakta ner fraud-detektionen.
Därför håller företag dem separata — två system optimerade för varsitt syfte.

---

### Why is observability critical?
> **Gäller främst: Exercise 2 och Exercise 4**

Utan errors.log (Exercise 2) hade vi inte vetat att 20% av events var ogiltiga.
Utan lag.log (Exercise 4) hade vi inte vetat att systemet halkade 3 sekunder efter.
Observability (loggar, metrics, tracing) är skillnaden mellan att veta vad som händer och att gissa.
I ett produktionssystem kan ett osynligt problem kosta miljoner innan det upptäcks.
Loggar och metrics gör det möjligt att se exakt när ett problem startade och hur allvarligt det är.

---

### Why is scaling difficult?
> **Gäller främst: Exercise 4**

I Exercise 4 såg vi att om man bara snabbade upp generatorn så kollapsade konsumenten.
Man kan inte bara "lägga till mer hårdvara" — man måste också designa om systemet med:
- **Partitionering** — dela data mellan instanser
- **Replikering** — kopior för redundans och feltolerans
- **Koordination** — vem bearbetar vad, utan att samma event bearbetas två gånger

Varje del av systemet skalas på olika sätt, och de måste synkroniseras med varandra.
Det är den tekniska och arkitekturella utmaningen med distribuerade system.

---

# Suggested Extensions

Advanced students can add:

- Kafka — ersätter CSV-filen som kommunikationskanal, ger skalbarhet och inbyggt backpressure
- Redis — lagrar tillstånd (t.ex. recent_payments) så att det överlever omstarter
- PostgreSQL — permanent lagring av batch-rapporter, möjliggör SQL-frågor mot historiken
- WebSockets — visar fraud-alerts live i en webbläsare istället för i terminalen
- Dashboards — visualiserar metrics och alerts i realtid
- Kubernetes — containerorkestrering, automatisk omstart och horisontell skalning
- Metrics collection — mäter events/sekund, latens och felfrekvens (t.ex. Prometheus)
- Distributed tracing — spårar ett event genom hela systemet för att hitta flaskhalsar (t.ex. Jaeger)


# Educational Goal
The focus is understanding:
- architecture
- tradeoffs
- scaling challenges
