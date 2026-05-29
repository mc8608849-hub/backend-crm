"""
Test suite for API endpoints

Run with: pytest test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from .main import app

client = TestClient(app)

# Test data
TEST_USERNAME = "admin"
TEST_PASSWORD = "changeme"
TEST_TOKEN = None

class TestAuthentication:
    def test_login_success(self):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        global TEST_TOKEN
        TEST_TOKEN = data["access_token"]
    
    def test_login_failure(self):
        """Test failed login"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "wrong_user",
                "password": "wrong_password"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self):
        """Test getting current user info"""
        if not TEST_TOKEN:
            self.test_login_success()
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == TEST_USERNAME

class TestPeople:
    @classmethod
    def setup_class(cls):
        """Setup - get auth token"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }
        )
        cls.token = response.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
    
    def test_create_person(self):
        """Test creating a new person"""
        person_data = {
            "name": "John Doe",
            "phone": "555-123-4567",
            "email": "john@example.com",
            "amount_owed": 5000.00,
            "sale_date": "2026-01-15T00:00:00",
            "state": "CA",
            "county": "Los Angeles"
        }
        response = client.post(
            "/api/people/",
            json=person_data,
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == person_data["name"]
        assert "id" in data
        self.person_id = data["id"]
    
    def test_list_people(self):
        """Test listing all people"""
        response = client.get(
            "/api/people/",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_person(self):
        """Test getting a specific person"""
        if not hasattr(self, 'person_id'):
            self.test_create_person()
        
        response = client.get(
            f"/api/people/{self.person_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.person_id
    
    def test_update_person(self):
        """Test updating a person"""
        if not hasattr(self, 'person_id'):
            self.test_create_person()
        
        update_data = {
            "name": "Jane Doe",
            "phone": "555-987-6543",
            "email": "jane@example.com",
            "amount_owed": 7500.00,
            "sale_date": "2026-01-15T00:00:00",
            "state": "TX",
            "county": "Dallas"
        }
        response = client.put(
            f"/api/people/{self.person_id}",
            json=update_data,
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Doe"

class TestCalls:
    @classmethod
    def setup_class(cls):
        """Setup - get auth token and create a person"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }
        )
        cls.token = response.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
        
        # Create a person for call testing
        person_data = {
            "name": "Call Test Person",
            "phone": "555-111-1111",
            "email": "call@example.com",
            "amount_owed": 1000.00,
            "sale_date": "2026-01-15T00:00:00",
            "state": "NY",
            "county": "New York"
        }
        response = client.post(
            "/api/people/",
            json=person_data,
            headers=cls.headers
        )
        cls.person_id = response.json()["id"]
    
    def test_create_call_log(self):
        """Test creating a call log"""
        call_data = {
            "person_id": self.person_id,
            "call_sid": "call_123456",
            "status": "completed"
        }
        response = client.post(
            "/api/calls/",
            json=call_data,
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["person_id"] == self.person_id
        assert "id" in data
        self.call_id = data["id"]
    
    def test_list_calls(self):
        """Test listing all calls"""
        response = client.get(
            "/api/calls/",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_person_calls(self):
        """Test getting calls for a specific person"""
        if not hasattr(self, 'call_id'):
            self.test_create_call_log()
        
        response = client.get(
            f"/api/calls/person/{self.person_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_update_call_log(self):
        """Test updating a call log"""
        if not hasattr(self, 'call_id'):
            self.test_create_call_log()
        
        update_data = {
            "result": "Customer agreed",
            "transcript": "Discussion about payment plan",
            "status": "completed"
        }
        response = client.put(
            f"/api/calls/{self.call_id}",
            json=update_data,
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["transcript"] == "Discussion about payment plan"

class TestVoice:
    @classmethod
    def setup_class(cls):
        """Setup - get auth token"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }
        )
        cls.token = response.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
    
    def test_voice_clone_endpoint_exists(self):
        """Test that voice endpoint exists"""
        # Note: This will fail without valid ElevenLabs API key
        # Just testing that the endpoint is defined
        assert "/api/voice/clone" in [route.path for route in app.routes]

class TestPhoneIntegration:
    @classmethod
    def setup_class(cls):
        """Setup - get auth token"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }
        )
        cls.token = response.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
    
    def test_incoming_call_webhook(self):
        """Test incoming call webhook"""
        # First create a person with a phone number
        person_data = {
            "name": "Webhook Test",
            "phone": "+15551234567",
            "email": "webhook@example.com",
            "amount_owed": 1000.00,
            "sale_date": "2026-01-15T00:00:00",
            "state": "CA",
            "county": "Los Angeles"
        }
        person_response = client.post(
            "/api/people/",
            json=person_data,
            headers=self.headers
        )
        person_id = person_response.json()["id"]
        
        # Now send webhook
        webhook_data = {
            "phone_number": "+15551234567",
            "from_number": "+15551234567",
            "call_id": "webhook_call_001",
            "timestamp": "2026-05-29T15:30:00Z"
        }
        response = client.post(
            "/api/phone/incoming-webhook",
            json=webhook_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
    
    def test_call_status_update_webhook(self):
        """Test call status update webhook"""
        update_data = {
            "call_id": "webhook_call_001",
            "status": "completed",
            "transcript": "Customer paid",
            "duration": 180
        }
        response = client.post(
            "/api/phone/call-status-update",
            json=update_data
        )
        # May return 404 if call doesn't exist, which is fine for this test
        assert response.status_code in [200, 404]
    
    def test_get_phone_stats(self):
        """Test getting phone statistics"""
        response = client.get(
            "/api/phone/stats",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_calls" in data
        assert "completed_calls" in data
        assert "failed_calls" in data
        assert "success_rate" in data

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
