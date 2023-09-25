import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        result = connection.execute("SELECT num_red_potions, num_red_ml, gold FROM global_inventory")
    print(result)
    return {"number_of_potions": 0, "ml_in_barrels": 0, "gold": 0}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
    return "OK"
