import pytest
from datetime import datetime

@pytest.mark.asyncio
async def test_get_global_stats_empty(client):
    response = await client.get("/stats/global")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_invested"] == 0
    assert data["total_spent"] == 0

@pytest.mark.asyncio
async def test_get_global_stats_calculated(client, db):
    from app.models.rubric import Rubric
    from app.models.user import User, RoleEnum
    from app.models.investment import Investment, InvestmentStatusEnum
    from app.models.expense import Expense
    
    rubric = Rubric(name="R", description="D", initial_balance=1000)
    db.add(rubric)
    investor = User(name="I", role=RoleEnum.INVESTOR, access_code="C")
    db.add(investor)
    treasurer = User(name="T", role=RoleEnum.TREASURER, access_code="admin@test.com")
    db.add(treasurer)
    await db.commit()
    
    # 500 invested (validated)
    db.add(Investment(
        investor_id=investor.id, rubric_id=rubric.id, amount=500.0, 
        bank_receipt_code="R1", status=InvestmentStatusEnum.VALIDATED
    ))
    # 200 spent
    db.add(Expense(
        rubric_id=rubric.id, amount=200.0, description="E", receipt_number="RE",
        date=datetime.utcnow(), treasurer_id=treasurer.id
    ))
    await db.commit()
    
    response = await client.get("/stats/global")
    assert response.status_code == 200
    data = response.json()["data"]
    # 1000 initial + 500 validated = 1500 total invested in terms of "stats" logic?
    # Wait, check app/crud/investment.py logic for GlobalStats
    # Usually it's sum of validated investments.
    # total_invested = sum(Investment.amount where status=VALIDATED)
    assert data["total_invested"] == 500.0
    assert data["total_spent"] == 200.0
    assert data["execution_rate"] == 40.0 # 200/500 * 100
