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
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            #update barrel_table (ml)
            #TODO: change from 100 when mixing colors
            sku_sql = f"SELECT sku FROM bottle_table WHERE r = :r and g = :g and b = :b and d = :d"
            parameters={
                "r":potion.potion_type[0],
                "g":potion.potion_type[1],
                "b":potion.potion_type[2],
                "d":potion.potion_type[3]
            }
            sku = connection.execute(statement=sqlalchemy.text(sku_sql),parameters=parameters)
            sku = sku.first()[0]    
            
            if potion.potion_type[0] > 0:
                rsql = "INSERT INTO barrel_ledger (type, sku, amount, description) VALUES ('Bottled', 'red_barrel', :amount, :description)"
                parameters = {
                    "amount":-(potion.quantity *potion.potion_type[0]),
                    "description":f"Bottled {potion.quantity} {sku} ({potion.potion_type})"
                }
                result = connection.execute(statement=sqlalchemy.text(rsql),parameters=parameters)
            if potion.potion_type[1] > 0:
                gsql = f"INSERT INTO barrel_ledger (type, sku, amount, description) VALUES ('Bottled', 'green_barrel', :amount, :description)"
                parameters = {
                    "amount": -(potion.quantity * potion.potion_type[1]),
                    "description": f"Bottled {potion.quantity} {sku} ({potion.potion_type})"
                }
                result = connection.execute(statement=sqlalchemy.text(gsql),parameters=parameters)
            if potion.potion_type[2] > 0:
                bsql = f"INSERT INTO barrel_ledger (type, sku, amount, description) VALUES ('Bottled', 'blue_barrel', :amount, :description)"
                parameters = {
                    "amount": -(potion.quantity * potion.potion_type[2]),
                    "description": f"Bottled {potion.quantity} {sku} ({potion.potion_type})"
                }
                result = connection.execute(statement=sqlalchemy.text(bsql), parameters=parameters)
            if potion.potion_type[3] > 0:
                dsql = f"INSERT INTO barrel_ledger (type, sku, amount, description) VALUES ('Bottled', 'dark_barrel', :amount, :description)"
                parameters = {
                    "amount": -(potion.quantity * potion.potion_type[3]),
                    "description": f"Bottled {potion.quantity} {sku} ({potion.potion_type})"
                }
                result = connection.execute(statement=sqlalchemy.text(dsql),parameters=parameters)
            
            
            # update bottle_table (potions)
            sql = f"INSERT INTO bottle_ledger (type, description, sku, amount) VALUES ('Delivered', :description, :sku, :amount)"
            parameters = {
                "description": f"Delivered {potion}",
                "sku": sku,
                "amount":potion.quantity
            }
            result = connection.execute(statement=sqlalchemy.text(sql),parameters=parameters)
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
    with db.engine.begin() as connection:
    
        quantity_check_sku = "SELECT bottle_table.name,bottle_table.sku,bottle_table.price,bottle_table.r,bottle_table.g,bottle_table.b,bottle_table.d,bottle_table.make_more,COALESCE(SUM(bottle_ledger.amount),0)AS quantity FROM bottle_table LEFT JOIN bottle_ledger ON bottle_table.sku=bottle_ledger.sku GROUP BY bottle_table.name,bottle_table.sku,bottle_table.price,bottle_table.r,bottle_table.g,bottle_table.b,bottle_table.d,bottle_table.make_more ORDER BY quantity ASC;"
        quantity_check = connection.execute(statement=sqlalchemy.text(quantity_check_sku))
        bottles = quantity_check.all()
        current_amount_of_potions = 0
        for value in bottles:
            current_amount_of_potions += int(value.quantity)
        available_storage = 300 - current_amount_of_potions

        sql = "SELECT barrel_table.sku, barrel_table.r, barrel_table.g, barrel_table.b, barrel_table.d, SUM(barrel_ledger.amount) AS quantity FROM barrel_table INNER JOIN barrel_ledger ON barrel_table.sku = barrel_ledger.sku GROUP BY barrel_table.sku, barrel_table.r, barrel_table.g, barrel_table.b, barrel_table.d ORDER BY quantity ASC;"
        result = connection.execute(statement=sqlalchemy.text(sql))
        barrels = result.all()
        
    available_colors = {
        "r":0,
        "g":0,
        "b":0,
        "d":0
    }
    for barrel in barrels:
        if barrel.r == 100:
            available_colors["r"] += int(barrel.quantity)
        elif barrel.g == 100:
            available_colors["g"] += int(barrel.quantity)
        elif barrel.b == 100:
            available_colors["b"] += int(barrel.quantity)
        elif barrel.d == 100:
            available_colors["d"] += int(barrel.quantity)
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
                    current_quantity = 50 - int(bottle.quantity) if 50 - int(bottle.quantity) > 0 else 0
                    potion_quantity = min(max_amount,current_quantity,available_storage)
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
