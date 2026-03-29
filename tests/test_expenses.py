import pytest

@pytest.mark.asyncio
async def test_create_expense_success(client, db, treasurer_token):
    from app.models.rubric import Rubric
    rub = Rubric(name="Health", description="D", initial_balance=5000)
    db.add(rub)
    await db.commit()
    
    response = await client.post(
        "/expenses/",
        json={
            "rubric_id": rub.id,
            "amount": 200.0,
            "description": "Medicine",
            "receipt_number": "R-001",
            "date": "2026-03-29"
        },
        headers={"Authorization": f"Bearer {treasurer_token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["data"]["amount"] == 200.0

@pytest.mark.asyncio
async def test_create_expense_insufficient_funds(client, db, treasurer_token):
    # This should still work as we don't have a strict "no-deficit" check on expense creation yet
    # but we should check the balance afterwards.
    from app.models.rubric import Rubric
    rub = Rubric(name="Empty", description="D", initial_balance=0)
    db.add(rub)
    await db.commit()
    
    response = await client.post(
        "/expenses/",
        json={
            "rubric_id": rub.id,
            "amount": 1000.0,
            "description": "Overspend",
            "receipt_number": "R-999",
            "date": "2026-03-29"
        },
        headers={"Authorization": f"Bearer {treasurer_token}"}
    )
    assert response.status_code == 201
