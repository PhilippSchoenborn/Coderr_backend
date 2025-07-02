#!/usr/bin/env python
"""
Schnelltest für die wichtigsten API-Feedback-Fixes
Einfache HTTP-Requests ohne Django-Setup
"""
import requests
import json
from datetime import datetime


class QuickAPITester:
    """Schnelle API-Tests über HTTP-Requests"""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.results = []
    
    def log_result(self, test_name, expected, actual, passed, details=""):
        """Test-Ergebnis protokollieren"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} {test_name}")
        print(f"   Erwartet: {expected} | Erhalten: {actual}")
        if details:
            print(f"   Details: {details}")
        print()
        
        self.results.append({
            'test': test_name,
            'passed': passed,
            'expected': expected,
            'actual': actual
        })
    
    def test_invalid_delivery_time(self):
        """Test: Invalid delivery_time sollte 400 zurückgeben"""
        print("🧪 Test: Invalid delivery_time Parameter")
        
        url = f"{self.base_url}/api/offers/?max_delivery_time=invalid"
        
        try:
            response = requests.get(url, timeout=10)
            expected = 400
            actual = response.status_code
            passed = actual == expected
            
            details = f"URL: {url}"
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Response: {response.text[:100]}"
            
            self.log_result(
                "Invalid delivery_time=invalid",
                f"Status {expected}",
                f"Status {actual}",
                passed,
                details
            )
            
            return passed
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Invalid delivery_time=invalid",
                "Status 400",
                f"Connection Error: {e}",
                False
            )
            return False
    
    def test_valid_delivery_time(self):
        """Test: Gültige delivery_time sollte 200 zurückgeben"""
        print("🧪 Test: Gültige delivery_time Parameter")
        
        url = f"{self.base_url}/api/offers/?max_delivery_time=7"
        
        try:
            response = requests.get(url, timeout=10)
            expected = 200
            actual = response.status_code
            passed = actual == expected
            
            details = f"URL: {url}"
            if response.status_code == 200:
                try:
                    data = response.json()
                    count = data.get('count', 0)
                    details += f", Gefilterte Angebote: {count}"
                except:
                    details += ", JSON Parse Error"
            
            self.log_result(
                "Valid delivery_time=7",
                f"Status {expected}",
                f"Status {actual}",
                passed,
                details
            )
            
            return passed
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Valid delivery_time=7",
                "Status 200",
                f"Connection Error: {e}",
                False
            )
            return False
    
    def test_search_empty_results(self):
        """Test: Suche mit nicht-existierendem Begriff"""
        print("🧪 Test: Suche mit nicht-existierendem Begriff")
        
        url = f"{self.base_url}/api/offers/?search=nichtexistierenderbegriff12345"
        
        try:
            response = requests.get(url, timeout=10)
            expected_status = 200
            actual_status = response.status_code
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    count = data.get('count', -1)
                    expected_count = 0
                    passed = (actual_status == expected_status) and (count == expected_count)
                    
                    details = f"URL: {url}, Anzahl Ergebnisse: {count}"
                    
                    self.log_result(
                        "Search empty results",
                        f"Status {expected_status}, Count {expected_count}",
                        f"Status {actual_status}, Count {count}",
                        passed,
                        details
                    )
                    
                    return passed
                    
                except Exception as e:
                    self.log_result(
                        "Search empty results",
                        "Status 200, Count 0",
                        f"Status {actual_status}, JSON Error: {e}",
                        False
                    )
                    return False
            else:
                self.log_result(
                    "Search empty results",
                    f"Status {expected_status}",
                    f"Status {actual_status}",
                    False
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Search empty results",
                "Status 200",
                f"Connection Error: {e}",
                False
            )
            return False
    
    def test_min_price_filter(self):
        """Test: min_price Filter"""
        print("🧪 Test: min_price Filter")
        
        url = f"{self.base_url}/api/offers/?min_price=75"
        
        try:
            response = requests.get(url, timeout=10)
            expected = 200
            actual = response.status_code
            passed = actual == expected
            
            details = f"URL: {url}"
            if response.status_code == 200:
                try:
                    data = response.json()
                    count = data.get('count', 0)
                    results = data.get('results', [])
                    
                    # Prüfen ob alle Angebote min_price >= 75 haben
                    all_valid = True
                    for offer in results:
                        min_price = offer.get('min_price', 0)
                        if min_price < 75:
                            all_valid = False
                            break
                    
                    passed = passed and all_valid
                    details += f", Angebote: {count}, Alle >= 75€: {all_valid}"
                    
                except:
                    details += ", JSON Parse Error"
            
            self.log_result(
                "min_price=75 Filter",
                f"Status {expected}, Alle Preise >= 75€",
                f"Status {actual}",
                passed,
                details
            )
            
            return passed
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "min_price=75 Filter",
                "Status 200",
                f"Connection Error: {e}",
                False
            )
            return False
    
    def test_offers_endpoint_available(self):
        """Test: Basis-Test ob API erreichbar ist"""
        print("🧪 Test: API Erreichbarkeit")
        
        url = f"{self.base_url}/api/offers/"
        
        try:
            response = requests.get(url, timeout=10)
            expected = 200
            actual = response.status_code
            passed = actual == expected
            
            details = f"URL: {url}"
            if response.status_code == 200:
                try:
                    data = response.json()
                    count = data.get('count', 0)
                    details += f", Angebote verfügbar: {count}"
                except:
                    details += ", JSON Parse Error"
            
            self.log_result(
                "API Erreichbarkeit",
                f"Status {expected}",
                f"Status {actual}",
                passed,
                details
            )
            
            return passed
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "API Erreichbarkeit",
                "Status 200",
                f"Connection Error: {e}",
                False,
                "Ist der Django-Server gestartet? (python manage.py runserver)"
            )
            return False
    
    def run_quick_tests(self):
        """Alle Schnelltests ausführen"""
        print("🚀 API Feedback Fixes - Schnelltests")
        print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        tests = [
            self.test_offers_endpoint_available,
            self.test_invalid_delivery_time,
            self.test_valid_delivery_time,
            self.test_search_empty_results,
            self.test_min_price_filter
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ FEHLER in {test.__name__}: {e}")
        
        print("=" * 50)
        print(f"📊 ERGEBNIS: {passed}/{total} Tests bestanden")
        
        if passed == total:
            print("🎉 Alle Schnelltests erfolgreich!")
        else:
            print("⚠️  Einige Tests fehlgeschlagen")
        
        return passed == total


def main():
    """Haupt-Funktion"""
    print("🧪 API Feedback Fixes - Schnelltest")
    print("Testet die wichtigsten Fixes über HTTP-Requests")
    print()
    
    tester = QuickAPITester()
    success = tester.run_quick_tests()
    
    print("\n💡 HINWEISE:")
    print("- Stelle sicher, dass der Django-Server läuft: python manage.py runserver")
    print("- Für umfassende Tests verwende: test_api_feedback_comprehensive.py")
    print("- Bei Fehlern prüfe die Server-Logs")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
