import pytest
from app.models.investment import InvestmentStatusEnum

@pytest.mark.asyncio
async def test_declare_investment_new_investor(client, db):
    from app.models.rubric import Rubric
    rubric = Rubric(name="Health", description="Test", initial_balance=0)
    db.add(rubric)
    await db.commit()
    await db.refresh(rubric)
    
    response = await client.post("/investments/", json={
        "investor_name": "John Doe",
        "rubric_id": rubric.id,
        "amount": 500.0,
        "bank_receipt_code": "REC-123"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["is_new_investor"] is True
    assert "INV-" in data["data"]["access_code"]
    assert data["data"]["investment"]["amount"] == 500.0

@pytest.mark.asyncio
async def test_declare_investment_returning_investor(client, db):
    from app.models.rubric import Rubric
    from app.models.user import User, RoleEnum
    
    rubric = Rubric(name="Health", description="Test", initial_balance=0)
    db.add(rubric)
    investor = User(name="John Doe", role=RoleEnum.INVESTOR, access_code="INV-1234")
    db.add(investor)
    await db.commit()
    await db.refresh(rubric)
    
    response = await client.post("/investments/", json={
        "access_code": "INV-1234",
        "rubric_id": rubric.id,
        "amount": 200.0,
        "bank_receipt_code": "REC-456"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["is_new_investor"] is False
    assert data["data"]["access_code"] == "INV-1234"

@pytest.mark.asyncio
async def test_validate_investment(client, db, treasurer_token):
    from app.models.rubric import Rubric
    from app.models.user import User, RoleEnum
    from app.models.investment import Investment
    
    rub = Rubric(name="R", description="D", initial_balance=0)
    db.add(rub)
    inv = User(name="I", role=RoleEnum.INVESTOR, access_code="C")
    db.add(inv)
    await db.commit()
    
    investment = Investment(
        id="test-inv-id",
        investor_id=inv.id,
        rubric_id=rub.id,
        amount=100.0,
        bank_receipt_code="B",
        status=InvestmentStatusEnum.PENDING
    )
    db.add(investment)
    await db.commit()
    
    response = await client.patch(
        f"/investments/{investment.id}/validate",
        headers={"Authorization": f"Bearer {treasurer_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "VALIDATED"


@pytest.mark.asyncio
async def test_declare_investment_existing_name_no_code(client, db):
    from app.models.rubric import Rubric
    rubric = Rubric(name="Education", description="Test", initial_balance=0)
    db.add(rubric)
    await db.commit()
    await db.refresh(rubric)
    
    # First investment
    response1 = await client.post("/investments/", json={
        "investor_name": "Jane Doe",
        "rubric_id": rubric.id,
        "amount": 1000.0,
        "bank_receipt_code": "REC-789"
    })
    assert response1.status_code == 201
    data1 = response1.json()
    access_code = data1["data"]["access_code"]
    assert data1["data"]["is_new_investor"] is True
    
    # Second investment with same name, no access code
    response2 = await client.post("/investments/", json={
        "investor_name": "Jane Doe",
        "rubric_id": rubric.id,
        "amount": 500.0,
        "bank_receipt_code": "REC-999"
    })
    assert response2.status_code == 201
    data2 = response2.json()
    assert data2["data"]["access_code"] == access_code
    assert data2["data"]["is_new_investor"] is False
