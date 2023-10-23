import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    #TODO Reset carts

    reset_cash_ledger_sql = f"INSERT INTO cash_ledger(type,description,amount,balance) VALUES ('reset','Reset Store - gold set to $100 and potions/barrels set to 0',100,100)"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(reset_cash_ledger_sql))
    
    #update global gold variable based on most recent ledger
    update_global_gold = f"UPDATE global_values SET gold = (SELECT balance FROM cash_ledger WHERE id = (SELECT MAX(id) FROM cash_ledger))"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(update_global_gold))

    #reset bottle_table
    sql = "DELETE FROM bottle_ledger"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))

    #reset barrel_table
    sql = "DELETE FROM barrel_ledger"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))

    #reset carts
    sql = "DELETE FROM cart_items"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))

    sql = "DELETE FROM cart_table"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """
    return {
        "shop_name": "Apothecary of Wonders",
        "shop_owner": "Sam Bock",
    }

