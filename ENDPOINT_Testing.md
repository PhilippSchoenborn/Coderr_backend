# API Endpoint Testing - REST Client Tests

Diese Datei enthält umfassende Tests für alle API-Endpunkte der Marketplace-Anwendung.

## Voraussetzungen

1. Django-Server läuft auf `http://127.0.0.1:8000`
2. Testdaten sind in der Datenbank vorhanden
3. REST Client Extension ist in VS Code installiert

## Authentifizierung

Zuerst müssen Sie sich authentifizieren, um einen Token zu erhalten:

### Login (Token abrufen)

```http
POST http://127.0.0.1:8000/api/login/
Content-Type: application/json

{
    "username": "testuser",
    "password": "testpass123"
}
```

**Erwartetes Ergebnis:** Status 200, Response enthält `token`

### Alternative Login-Benutzer

```http
POST http://127.0.0.1:8000/api/login/
Content-Type: application/json

{
    "username": "designer123",
    "password": "test123"
}
```

### Falscher Login (Fehlertest)

```http
POST http://127.0.0.1:8000/api/login/
Content-Type: application/json

{
    "username": "falschuser",
    "password": "falschpasswort"
}
```

**Erwartetes Ergebnis:** Status 400, Fehler-Message

---

## Angebote (Offers) - Authentifiziert

**Hinweis:** Für alle authentifizierten Requests verwenden Sie:
```
Authorization: Token IHRE_TOKEN_HIER
```

### 1. Alle Angebote abrufen (Authentifiziert)

```http
GET http://127.0.0.1:8000/api/offer/
Authorization: Token IHRE_TOKEN_HIER
```

**Erwartetes Ergebnis:** Status 200, Liste aller Angebote mit Pagination

### 2. Angebote ohne Authentifizierung (Fehlertest)

```http
GET http://127.0.0.1:8000/api/offer/
```

**Erwartetes Ergebnis:** Status 200 (da GET erlaubt ist für diesen Endpoint)

### 3. Angebot erstellen ohne Authentifizierung (Fehlertest)

```http
POST http://127.0.0.1:8000/api/offer/
Content-Type: application/json

{
    "title": "Test Angebot"
}
```

**Erwartetes Ergebnis:** Status 401 Unauthorized

---

## Öffentliche Angebote (Public Offers)

### 1. Alle öffentlichen Angebote

```http
GET http://127.0.0.1:8000/api/public-offer/
```

**Erwartetes Ergebnis:** Status 200, Liste aller Angebote

### 2. Öffentliche Angebote mit Pagination

```http
GET http://127.0.0.1:8000/api/public-offer/?page_size=2
```

**Erwartetes Ergebnis:** Status 200, maximal 2 Angebote pro Seite

### 3. Pagination - Nächste Seite

```http
GET http://127.0.0.1:8000/api/public-offer/?page_size=2&page=2
```

---

## Filter-Tests

### 1. Min Price Filter

#### Günstige Angebote (>= 100€)
```http
GET http://127.0.0.1:8000/api/public-offer/?min_price=100
```

#### Teure Angebote (>= 1000€)
```http
GET http://127.0.0.1:8000/api/public-offer/?min_price=1000
```

#### Sehr teure Angebote (>= 50000€) - sollte wenige/keine Ergebnisse geben
```http
GET http://127.0.0.1:8000/api/public-offer/?min_price=50000
```

#### Ungültiger Min Price Filter
```http
GET http://127.0.0.1:8000/api/public-offer/?min_price=ungueltig
```

**Erwartetes Ergebnis:** Filter wird ignoriert, alle Angebote gezeigt

#### Negativer Min Price Filter
```http
GET http://127.0.0.1:8000/api/public-offer/?min_price=-100
```

### 2. Max Delivery Time Filter

#### Schnelle Lieferung (<= 7 Tage)
```http
GET http://127.0.0.1:8000/api/public-offer/?max_delivery_time=7
```

#### Standard Lieferung (<= 14 Tage)
```http
GET http://127.0.0.1:8000/api/public-offer/?max_delivery_time=14
```

#### Lange Lieferung (<= 30 Tage)
```http
GET http://127.0.0.1:8000/api/public-offer/?max_delivery_time=30
```

#### Sehr kurze Lieferung (<= 1 Tag)
```http
GET http://127.0.0.1:8000/api/public-offer/?max_delivery_time=1
```

#### Ungültiger Delivery Time Filter
```http
GET http://127.0.0.1:8000/api/public-offer/?max_delivery_time=abc
```

### 3. Search Filter

#### Suche nach "Design"
```http
GET http://127.0.0.1:8000/api/public-offer/?search=design
```

#### Suche nach "Web"
```http
GET http://127.0.0.1:8000/api/public-offer/?search=web
```

#### Suche nach "SEO"
```http
GET http://127.0.0.1:8000/api/public-offer/?search=seo
```

#### Suche nach nicht existierendem Begriff
```http
GET http://127.0.0.1:8000/api/public-offer/?search=nichtexistierend
```

#### Leere Suche
```http
GET http://127.0.0.1:8000/api/public-offer/?search=
```

### 4. Creator ID Filter

#### Filter nach Designer (User ID 9)
```http
GET http://127.0.0.1:8000/api/public-offer/?creator_id=9
```

#### Filter nach Developer (User ID 10)
```http
GET http://127.0.0.1:8000/api/public-offer/?creator_id=10
```

#### Filter nach nicht existierender User ID
```http
GET http://127.0.0.1:8000/api/public-offer/?creator_id=99999
```

#### Ungültige Creator ID
```http
GET http://127.0.0.1:8000/api/public-offer/?creator_id=ungueltig
```

### 5. Kombinierte Filter

#### Teure Angebote mit schneller Lieferung
```http
GET http://127.0.0.1:8000/api/public-offer/?min_price=500&max_delivery_time=7
```

#### Design-Angebote unter 300€
```http
GET http://127.0.0.1:8000/api/public-offer/?search=design&min_price=1&max_delivery_time=100
```

#### Alle Filter kombiniert
```http
GET http://127.0.0.1:8000/api/public-offer/?min_price=100&max_delivery_time=21&search=web&creator_id=10
```

#### Widersprüchliche Filter (sollte keine Ergebnisse geben)
```http
GET http://127.0.0.1:8000/api/public-offer/?min_price=100000&max_delivery_time=1
```

---

## Sortierung (Ordering)

### 1. Sortierung nach Erstellungsdatum (Standard)
```http
GET http://127.0.0.1:8000/api/public-offer/?ordering=created_at
```

### 2. Sortierung nach Update-Datum
```http
GET http://127.0.0.1:8000/api/public-offer/?ordering=updated_at
```

### 3. Sortierung nach Mindestpreis (aufsteigend)
```http
GET http://127.0.0.1:8000/api/public-offer/?ordering=min_price
```

### 4. Sortierung nach Mindestpreis mit Filter
```http
GET http://127.0.0.1:8000/api/public-offer/?ordering=min_price&min_price=100
```

### 5. Ungültige Sortierung
```http
GET http://127.0.0.1:8000/api/public-offer/?ordering=ungueltigesfeld
```

---

## Profile Tests

### 1. Alle Profile ohne Authentifizierung (Fehlertest)
```http
GET http://127.0.0.1:8000/api/profile/
```

**Erwartetes Ergebnis:** Status 401 Unauthorized

### 2. Alle Profile mit Authentifizierung
```http
GET http://127.0.0.1:8000/api/profile/
Authorization: Token IHRE_TOKEN_HIER
```

### 3. Business Profile
```http
GET http://127.0.0.1:8000/api/profile/business/
Authorization: Token IHRE_TOKEN_HIER
```

### 4. Customer Profile
```http
GET http://127.0.0.1:8000/api/profile/customer/
Authorization: Token IHRE_TOKEN_HIER
```

### 5. Spezifisches Profil abrufen
```http
GET http://127.0.0.1:8000/api/profile/9/
Authorization: Token IHRE_TOKEN_HIER
```

### 6. Nicht existierendes Profil
```http
GET http://127.0.0.1:8000/api/profile/99999/
Authorization: Token IHRE_TOKEN_HIER
```

**Erwartetes Ergebnis:** Status 404 Not Found

---

## Bestellungen (Orders) Tests

### 1. Alle Bestellungen ohne Authentifizierung
```http
GET http://127.0.0.1:8000/api/order/
```

**Erwartetes Ergebnis:** Status 401 Unauthorized

### 2. Alle Bestellungen mit Authentifizierung
```http
GET http://127.0.0.1:8000/api/order/
Authorization: Token IHRE_TOKEN_HIER
```

### 3. Bestellung erstellen (Beispiel)
```http
POST http://127.0.0.1:8000/api/order/
Authorization: Token IHRE_TOKEN_HIER
Content-Type: application/json

{
    "offer_detail_id": 1,
    "message": "Testbestellung"
}
```

---

## Bewertungen (Reviews) Tests

### 1. Alle Bewertungen ohne Authentifizierung
```http
GET http://127.0.0.1:8000/api/review/
```

**Erwartetes Ergebnis:** Status 401 Unauthorized

### 2. Alle Bewertungen mit Authentifizierung
```http
GET http://127.0.0.1:8000/api/review/
Authorization: Token IHRE_TOKEN_HIER
```

---

## Edge Cases und Stress Tests

### 1. Sehr große page_size
```http
GET http://127.0.0.1:8000/api/public-offer/?page_size=10000
```

### 2. Negative page_size
```http
GET http://127.0.0.1:8000/api/public-offer/?page_size=-1
```

### 3. page_size = 0
```http
GET http://127.0.0.1:8000/api/public-offer/?page_size=0
```

### 4. Sehr große Seitenzahl
```http
GET http://127.0.0.1:8000/api/public-offer/?page=999999
```

### 5. Multiple gleiche Parameter
```http
GET http://127.0.0.1:8000/api/public-offer/?min_price=100&min_price=200&min_price=300
```

### 6. SQL Injection Versuche (sollten sicher abgefangen werden)
```http
GET http://127.0.0.1:8000/api/public-offer/?search='; DROP TABLE offers; --
```

### 7. XSS Versuche
```http
GET http://127.0.0.1:8000/api/public-offer/?search=<script>alert('xss')</script>
```

### 8. Sehr langer Suchbegriff
```http
GET http://127.0.0.1:8000/api/public-offer/?search=dasisteinextremlangersuchbegriffderviellängeriststalseinüblichersuchbegriffundsolltetestenobdieapimitlangeneingabenumgehenkann
```

---

## Nicht existierende Endpunkte (404 Tests)

### 1. Falscher Endpunkt
```http
GET http://127.0.0.1:8000/api/nichtexistierend/
```

### 2. Falsche HTTP-Methode
```http
DELETE http://127.0.0.1:8000/api/public-offer/
```

### 3. Falscher URL-Pfad
```http
GET http://127.0.0.1:8000/api/offer/nichtexistierend/
```

---

## Performance Tests

### 1. Viele gleichzeitige Filter
```http
GET http://127.0.0.1:8000/api/public-offer/?min_price=1&max_delivery_time=1000&search=&creator_id=&ordering=min_price&page_size=1&page=1
```

### 2. Pagination durch alle Seiten
```http
GET http://127.0.0.1:8000/api/public-offer/?page_size=1&page=1
```

```http
GET http://127.0.0.1:8000/api/public-offer/?page_size=1&page=2
```

```http
GET http://127.0.0.1:8000/api/public-offer/?page_size=1&page=3
```

---

## Angebot erstellen (Authentifiziert)

### 1. Gültiges Angebot erstellen
```http
POST http://127.0.0.1:8000/api/offer/
Authorization: Token IHRE_TOKEN_HIER
Content-Type: application/json

{
    "title": "REST Client Test Angebot",
    "description": "Test-Angebot erstellt über REST Client",
    "details": [
        {
            "title": "Basic Paket",
            "price": 299.99,
            "delivery_time_in_days": 7,
            "revisions": 2,
            "offer_type": "basic",
            "features": ["Feature 1", "Feature 2"]
        },
        {
            "title": "Standard Paket",
            "price": 499.99,
            "delivery_time_in_days": 5,
            "revisions": 3,
            "offer_type": "standard",
            "features": ["Feature 1", "Feature 2", "Feature 3"]
        },
        {
            "title": "Premium Paket",
            "price": 799.99,
            "delivery_time_in_days": 3,
            "revisions": 5,
            "offer_type": "premium",
            "features": ["All Features", "Premium Support"]
        }
    ]
}
```

### 2. Angebot mit fehlendem Titel (Fehlertest)
```http
POST http://127.0.0.1:8000/api/offer/
Authorization: Token IHRE_TOKEN_HIER
Content-Type: application/json

{
    "description": "Angebot ohne Titel",
    "details": [
        {
            "title": "Basic",
            "price": 100,
            "delivery_time_in_days": 7,
            "revisions": 2,
            "offer_type": "basic",
            "features": ["Feature"]
        },
        {
            "title": "Standard",
            "price": 200,
            "delivery_time_in_days": 5,
            "revisions": 3,
            "offer_type": "standard",
            "features": ["Feature"]
        },
        {
            "title": "Premium",
            "price": 300,
            "delivery_time_in_days": 3,
            "revisions": 5,
            "offer_type": "premium",
            "features": ["Feature"]
        }
    ]
}
```

### 3. Angebot mit nur 2 Details (Fehlertest - braucht genau 3)
```http
POST http://127.0.0.1:8000/api/offer/
Authorization: Token IHRE_TOKEN_HIER
Content-Type: application/json

{
    "title": "Unvollständiges Angebot",
    "description": "Nur 2 Details statt 3",
    "details": [
        {
            "title": "Basic",
            "price": 100,
            "delivery_time_in_days": 7,
            "revisions": 2,
            "offer_type": "basic",
            "features": ["Feature"]
        },
        {
            "title": "Premium",
            "price": 300,
            "delivery_time_in_days": 3,
            "revisions": 5,
            "offer_type": "premium",
            "features": ["Feature"]
        }
    ]
}
```

### 4. Angebot mit fehlenden Detail-Feldern
```http
POST http://127.0.0.1:8000/api/offer/
Authorization: Token IHRE_TOKEN_HIER
Content-Type: application/json

{
    "title": "Fehlerhaftes Angebot",
    "description": "Details haben fehlende Felder",
    "details": [
        {
            "title": "Basic",
            "price": 100
            // revisions, delivery_time_in_days, offer_type, features fehlen
        },
        {
            "title": "Standard",
            "price": 200,
            "delivery_time_in_days": 5,
            "revisions": 3,
            "offer_type": "standard",
            "features": ["Feature"]
        },
        {
            "title": "Premium",
            "price": 300,
            "delivery_time_in_days": 3,
            "revisions": 5,
            "offer_type": "premium",
            "features": ["Feature"]
        }
    ]
}
```

---

## Logout Test

### Logout
```http
POST http://127.0.0.1:8000/api/logout/
Authorization: Token IHRE_TOKEN_HIER
```

### Nach Logout - Token sollte ungültig sein
```http
GET http://127.0.0.1:8000/api/offer/
Authorization: Token IHRE_UNGÜLTIGER_TOKEN
```

**Erwartetes Ergebnis:** Status 401 Unauthorized

---

## Registrierung Tests

### 1. Neue Registrierung
```http
POST http://127.0.0.1:8000/api/registration/
Content-Type: application/json

{
    "username": "neueruser",
    "email": "neuer@test.com",
    "password": "sicherespasswort123",
    "repeated_password": "sicherespasswort123",
    "type": "customer"
}
```

### 2. Registrierung mit existierendem Benutzernamen
```http
POST http://127.0.0.1:8000/api/registration/
Content-Type: application/json

{
    "username": "testuser",
    "email": "andere@test.com",
    "password": "passwort123",
    "repeated_password": "passwort123",
    "type": "business"
}
```

### 3. Registrierung mit nicht übereinstimmenden Passwörtern
```http
POST http://127.0.0.1:8000/api/registration/
Content-Type: application/json

{
    "username": "testuser2",
    "email": "test2@test.com",
    "password": "passwort123",
    "repeated_password": "anderespasswort",
    "type": "customer"
}
```

---

## Dashboard Test

### Dashboard (Authentifiziert)
```http
GET http://127.0.0.1:8000/api/dashboard/
Authorization: Token IHRE_TOKEN_HIER
```

---

## Sonstige Endpunkte

### Base Info (Öffentlich)
```http
GET http://127.0.0.1:8000/api/base-info/
```

### Hello World (Öffentlich)
```http
GET http://127.0.0.1:8000/api/hello/
```

### Public Profiles (Öffentlich)
```http
GET http://127.0.0.1:8000/api/public-profile/
```

### My Offers (Authentifiziert)
```http
GET http://127.0.0.1:8000/api/my-offer/
Authorization: Token IHRE_TOKEN_HIER
```

### Offer Details
```http
GET http://127.0.0.1:8000/api/offerdetail/1/
```

---

## Test-Checkliste

- [ ] Alle Authentifizierungs-Tests bestanden
- [ ] Alle Filter funktionieren korrekt
- [ ] Pagination funktioniert
- [ ] Sortierung funktioniert
- [ ] Edge Cases werden korrekt behandelt
- [ ] Fehler-Status-Codes sind korrekt (401, 403, 404, 400)
- [ ] Ungültige Eingaben werden abgefangen
- [ ] SQL-Injection-Schutz funktioniert
- [ ] Performance ist akzeptabel
- [ ] Angebotserstellung funktioniert
- [ ] Logout funktioniert korrekt

---

## Erwartete Testdaten in der Datenbank

Nach dem Ausführen der Testdaten-Scripts sollten folgende Daten vorhanden sein:

**Benutzer:**
- testuser (ID: 1) - business
- designer123 (ID: 9) - business  
- developer456 (ID: 10) - business
- customer789 (ID: 11) - customer
- freelancer999 (ID: 12) - business

**Angebote:**
- Test Web Development (min_price: 300.0, min_delivery_time: 7)
- Mobile App Development (min_price: 800.0, min_delivery_time: 15)
- Logo Design Paket (min_price: 150.0, min_delivery_time: 2)
- E-Commerce Website (min_price: 800.0, min_delivery_time: 10)
- SEO Optimierung (min_price: 200.0, min_delivery_time: 7)
- Extrem Günstiges Design (min_price: 1.0, min_delivery_time: 1)

Diese Testdaten decken verschiedene Preisklassen und Lieferzeiten ab, um alle Filter-Szenarien zu testen.
