"""
Live Q&A Platform - HTTP Test Suite
====================================
Simple HTTP-based tests that verify the application is running correctly
without requiring browser automation (Selenium).

These tests are faster and more reliable in CI/CD environments.

Prerequisites:
- Frontend running on http://localhost:3001
- Backend running on http://localhost:3000
"""

import requests
import pytest


class TestHTTPBasic:
    """Basic HTTP tests for Live Q&A Platform"""
    
    FRONTEND_URL = "http://localhost:3001"
    BACKEND_URL = "http://localhost:3000"
    TIMEOUT = 10
    
    def test_frontend_server_running(self):
        """Test 1: Verify frontend server is accessible"""
        try:
            response = requests.get(self.FRONTEND_URL, timeout=self.TIMEOUT)
            assert response.status_code == 200, f"Frontend returned status code {response.status_code}"
            print("✅ Frontend server is running")
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Frontend server is not accessible: {e}")
    
    def test_backend_server_running(self):
        """Test 2: Verify backend server is accessible"""
        try:
            # Try the GraphQL endpoint
            response = requests.post(
                f"{self.BACKEND_URL}/graphql",
                json={"query": "{ __typename }"},
                timeout=self.TIMEOUT
            )
            # Backend should respond (even if it's an error, it means it's running)
            assert response.status_code in [200, 400], f"Backend returned unexpected status code {response.status_code}"
            print("✅ Backend server is running")
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Backend server is not accessible: {e}")
    
    def test_frontend_home_page(self):
        """Test 3: Verify frontend home page loads with expected content"""
        try:
            response = requests.get(self.FRONTEND_URL, timeout=self.TIMEOUT)
            assert response.status_code == 200
            
            # Check for basic Next.js content
            content = response.text.lower()
            assert len(content) > 0, "Frontend returned empty content"
            
            # Check for common HTML elements
            assert "<html" in content or "<!doctype html>" in content, "Response is not HTML"
            print("✅ Frontend home page loads successfully")
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to load frontend home page: {e}")
    
    def test_frontend_routes_accessible(self):
        """Test 4: Verify key frontend routes are accessible"""
        routes = ["/", "/about"]
        
        for route in routes:
            try:
                url = f"{self.FRONTEND_URL}{route}"
                response = requests.get(url, timeout=self.TIMEOUT, allow_redirects=True)
                # Accept 200 (success) or 3xx (redirect to auth)
                assert response.status_code in [200, 301, 302, 307, 308], \
                    f"Route {route} returned status code {response.status_code}"
                print(f"✅ Route {route} is accessible")
            except requests.exceptions.RequestException as e:
                pytest.fail(f"Route {route} is not accessible: {e}")
    
    def test_backend_graphql_endpoint(self):
        """Test 5: Verify GraphQL endpoint responds correctly"""
        try:
            # Send a basic introspection query
            response = requests.post(
                f"{self.BACKEND_URL}/graphql",
                json={
                    "query": "{ __schema { queryType { name } } }"
                },
                headers={"Content-Type": "application/json"},
                timeout=self.TIMEOUT
            )
            
            # GraphQL should respond with 200 or 400 (if auth required)
            assert response.status_code in [200, 400, 401], \
                f"GraphQL endpoint returned unexpected status code {response.status_code}"
            
            # Check if response is JSON
            try:
                json_response = response.json()
                assert json_response is not None, "GraphQL endpoint returned invalid JSON"
                print("✅ GraphQL endpoint is responding correctly")
            except ValueError:
                pytest.fail("GraphQL endpoint did not return valid JSON")
                
        except requests.exceptions.RequestException as e:
            pytest.fail(f"GraphQL endpoint is not accessible: {e}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
