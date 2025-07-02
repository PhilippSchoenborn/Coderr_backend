#!/usr/bin/env python
"""
Umfassende Test-Datei für alle API-Feedback-Fixes
Testet alle kritischen Punkte die im Feedback erwähnt wurden
"""
import os
import sys
import django
import json
from datetime import datetime

# Django Setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from profiles_app.models import Profile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


class APIFeedbackTester:
    """Tester für alle API-Feedback-Fixes"""
    
    def __init__(self):
        self.client = APIClient()
        self.test_results = []
        self.setup_test_data()
    
    def setup_test_data(self):
        """Test-Daten vorbereiten"""
        print("🔧 Test-Daten werden vorbereitet...")
        
        # Test-User erstellen falls sie nicht existieren
        try:
            self.business_user = User.objects.get(username='test_business')
        except User.DoesNotExist:
            self.business_user = User.objects.create_user(
                username='test_business',
                email='business@test.com',
                password='testpass123'
            )
            Profile.objects.create(
                user=self.business_user,
                type='business'
            )
        
        try:
            self.customer_user = User.objects.get(username='test_customer')
        except User.DoesNotExist:
            self.customer_user = User.objects.create_user(
                username='test_customer',
                email='customer@test.com',
                password='testpass123'
            )
            Profile.objects.create(
                user=self.customer_user,
                type='customer'
            )
        
        # Tokens erstellen
        self.business_token, _ = Token.objects.get_or_create(user=self.business_user)
        self.customer_token, _ = Token.objects.get_or_create(user=self.customer_user)
        
        print(f"✅ Test-User erstellt: Business({self.business_user.id}), Customer({self.customer_user.id})")
    
    def log_test(self, test_name, expected, actual, passed, details=""):
        """Test-Ergebnis protokollieren"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        result = {
            'test': test_name,
            'expected': expected,
            'actual': actual,
            'status': status,
            'details': details,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print(f"   Erwartet: {expected} | Erhalten: {actual}")
        print()
    
    def test_invalid_delivery_time(self):
        """Test 1: Invalid max_delivery_time sollte 400 Bad Request zurückgeben"""
        print("🧪 Test 1: Invalid delivery_time Parameter")
        
        # Test mit String statt Integer
        response = self.client.get('/api/offers/?max_delivery_time=invalid')
        
        expected_status = 400
        actual_status = response.status_code
        passed = actual_status == expected_status
        
        details = f"Response: {response.data if hasattr(response, 'data') else 'No data'}"
        
        self.log_test(
            "Invalid delivery_time Parameter",
            f"Status {expected_status}",
            f"Status {actual_status}",
            passed,
            details
        )
        
        # Test mit anderem ungültigen Wert
        response2 = self.client.get('/api/offers/?max_delivery_time=test123')
        passed2 = response2.status_code == 400
        
        self.log_test(
            "Invalid delivery_time 'test123'",
            "Status 400",
            f"Status {response2.status_code}",
            passed2
        )
        
        return passed and passed2
    
    def test_valid_delivery_time(self):
        """Test 2: Gültige delivery_time sollte 200 OK zurückgeben"""
        print("🧪 Test 2: Gültige delivery_time Parameter")
        
        response = self.client.get('/api/offers/?max_delivery_time=7')
        
        expected_status = 200
        actual_status = response.status_code
        passed = actual_status == expected_status
        
        count = response.data.get('count', 0) if hasattr(response, 'data') else 0
        details = f"Gefilterte Angebote: {count}"
        
        self.log_test(
            "Gültige delivery_time=7",
            f"Status {expected_status}",
            f"Status {actual_status}",
            passed,
            details
        )
        
        return passed
    
    def test_customer_offer_access(self):
        """Test 3: Kunden sollten einzelne Angebote abrufen können"""
        print("🧪 Test 3: Kunden-Zugriff auf einzelne Angebote")
        
        # Erst alle Angebote abrufen um eine ID zu bekommen
        offers_response = self.client.get('/api/offers/')
        if offers_response.status_code != 200 or not offers_response.data.get('results'):
            self.log_test(
                "Kunde Angebot-Zugriff",
                "Angebot gefunden",
                "Keine Angebote verfügbar",
                False,
                "Keine Test-Angebote vorhanden"
            )
            return False
        
        offer_id = offers_response.data['results'][0]['id']
        
        # Mit Customer-Token einzelnes Angebot abrufen
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.get(f'/api/offers/{offer_id}/')
        
        expected_status = 200
        actual_status = response.status_code
        passed = actual_status == expected_status
        
        details = f"Angebot ID: {offer_id}, Token: Customer"
        
        self.log_test(
            "Kunde Angebot-Zugriff",
            f"Status {expected_status}",
            f"Status {actual_status}",
            passed,
            details
        )
        
        # Credentials zurücksetzen
        self.client.credentials()
        return passed
    
    def test_search_empty_results(self):
        """Test 4: Suche sollte leere Ergebnisse für nicht-existierende Begriffe zurückgeben"""
        print("🧪 Test 4: Such-Funktion mit nicht-existierenden Begriffen")
        
        response = self.client.get('/api/offers/?search=nichtexistierenderbegriff12345')
        
        expected_status = 200
        actual_status = response.status_code
        expected_count = 0
        actual_count = response.data.get('count', -1) if hasattr(response, 'data') else -1
        
        passed = (actual_status == expected_status) and (actual_count == expected_count)
        
        details = f"Such-Begriff: 'nichtexistierenderbegriff12345', Anzahl Ergebnisse: {actual_count}"
        
        self.log_test(
            "Suche - Leere Ergebnisse",
            f"Status {expected_status}, Count {expected_count}",
            f"Status {actual_status}, Count {actual_count}",
            passed,
            details
        )
        
        return passed
    
    def test_search_with_results(self):
        """Test 5: Suche sollte Ergebnisse für existierende Begriffe zurückgeben"""
        print("🧪 Test 5: Such-Funktion mit existierenden Begriffen")
        
        # Nach einem häufigen Begriff suchen (z.B. "web" oder "design")
        response = self.client.get('/api/offers/?search=web')
        
        expected_status = 200
        actual_status = response.status_code
        actual_count = response.data.get('count', 0) if hasattr(response, 'data') else 0
        
        passed = actual_status == expected_status
        
        details = f"Such-Begriff: 'web', Anzahl Ergebnisse: {actual_count}"
        
        self.log_test(
            "Suche - Mit Ergebnissen",
            f"Status {expected_status}",
            f"Status {actual_status}",
            passed,
            details
        )
        
        return passed
    
    def test_min_price_filter(self):
        """Test 6: min_price Filter sollte nur Angebote >= Wert zurückgeben"""
        print("🧪 Test 6: min_price Filter-Funktion")
        
        response = self.client.get('/api/offers/?min_price=75')
        
        expected_status = 200
        actual_status = response.status_code
        passed = actual_status == expected_status
        
        if passed and hasattr(response, 'data'):
            offers = response.data.get('results', [])
            all_valid = True
            for offer in offers:
                min_price = offer.get('min_price', 0)
                if min_price < 75:
                    all_valid = False
                    break
            
            passed = passed and all_valid
            details = f"Angebote gefunden: {len(offers)}, Alle >= 75€: {all_valid}"
        else:
            details = "Keine Daten erhalten"
        
        self.log_test(
            "min_price=75 Filter",
            f"Status {expected_status}, Alle Preise >= 75€",
            f"Status {actual_status}",
            passed,
            details
        )
        
        return passed
    
    def test_order_creation_authorization(self):
        """Test 7: Business-User sollten keine Bestellungen erstellen können (403 Forbidden)"""
        print("🧪 Test 7: Bestellungs-Autorisierung")
        
        # Erst ein OfferDetail finden
        offers_response = self.client.get('/api/offers/')
        if offers_response.status_code != 200 or not offers_response.data.get('results'):
            self.log_test(
                "Business-User Bestellung",
                "Test übersprungen",
                "Keine Angebote verfügbar",
                False,
                "Keine Test-Angebote für Bestellung vorhanden"
            )
            return False
        
        offer = offers_response.data['results'][0]
        offer_details = offer.get('details', [])
        if not offer_details:
            self.log_test(
                "Business-User Bestellung",
                "Test übersprungen",
                "Keine Angebots-Details verfügbar",
                False,
                "Keine OfferDetails für Test vorhanden"
            )
            return False
        
        offer_detail_id = offer_details[0]['id']
        
        # Mit Business-Token versuchen Bestellung zu erstellen
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        response = self.client.post('/api/orders/', {
            'offer_detail_id': offer_detail_id
        })
        
        expected_status = 403
        actual_status = response.status_code
        passed = actual_status == expected_status
        
        details = f"Business-User Token, OfferDetail ID: {offer_detail_id}"
        if hasattr(response, 'data'):
            details += f", Response: {response.data}"
        
        self.log_test(
            "Business-User Bestellung (403 erwartet)",
            f"Status {expected_status}",
            f"Status {actual_status}",
            passed,
            details
        )
        
        # Credentials zurücksetzen
        self.client.credentials()
        return passed
    
    def test_customer_order_creation(self):
        """Test 8: Customer-User sollten Bestellungen erstellen können"""
        print("🧪 Test 8: Kunden-Bestellungs-Erstellung")
        
        # Angebot eines anderen Users finden (nicht des Customer)
        offers_response = self.client.get('/api/offers/')
        if offers_response.status_code != 200:
            self.log_test(
                "Kunden-Bestellung",
                "Test übersprungen",
                "Keine Angebote verfügbar",
                False
            )
            return False
        
        suitable_offer = None
        for offer in offers_response.data.get('results', []):
            if offer.get('user') != self.customer_user.id and offer.get('details'):
                suitable_offer = offer
                break
        
        if not suitable_offer:
            self.log_test(
                "Kunden-Bestellung",
                "Test übersprungen",
                "Kein geeignetes Angebot gefunden",
                False,
                "Alle Angebote gehören dem Test-Customer oder haben keine Details"
            )
            return False
        
        offer_detail_id = suitable_offer['details'][0]['id']
        
        # Mit Customer-Token Bestellung erstellen
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.post('/api/orders/', {
            'offer_detail_id': offer_detail_id
        })
        
        expected_status = 201
        actual_status = response.status_code
        passed = actual_status == expected_status
        
        details = f"Customer-Token, OfferDetail ID: {offer_detail_id}"
        if not passed and hasattr(response, 'data'):
            details += f", Error: {response.data}"
        
        self.log_test(
            "Kunden-Bestellung (201 erwartet)",
            f"Status {expected_status}",
            f"Status {actual_status}",
            passed,
            details
        )
        
        # Credentials zurücksetzen
        self.client.credentials()
        return passed
    
    def run_all_tests(self):
        """Alle Tests ausführen"""
        print("🚀 Starte umfassende API-Feedback-Tests...")
        print("=" * 60)
        
        test_methods = [
            self.test_invalid_delivery_time,
            self.test_valid_delivery_time,
            self.test_customer_offer_access,
            self.test_search_empty_results,
            self.test_search_with_results,
            self.test_min_price_filter,
            self.test_order_creation_authorization,
            self.test_customer_order_creation
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                result = test_method()
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ FEHLER in {test_method.__name__}: {e}")
                self.log_test(
                    test_method.__name__,
                    "Erfolgreiche Ausführung",
                    f"Exception: {e}",
                    False
                )
        
        print("=" * 60)
        print("📊 TEST-ZUSAMMENFASSUNG:")
        print(f"Bestanden: {passed_tests}/{total_tests}")
        print(f"Erfolgsrate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALLE TESTS BESTANDEN! API ist bereit für Produktion.")
        else:
            print("⚠️  Einige Tests fehlgeschlagen. Überprüfung erforderlich.")
        
        return passed_tests == total_tests


def main():
    """Haupt-Testfunktion"""
    print("🧪 API Feedback Fixes - Comprehensive Testing")
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tester = APIFeedbackTester()
    
    try:
        success = tester.run_all_tests()
        
        # Detaillierte Ergebnisse ausgeben
        print("\n📋 DETAILLIERTE TEST-ERGEBNISSE:")
        for result in tester.test_results:
            print(f"{result['status']} {result['test']} ({result['timestamp']})")
            if result['details']:
                print(f"   {result['details']}")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ KRITISCHER FEHLER: {e}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
