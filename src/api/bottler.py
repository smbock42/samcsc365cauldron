import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)
    sql = f"UPDATE global_inventory SET num_red_ml = num_red_ml - {potions_delivered[0].quantity*potions_delivered[0].potion_type[0]}"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))

    sql = f"UPDATE global_inventory SET num_red_potions = num_red_potions + {potions_delivered[0].quantity}"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    sql = "SELECT num_red_ml from global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    first_row = result.first()
    num_red_ml = first_row[0]
    quantity = num_red_ml//100
    if quantity == 0:
        return []
    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": quantity,
            }
        ]
