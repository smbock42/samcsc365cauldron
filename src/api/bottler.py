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

#TODO: Make bottler, cash, and barrel ledgers. 

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)
    for potion in potions_delivered:
        #update barrel_table (ml)
        #TODO: change from 100 when mixing colors
        rsql = f"UPDATE barrel_table SET quantity = quantity - {potion.quantity * potion.potion_type[0]} WHERE r = 100"
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(rsql))
        gsql = f"UPDATE barrel_table SET quantity = quantity - {potion.quantity * potion.potion_type[1]} WHERE g = 100"
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(gsql))
        bsql = f"UPDATE barrel_table SET quantity = quantity - {potion.quantity * potion.potion_type[2]} WHERE b = 100"
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(bsql))
        dsql = f"UPDATE barrel_table SET quantity = quantity - {potion.quantity * potion.potion_type[3]} WHERE d = 100"
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(dsql))
        
        
        
        
        # update bottle_table (potions)
        sql = f"UPDATE bottle_table SET quantity = quantity + {potion.quantity} WHERE r= {potion.potion_type[0]} AND g = {potion.potion_type[1]} AND b = {potion.potion_type[2]} AND d = {potion.potion_type[3]}"
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
    
    quantity_check_sku = "SELECT name, quantity, r,g,b,d, make_more FROM bottle_table"
    with db.engine.begin() as connection:
        quantity_check = connection.execute(sqlalchemy.text(quantity_check_sku))
    bottles = quantity_check.all()
    current_amount_of_potions = 0
    for value in bottles:
        current_amount_of_potions += value.quantity
    available_storage = 300 - current_amount_of_potions

    sql = "SELECT sku, quantity, r,g,b,d FROM barrel_table "
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    barrels = result.all()
    
    available_colors = {
        "r":0,
        "g":0,
        "b":0,
        "d":0
    }
    for barrel in barrels:
        if barrel.r == 100:
            available_colors["r"] += barrel.quantity
        elif barrel.g == 100:
            available_colors["g"] += barrel.quantity
        elif barrel.b == 100:
            available_colors["b"] += barrel.quantity
        elif barrel.d == 100:
            available_colors["d"] += barrel.quantity
        #TODO: sort by descending stock order (restock low stock first)
    bottle_list = []
    for bottle in bottles:
        if bottle.make_more == True and available_storage > 0 and bottle.quantity <= 30:
            rgbd = (bottle.r,bottle.g,bottle.b,bottle.d)
            potion_amounts = []
            if bottle.r > 0:
                potion_amounts.append(available_colors["r"] // bottle.r if bottle.r > 0 else 0)
            if bottle.g > 0:
                potion_amounts.append(available_colors["g"] // bottle.g if bottle.g > 0 else 0)
            if bottle.b > 0:
                potion_amounts.append(available_colors["b"] // bottle.b if bottle.b > 0 else 0)
            if bottle.d > 0:
                potion_amounts.append(available_colors["d"] // bottle.d if bottle.d > 0 else 0)
            max_amount = [number for number in potion_amounts]
            if len(max_amount) != 0:
                max_amount = min(max_amount)
                if max_amount > 0:
                    potion_quantity = min(max_amount,50,available_storage)
                    for i, color in enumerate(rgbd):
                        if color > 0:
                            match i:
                                case 0:
                                    available_colors["r"] -= potion_quantity * color
                                case 1:
                                    available_colors["g"] -= potion_quantity * color
                                case 2:
                                    available_colors["b"] -= potion_quantity * color
                                case 3:
                                    available_colors["d"] -= potion_quantity * color
                    bottle_info = {
                        "potion_type": [rgbd[0],rgbd[1],rgbd[2],rgbd[3]],
                        "quantity":potion_quantity

                    }
                    bottle_list.append(bottle_info)
                    available_storage -= potion_quantity

    return bottle_list
