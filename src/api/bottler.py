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
    
    quantity_check_sku = "SELECT quantity from bottle_table"
    with db.engine.begin() as connection:
        quantity_check = connection.execute(sqlalchemy.text(quantity_check_sku))
    quantity_check = quantity_check.all()
    current_amount_of_potions = 0
    for value in quantity_check:
        current_amount_of_potions += value[0]
    available_storage = 300 - current_amount_of_potions

    sql = "SELECT sku, quantity, r,g,b,d FROM barrel_table "
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    barrels = result.all()
    
    sql = "SELECT name, quantity, r,g,b,d FROM bottle_table "
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    bottles = result.all()
    
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
        
    max_potion_quantities = {}
    for bottle in bottles:
        rgbd = (bottle.r,bottle.g,bottle.b,bottle.d)
        potion_amounts = []
        potion_amounts.append(available_colors["r"] // bottle.r if bottle.r != 0 else 0)
        potion_amounts.append(available_colors["g"] // bottle.g if bottle.g != 0 else 0)
        potion_amounts.append(available_colors["b"] // bottle.b if bottle.b != 0 else 0)
        potion_amounts.append(available_colors["d"] // bottle.d if bottle.d != 0 else 0)
        non_zero_vals = [number for number in potion_amounts if number != 0]
        if len(non_zero_vals) != 0:
            max_potion_quantities[rgbd] = min(non_zero_vals)
            
        

# CONTINUE WORK HERE
    total_potions = 0
    for rgbd, max_quantity in max_potion_quantities.items():
        total_potions+= max_quantity
        
    if total_potions > available_storage:
        for rgbd, max_quantity in max_potion_quantities.items():
            max_potion_quantities[rgbd] = int(max_quantity * available_storage / total_potions)
            

    bottle_list = []
    for rgbd, max_quantity in max_potion_quantities.items():
        quantity = min(max_quantity, available_storage)
        if quantity > 0:
            bottle_info = {
                "potion_type": [rgbd[0],rgbd[1],rgbd[2],rgbd[3]],
                "quantity": quantity
            }
            bottle_list.append(bottle_info)
            available_storage -= quantity

    #TODO: change back
    return bottle_list
