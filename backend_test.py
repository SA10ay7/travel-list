#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Travel Packing List Application
Tests all endpoints with Arabic text support and realistic travel data
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://2c183e2e-3cc7-43c2-85b3-0c4f74d74da2.preview.emergentagent.com/api"

class TravelPackingListTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.created_list_id = None
        self.created_item_id = None
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        })
        
    def test_get_categories(self):
        """Test GET /api/categories endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/categories")
            
            if response.status_code == 200:
                categories = response.json()
                
                # Check if we have categories
                if len(categories) > 0:
                    # Verify Arabic text support
                    arabic_found = any('name_ar' in cat and cat['name_ar'] for cat in categories)
                    
                    if arabic_found:
                        self.log_test("GET Categories", True, 
                                    f"Retrieved {len(categories)} categories with Arabic support")
                        
                        # Print sample categories for verification
                        print("   Sample categories:")
                        for cat in categories[:3]:
                            print(f"     - {cat.get('name', 'N/A')} ({cat.get('name_ar', 'N/A')}) {cat.get('icon', '')}")
                        
                        return True
                    else:
                        self.log_test("GET Categories", False, 
                                    "Categories found but missing Arabic text support")
                        return False
                else:
                    self.log_test("GET Categories", False, "No categories returned")
                    return False
            else:
                self.log_test("GET Categories", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET Categories", False, f"Exception: {str(e)}")
            return False
    
    def test_create_travel_list(self):
        """Test POST /api/travel-lists endpoint with Arabic data"""
        try:
            # Realistic Arabic travel list data
            travel_list_data = {
                "name": "رحلة إلى دبي",  # Trip to Dubai
                "destination": "دبي، الإمارات العربية المتحدة"  # Dubai, UAE
            }
            
            response = self.session.post(
                f"{self.base_url}/travel-lists",
                json=travel_list_data
            )
            
            if response.status_code == 200:
                created_list = response.json()
                
                # Verify the created list has correct data
                if (created_list.get('name') == travel_list_data['name'] and 
                    created_list.get('destination') == travel_list_data['destination']):
                    
                    # Check if default items were created
                    items = created_list.get('items', [])
                    if len(items) > 0:
                        # Store the list ID for subsequent tests
                        self.created_list_id = created_list.get('id')
                        
                        # Check for Arabic items
                        arabic_items = [item for item in items if item.get('name_ar')]
                        
                        self.log_test("POST Travel List", True, 
                                    f"Created list '{travel_list_data['name']}' with {len(items)} default items ({len(arabic_items)} with Arabic names)")
                        
                        # Print sample items
                        print("   Sample default items:")
                        for item in items[:5]:
                            print(f"     - {item.get('name', 'N/A')} ({item.get('name_ar', 'N/A')}) [{item.get('category', 'N/A')}]")
                        
                        return True
                    else:
                        self.log_test("POST Travel List", False, 
                                    "List created but no default items were added")
                        return False
                else:
                    self.log_test("POST Travel List", False, 
                                "List created but data doesn't match input")
                    return False
            else:
                self.log_test("POST Travel List", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST Travel List", False, f"Exception: {str(e)}")
            return False
    
    def test_get_all_travel_lists(self):
        """Test GET /api/travel-lists endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/travel-lists")
            
            if response.status_code == 200:
                travel_lists = response.json()
                
                if len(travel_lists) > 0:
                    # Check if our created list is in the results
                    if self.created_list_id:
                        found_list = next((tl for tl in travel_lists if tl.get('id') == self.created_list_id), None)
                        if found_list:
                            self.log_test("GET All Travel Lists", True, 
                                        f"Retrieved {len(travel_lists)} travel lists including our created list")
                            return True
                        else:
                            self.log_test("GET All Travel Lists", False, 
                                        "Lists retrieved but our created list not found")
                            return False
                    else:
                        self.log_test("GET All Travel Lists", True, 
                                    f"Retrieved {len(travel_lists)} travel lists")
                        return True
                else:
                    self.log_test("GET All Travel Lists", False, "No travel lists found")
                    return False
            else:
                self.log_test("GET All Travel Lists", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET All Travel Lists", False, f"Exception: {str(e)}")
            return False
    
    def test_get_specific_travel_list(self):
        """Test GET /api/travel-lists/{list_id} endpoint"""
        if not self.created_list_id:
            self.log_test("GET Specific Travel List", False, 
                        "No list ID available from previous test")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/travel-lists/{self.created_list_id}")
            
            if response.status_code == 200:
                travel_list = response.json()
                
                # Verify the list data
                if (travel_list.get('id') == self.created_list_id and 
                    travel_list.get('name') == "رحلة إلى دبي"):
                    
                    items = travel_list.get('items', [])
                    self.log_test("GET Specific Travel List", True, 
                                f"Retrieved specific list with {len(items)} items")
                    return True
                else:
                    self.log_test("GET Specific Travel List", False, 
                                "List retrieved but data doesn't match expected values")
                    return False
            else:
                self.log_test("GET Specific Travel List", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET Specific Travel List", False, f"Exception: {str(e)}")
            return False
    
    def test_get_list_stats(self):
        """Test GET /api/travel-lists/{list_id}/stats endpoint"""
        if not self.created_list_id:
            self.log_test("GET List Stats", False, 
                        "No list ID available from previous test")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/travel-lists/{self.created_list_id}/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Verify stats structure
                required_fields = ['total_items', 'packed_items', 'remaining_items', 
                                 'progress_percentage', 'category_stats']
                
                if all(field in stats for field in required_fields):
                    total = stats['total_items']
                    packed = stats['packed_items']
                    remaining = stats['remaining_items']
                    progress = stats['progress_percentage']
                    
                    # Verify calculations
                    if remaining == total - packed and progress == (packed / total * 100 if total > 0 else 0):
                        self.log_test("GET List Stats", True, 
                                    f"Stats: {total} total, {packed} packed, {remaining} remaining, {progress}% progress")
                        
                        # Print category stats
                        print("   Category breakdown:")
                        for category, cat_stats in stats['category_stats'].items():
                            print(f"     - {category}: {cat_stats['packed']}/{cat_stats['total']}")
                        
                        return True
                    else:
                        self.log_test("GET List Stats", False, 
                                    "Stats calculations are incorrect")
                        return False
                else:
                    self.log_test("GET List Stats", False, 
                                f"Missing required fields in stats response")
                    return False
            else:
                self.log_test("GET List Stats", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET List Stats", False, f"Exception: {str(e)}")
            return False
    
    def test_add_custom_item(self):
        """Test POST /api/travel-lists/{list_id}/items endpoint with Arabic item"""
        if not self.created_list_id:
            self.log_test("POST Custom Item", False, 
                        "No list ID available from previous test")
            return False
            
        try:
            # Add a custom Arabic travel item
            custom_item = {
                "name": "Traditional Dress",
                "name_ar": "ثوب تقليدي",
                "category": "clothes",
                "notes": "للمناسبات الخاصة"  # For special occasions
            }
            
            response = self.session.post(
                f"{self.base_url}/travel-lists/{self.created_list_id}/items",
                json=custom_item
            )
            
            if response.status_code == 200:
                created_item = response.json()
                
                # Verify the created item
                if (created_item.get('name') == custom_item['name'] and 
                    created_item.get('name_ar') == custom_item['name_ar'] and
                    created_item.get('notes') == custom_item['notes']):
                    
                    self.created_item_id = created_item.get('id')
                    self.log_test("POST Custom Item", True, 
                                f"Added custom item '{custom_item['name']}' ({custom_item['name_ar']})")
                    return True
                else:
                    self.log_test("POST Custom Item", False, 
                                "Item created but data doesn't match input")
                    return False
            else:
                self.log_test("POST Custom Item", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST Custom Item", False, f"Exception: {str(e)}")
            return False
    
    def test_update_item(self):
        """Test PUT /api/travel-lists/{list_id}/items/{item_id} endpoint"""
        if not self.created_list_id or not self.created_item_id:
            self.log_test("PUT Update Item", False, 
                        "No list ID or item ID available from previous tests")
            return False
            
        try:
            # Update the item - mark as packed and add notes
            updates = {
                "is_packed": True,
                "notes": "تم تحضيره وجاهز للسفر"  # Prepared and ready for travel
            }
            
            response = self.session.put(
                f"{self.base_url}/travel-lists/{self.created_list_id}/items/{self.created_item_id}",
                json=updates
            )
            
            if response.status_code == 200:
                updated_item = response.json()
                
                # Verify the updates
                if (updated_item.get('is_packed') == True and 
                    updated_item.get('notes') == updates['notes']):
                    
                    self.log_test("PUT Update Item", True, 
                                f"Updated item - marked as packed with Arabic notes")
                    return True
                else:
                    self.log_test("PUT Update Item", False, 
                                "Item updated but changes don't match input")
                    return False
            else:
                self.log_test("PUT Update Item", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PUT Update Item", False, f"Exception: {str(e)}")
            return False
    
    def test_verify_stats_after_update(self):
        """Verify that stats are updated correctly after marking item as packed"""
        if not self.created_list_id:
            self.log_test("Verify Stats After Update", False, 
                        "No list ID available from previous test")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/travel-lists/{self.created_list_id}/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Should have at least 1 packed item now
                if stats['packed_items'] >= 1:
                    progress = stats['progress_percentage']
                    self.log_test("Verify Stats After Update", True, 
                                f"Stats updated correctly - {stats['packed_items']} packed items, {progress}% progress")
                    return True
                else:
                    self.log_test("Verify Stats After Update", False, 
                                "Stats not updated after marking item as packed")
                    return False
            else:
                self.log_test("Verify Stats After Update", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify Stats After Update", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_item(self):
        """Test DELETE /api/travel-lists/{list_id}/items/{item_id} endpoint"""
        if not self.created_list_id or not self.created_item_id:
            self.log_test("DELETE Item", False, 
                        "No list ID or item ID available from previous tests")
            return False
            
        try:
            response = self.session.delete(
                f"{self.base_url}/travel-lists/{self.created_list_id}/items/{self.created_item_id}"
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('message') == "Item deleted successfully":
                    self.log_test("DELETE Item", True, 
                                "Successfully deleted custom item")
                    return True
                else:
                    self.log_test("DELETE Item", False, 
                                "Unexpected response message")
                    return False
            else:
                self.log_test("DELETE Item", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("DELETE Item", False, f"Exception: {str(e)}")
            return False
    
    def test_verify_item_deleted(self):
        """Verify that the item was actually deleted from the list"""
        if not self.created_list_id or not self.created_item_id:
            self.log_test("Verify Item Deleted", False, 
                        "No list ID or item ID available from previous tests")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/travel-lists/{self.created_list_id}")
            
            if response.status_code == 200:
                travel_list = response.json()
                items = travel_list.get('items', [])
                
                # Check if the deleted item is still in the list
                deleted_item = next((item for item in items if item.get('id') == self.created_item_id), None)
                
                if deleted_item is None:
                    self.log_test("Verify Item Deleted", True, 
                                "Confirmed item was successfully removed from list")
                    return True
                else:
                    self.log_test("Verify Item Deleted", False, 
                                "Item still exists in list after deletion")
                    return False
            else:
                self.log_test("Verify Item Deleted", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify Item Deleted", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend API tests in sequence"""
        print(f"🚀 Starting Travel Packing List Backend API Tests")
        print(f"📍 Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test sequence
        tests = [
            self.test_get_categories,
            self.test_create_travel_list,
            self.test_get_all_travel_lists,
            self.test_get_specific_travel_list,
            self.test_get_list_stats,
            self.test_add_custom_item,
            self.test_update_item,
            self.test_verify_stats_after_update,
            self.test_delete_item,
            self.test_verify_item_deleted
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            if test():
                passed += 1
            else:
                failed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 80)
        print(f"📊 TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("🎉 All tests passed! Backend API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return failed == 0

def main():
    """Main test execution"""
    tester = TravelPackingListTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()