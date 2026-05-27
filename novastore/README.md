# NovaStore – Del 1 & 2: Setup

## Steg 1 – Starta databaserna

```bash
cd novastore
docker compose up -d
docker ps        # båda containers ska vara "Up"
```

## Steg 2 – Kontrollera att PostgreSQL är igång

```bash
docker exec -it sql-demo psql -U student -d shop
```

Inuti psql:
```sql
SELECT NOW();     -- ska returnera aktuell tid
\dt               -- lista alla tabeller (laddas från schema.sql automatiskt)
SELECT * FROM customers;
\q                -- avsluta
```

## Steg 3 – Kontrollera att MongoDB är igång

```bash
docker exec -it nosql-demo mongosh
```

Inuti mongosh:
```js
show dbs
use shop
db.orders.find()
exit
```

## Steg 4 – Kör Python-skripten

Installera paket (en gång):
```bash
pip install psycopg2-binary pymongo
```

Kör PostgreSQL CRUD:
```bash
python python/postgres_crud.py
```

Kör MongoDB CRUD:
```bash
python python/mongo_crud.py
```

## Filstruktur

```
novastore/
├── docker-compose.yml       # PostgreSQL + MongoDB
├── sql/
│   └── schema.sql           # Tabeller + exempeldata (körs automatiskt vid start)
└── python/
    ├── postgres_crud.py     # CRUD mot PostgreSQL
    └── mongo_crud.py        # CRUD mot MongoDB
```

## Stoppa databaserna

```bash
docker compose down          # stoppar containers
docker compose down -v       # stoppar + tar bort all data (börja om från scratch)
```
