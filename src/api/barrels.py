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
    print(barrels_delivered)
    barrel = barrels_delivered[0]
    add_barrel_sql = f"UPDATE global_inventory SET num_red_ml = num_red_ml + {barrel.ml_per_barrel*barrel.quantity}"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(add_barrel_sql))
    subtract_gold_sql = f"UPDATE global_inventory SET gold = gold - {barrel.price * barrel.quantity}"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(subtract_gold_sql))
    return "OK"

"""
[Barrel(sku='MEDIUM_RED_BARREL', ml_per_barrel=2500, potion_type=[1, 0, 0, 0], price=250, quantity=10), Barrel(sku='SMALL_RED_BARREL', ml_per_barrel=500, potion_type=[1, 0, 0, 0], price=100, quantity=10), Barrel(sku='MEDIUM_GREEN_BARREL', ml_per_barrel=2500, potion_type=[0, 1, 0, 0], price=250, quantity=10), Barrel(sku='SMALL_GREEN_BARREL', ml_per_barrel=500, potion_type=[0, 1, 0, 0], price=100, quantity=10), Barrel(sku='MEDIUM_BLUE_BARREL', ml_per_barrel=2500, potion_type=[0, 0, 1, 0], price=300, quantity=10), Barrel(sku='SMALL_BLUE_BARREL', ml_per_barrel=500, potion_type=[0, 0, 1, 0], price=120, quantity=10), Barrel(sku='MINI_RED_BARREL', ml_per_barrel=200, potion_type=[1, 0, 0, 0], price=60, quantity=1), Barrel(sku='MINI_GREEN_BARREL', ml_per_barrel=200, potion_type=[1, 0, 0, 0], price=60, quantity=1), Barrel(sku='MINI_BLUE_BARREL', ml_per_barrel=200, potion_type=[1, 0, 0, 0], price=60, quantity=1)]
"""

#green 30%
#green-small 5%
#green
#red 50%

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    sql = "SELECT num_red_potions FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    first_row = result.first()
    num_red_potions = first_row[0]
    purchase_list = []
    for barrel in wholesale_catalog:
        if barrel.sku == "SMALL_RED_BARREL" or barrel.sku == "small_red_barrel" or "red" in barrel.sku or barrel.potion_type[0] == 100:
            purchase_list.append(barrel)
    if num_red_potions < 15:

        sql = "SELECT gold FROM global_inventory"
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()
        gold = first_row[0]
        barrel = purchase_list[0]
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
    return []


