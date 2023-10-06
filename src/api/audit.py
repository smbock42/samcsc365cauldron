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
    sql = "SELECT sku, quantity FROM bottle_table"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))

    result = result.all()
    
    return result

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
