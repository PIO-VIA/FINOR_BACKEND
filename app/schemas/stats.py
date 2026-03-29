from pydantic import BaseModel


class GlobalStats(BaseModel):
    total_invested: float
    total_spent: float
    execution_rate: float


class InvestorImpactItem(BaseModel):
    rubric_id: str
    rubric_name: str
    amount_invested: float
    total_spent_in_rubric: float
