import pytest
from app.config import settings

@pytest.mark.asyncio
async def test_treasurer_login_success(client, db):
    # Seeding manually for the test
    from app.models.user import User, RoleEnum
    from app.security import hash_password
    
    test_user = User(
        name="Test Treasurer",
        role=RoleEnum.TREASURER,
        access_code="test@finor.com",
        password_hash=hash_password("password123")
    )
    db.add(test_user)
    await db.commit()
    
    response = await client.post("/auth/treasurer/login", json={
        "email": "test@finor.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "access_token" in data["data"]

@pytest.mark.asyncio
async def test_treasurer_login_fail(client, db):
    response = await client.post("/auth/treasurer/login", json={
        "email": "nonexistent@finor.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_investor_login_success(client, db):
    from app.models.user import User, RoleEnum
    
    test_investor = User(
        name="Test Investor",
        role=RoleEnum.INVESTOR,
        access_code="INV-1234"
    )
    db.add(test_investor)
    await db.commit()
    
    response = await client.post("/auth/investor/login", json={
        "access_code": "INV-1234"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["access_code"] == "INV-1234"
    assert data["data"]["name"] == "Test Investor"

@pytest.mark.asyncio
async def test_investor_login_not_found(client, db):
    response = await client.post("/auth/investor/login", json={
        "access_code": "INV-9999"
    })
    
    assert response.status_code == 404
    assert "Personal code not found" in response.json()["detail"]
