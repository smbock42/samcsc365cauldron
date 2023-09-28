import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    #TODO
    for barrel in barrels_delivered:
        print(barrel)
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    #DONE

    sql = "SELECT gold FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    first_row = result.first()
    gold = first_row[0]
    barrel = wholesale_catalog[0]
    potion_cost = barrel.price
    potential_quantity = gold // potion_cost
    if (potential_quantity > barrel.quantity):
        quantity = barrel.quantity
    else: 
        quantity = potential_quantity
    
    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": quantity,
        }
    ]

