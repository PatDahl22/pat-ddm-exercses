# Föreläsningsövningar – API

## Syfte

Syftet med övningarna är att förstå hur klienter och API:er kommunicerar, hur API:er skyddar bakomliggande system och hur statuskoder används för att beskriva resultatet av ett anrop.

---

# Förmiddag – Konsumera ett API

## Scenario

Ni har precis anslutit till NovaStores backend. Ett API finns redan utvecklat och er uppgift är att förstå hur klienten använder API:et för att hämta produktinformation. Under förmiddagen fokuserar ni på att läsa data, förstå JSON-svar och se hur små förändringar i API:et påverkar klienten.

## Uppgift 1

Starta lösningen genom att köra:

```bash
docker compose up --build
```

## Uppgift 2

Öppna API:et i webbläsaren på:

```text
http://localhost:5001/products
```

Undersök vilken information som returneras och diskutera om svaret är HTML eller JSON.

## Uppgift 3

Kör klientapplikationen och skriv ut JSON-svaret genom att köra:

```bash
docker compose run --rm client
```

## Uppgift 4

Skriv ut statuskoden från svaret och fundera över vad klienten kan lära sig av den.

## Uppgift 5

Extrahera `id`, `name` och `price` ur JSON-svaret.

## Uppgift 6

Lägg till fältet `category` i API-svaret och verifiera att klienten fortfarande fungerar.

## Uppgift 7

Lägg till fler produkter och observera hur klienten påverkas när mängden data växer.

## Extra Uppgift 8

Returnera fler produkter i listan.

## Extra Uppgift 9

Lägg till `stock` i JSON-svaret.

## Extra Uppgift 10

Lägg till endpointen `/health` som returnerar att API:et är igång.

---

# Eftermiddag – Bygg ett robust API

## Scenario

NovaStore växer. Fler klienter börjar använda API:et och det räcker inte längre att bara returnera data. API:et måste kunna hantera fel, validera indata och ge tydlig feedback när något går fel.

## Uppgift 1

Implementera:

```http
GET /products/{id}
```

Klienter ska kunna hämta en specifik produkt utan att läsa hela produktlistan.

## Uppgift 2

Implementera `404 Not Found`.

Om en produkt inte finns, exempelvis:

```http
GET /products/999
```

ska API:et returnera ett tydligt felmeddelande.

## Uppgift 3

Implementera:

```http
POST /products
```

så att nya produkter kan skickas till API:et via JSON.

## Uppgift 4

Implementera `400 Bad Request`.

API:et ska stoppa ogiltig data innan den når databasen.

## Uppgift 5

Implementera:

```http
GET /crash
```

som simulerar ett serverfel och returnerar `500 Internal Server Error`.

## Extra Uppgift 6

Verifiera att:

```http
GET /products
```

visar produkter som skapats via `POST`.

## Extra Uppgift 7

Implementera:

```http
PUT /products/{id}
```

för att uppdatera produkter.

## Extra Uppgift 8

Implementera:

```http
DELETE /products/{id}
```

## Extra Uppgift 9

Returnera `201 Created` när en produkt skapas.

## Extra Uppgift 10

Returnera `204 No Content` när en produkt tas bort.

---

# Exempel på 400 Bad Request

Följande requests ska inte accepteras av API:et:

- `name` saknas
- `price` saknas
- `price` är negativt

Fundera över varför API:et bör stoppa denna data innan den lagras.

---

# Avslutande reflektion

- Vilket fel är användarens fel?
- Vilket fel är utvecklarens fel?
