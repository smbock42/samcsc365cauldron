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
    #TODO: Return items
    potion_quantity_sql = "SELECT SUM(quantity) FROM bottle_table"
    with db.engine.begin() as connection:
        potion_quantity = connection.execute(sqlalchemy.text(potion_quantity_sql))
    potion_quantity = potion_quantity.first()[0]
    
    ml_barrels_sql = "SELECT SUM(quantity) FROM barrel_table"
    with db.engine.begin() as connection:
        ml_barrels = connection.execute(sqlalchemy.text(ml_barrels_sql))
    ml_barrels = ml_barrels.first()[0]
    
    gold_sql = "SELECT SUM(amount) from cash_ledger"
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text(gold_sql))
    gold = gold.first()[0]
    return {"number_of_potions": potion_quantity, "ml_in_barrels": ml_barrels, "gold": gold}


class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    #TODO - not sure what to put here
    print(audit_explanation)
    # with db.engine.begin() as connection:
    #     result = connection.execute(sql_to_execute)
    return "OK"
