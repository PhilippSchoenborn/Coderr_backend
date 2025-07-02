# API Feedback Tests

Dieses Verzeichnis enthält Test-Dateien um alle API-Feedback-Fixes zu validieren.

## 📋 Test-Dateien

### 1. `test_api_quick.py` - Schnelltests ⚡
**Verwendung**: Schnelle HTTP-Tests ohne Django-Setup
```bash
python test_api_quick.py
```

**Was wird getestet**:
- ✅ API-Erreichbarkeit
- ✅ Invalid `max_delivery_time` → 400 Bad Request
- ✅ Gültige `max_delivery_time` → 200 OK
- ✅ Suche mit nicht-existierendem Begriff → Leere Ergebnisse
- ✅ `min_price` Filter-Logik

**Voraussetzungen**: 
- Django-Server muss laufen (`python manage.py runserver`)

### 2. `test_api_feedback_comprehensive.py` - Umfassende Tests 🔬
**Verwendung**: Vollständige Django-Tests mit Datenbankzugriff
```bash
python test_api_feedback_comprehensive.py
```

**Was wird getestet**:
- ✅ Invalid/Valid `max_delivery_time` Parameter
- ✅ Kunden-Zugriff auf einzelne Angebote
- ✅ Such-Funktion (leer und mit Ergebnissen)
- ✅ `min_price` Filter mit Validierung
- ✅ Bestellungs-Autorisierung (Business vs Customer)
- ✅ PATCH-Operationen und Validierung

**Voraussetzungen**:
- Vollständige Django-Umgebung
- Testdaten werden automatisch erstellt

## 🚀 Tests ausführen

### Schritt 1: Django-Server starten
```bash
cd "c:\Users\Phil\Desktop\DeveloperAkademie\BACKEND\modul_8\marketplace_project_restored"
python manage.py runserver 8000
```

### Schritt 2: Tests in neuem Terminal ausführen

**Schnelltests** (empfohlen für erste Validierung):
```bash
python test_api_quick.py
```

**Umfassende Tests** (für vollständige Validierung):
```bash
python test_api_feedback_comprehensive.py
```

## 📊 Erwartete Ergebnisse

### ✅ Erfolgreiche Tests zeigen:
- `Status 400` für invalid `max_delivery_time=invalid`
- `Status 200` für gültige `max_delivery_time=7`
- `Count 0` für Suche mit nicht-existierendem Begriff
- `Status 200` mit gefilterten Ergebnissen für `min_price=75`
- `Status 403` für Business-User Bestellversuche
- `Status 200/201` für Customer-Aktionen

### ❌ Häufige Probleme:
- **Connection Error**: Django-Server nicht gestartet
- **404 Errors**: URL-Konfiguration prüfen
- **500 Errors**: Server-Logs überprüfen
- **Keine Testdaten**: Datenbank mit Angeboten befüllen

## 🔧 Debugging

### Server-Logs prüfen:
```bash
# Im Server-Terminal die Ausgabe beobachten
python manage.py runserver 8000
# Logs zeigen HTTP-Requests und Fehler
```

### Manuelle API-Tests:
```bash
# PowerShell/CMD
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/offers/?max_delivery_time=invalid" -Method GET

# Oder im Browser:
http://127.0.0.1:8000/api/offers/?max_delivery_time=invalid
```

### Django-Shell für Datenbankprüfung:
```bash
python manage.py shell
# In Shell:
from offers_app.models import Offer
print(f"Angebote in DB: {Offer.objects.count()}")
```

## 📈 Test-Abdeckung

Die Tests decken alle im Feedback erwähnten Problembereiche ab:

1. **❌ → ✅ min_price filter** - Ausschluss von Angeboten unter Minimum
2. **❌ → ✅ delivery_time filter** - Ausschluss von Angeboten über Maximum  
3. **❌ → ✅ Search no results** - Leere Ergebnisse für nicht-existierende Begriffe
4. **❌ → ✅ Single offer permissions** - Customer-Token-Zugriff
5. **❌ → ✅ Invalid delivery_time** - 400 Bad Request für ungültige Werte
6. **❌ → ✅ Patch offer_type** - Erforderliches Feld für PATCH
7. **❌ → ✅ Order authorization** - 403 für unauthorized, nicht 400

## 🎯 Verwendung nach Deployment

Diese Test-Dateien können auch für Produktions-Validierung verwendet werden:

```bash
# Test-URL ändern
python test_api_quick.py  # Ändere base_url in der Datei
```

Oder mit Umgebungsvariable:
```bash
export API_BASE_URL="https://your-production-api.com"
python test_api_quick.py
```
