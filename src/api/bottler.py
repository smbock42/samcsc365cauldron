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
        sql = f"UPDATE barrel_table SET quantity = quantity - {potion.quantity*100} WHERE r= {potion.potion_type[0]} AND g = {potion.potion_type[1]} AND b = {potion.potion_type[2]} AND d = {potion.potion_type[3]}"
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql))
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
    results = result.all()
    bottle_list = []
    for result in results:
        #TODO: Change this when I want to start mixing potions
        quantity = result.quantity//100
        if quantity > available_storage:
            quantity = available_storage
        
        available_storage -= quantity 
        if quantity != 0:
            bottle_info = {
                "potion_type":[result.r,result.g,result.b,result.d],
                "quantity":quantity
            }
            bottle_list.append(bottle_info)
    return bottle_list
