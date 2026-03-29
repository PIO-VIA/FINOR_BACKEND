import pytest

@pytest.mark.asyncio
async def test_create_rubric_success(client, treasurer_token):
    response = await client.post(
        "/rubrics/",
        json={"name": "Health", "description": "Medical expenses", "initial_balance": 1000.0},
        headers={"Authorization": f"Bearer {treasurer_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["name"] == "Health"
    assert data["data"]["initial_balance"] == 1000.0

@pytest.mark.asyncio
async def test_create_rubric_duplicate(client, db, treasurer_token):
    from app.models.rubric import Rubric
    db.add(Rubric(name="Health", description="Test", initial_balance=0))
    await db.commit()
    
    response = await client.post(
        "/rubrics/",
        json={"name": "Health", "description": "Duplicate", "initial_balance": 0},
        headers={"Authorization": f"Bearer {treasurer_token}"}
    )
    
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_list_rubrics(client, db):
    from app.models.rubric import Rubric
    db.add(Rubric(name="R1", description="D1", initial_balance=100))
    db.add(Rubric(name="R2", description="D2", initial_balance=200))
    await db.commit()
    
    response = await client.get("/rubrics/")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 2
    assert any(r["name"] == "R1" for r in data)
    assert any(r["name"] == "R2" for r in data)

@pytest.mark.asyncio
async def test_delete_rubric_unauthorized(client, db):
    response = await client.delete("/rubrics/some-id")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_rubric_not_found(client, treasurer_token):
    response = await client.delete(
        "/rubrics/nonexistent-id",
        headers={"Authorization": f"Bearer {treasurer_token}"}
    )
    assert response.status_code == 404
