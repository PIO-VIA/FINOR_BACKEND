import pytest

@pytest.mark.asyncio
async def test_create_transfer_success(client, db, treasurer_token):
    from app.models.rubric import Rubric
    r1 = Rubric(name="R1", description="S", initial_balance=1000)
    r2 = Rubric(name="R2", description="D", initial_balance=100)
    db.add_all([r1, r2])
    await db.commit()
    
    response = await client.post(
        "/transfers/",
        json={
            "source_rubric_id": r1.id,
            "destination_rubric_id": r2.id,
            "amount": 300.0,
            "reason": "Test Transfer",
            "date": "2026-03-29"
        },
        headers={"Authorization": f"Bearer {treasurer_token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["data"]["amount"] == 300.0

@pytest.mark.asyncio
async def test_create_transfer_same_rubric(client, treasurer_token):
    response = await client.post(
        "/transfers/",
        json={
            "source_rubric_id": "same",
            "destination_rubric_id": "same",
            "amount": 100.0
        },
        headers={"Authorization": f"Bearer {treasurer_token}"}
    )
    assert response.status_code == 422
