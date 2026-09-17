"""
Pydantic models defining the API's response shapes.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Contract(BaseModel):
    contract_id: Optional[str] = None
    tender_title: Optional[str] = None
    buyer_name: Optional[str] = None
    price_excl_vat: Optional[float] = None
    price_incl_vat: Optional[float] = None
    announcement_date: Optional[datetime] = None
    contract_status: Optional[str] = None


class BuyerSpend(BaseModel):
    buyer_name: str
    total_spend: float
    contract_count: int


class StatsSummary(BaseModel):
    total_contracts: int
    total_value: float
    unique_buyers: int
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
