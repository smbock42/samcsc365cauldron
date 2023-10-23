import sqlalchemy
from json import dumps
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
"""
[
  {
    "sku": "MEDIUM_GREEN_BARREL",
    "ml_per_barrel": 2500,
    "potion_type": [
      1,0,0,0
    ],
    "price": 250,
    "quantity": 5
  },
  {
    "sku": "MEDIUM_BLUE_BARREL",
    "ml_per_barrel": 2500,
    "potion_type": [
      0,1,0,0
    ],
    "price": 250,
    "quantity": 5
  }
]
"""
@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    #TODO
    print(barrels_delivered)
    for barrel in barrels_delivered:
        color = barrel.sku.split("_")[1].lower()
        total_cost = barrel.price*barrel.quantity

        # add cash_ledger
        add_cash_ledger_sql = f"INSERT INTO cash_ledger(type,description,amount) VALUES ('withdrawl','Purchased {barrel.quantity} amount of {barrel.sku} for ${total_cost} at ${barrel.price} per barrel',-{total_cost})"
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(add_cash_ledger_sql))
        


        # update barrel table
        update_barrel_sql = f"INSERT INTO barrel_ledger (type, sku, amount, description) VALUES ('Delivered', '{color}_barrel', {barrel.quantity*barrel.ml_per_barrel}, 'Delivered {barrel.quantity} {color}_barrel')"
        
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(update_barrel_sql))
    return "OK"

"""
[Barrel(sku='MEDIUM_RED_BARREL', ml_per_barrel=2500, potion_type=[1, 0, 0, 0], price=250, quantity=10), Barrel(sku='SMALL_RED_BARREL', ml_per_barrel=500, potion_type=[1, 0, 0, 0], price=100, quantity=10), Barrel(sku='MEDIUM_GREEN_BARREL', ml_per_barrel=2500, potion_type=[0, 1, 0, 0], price=250, quantity=10), Barrel(sku='SMALL_GREEN_BARREL', ml_per_barrel=500, potion_type=[0, 1, 0, 0], price=100, quantity=10), Barrel(sku='MEDIUM_BLUE_BARREL', ml_per_barrel=2500, potion_type=[0, 0, 1, 0], price=300, quantity=10), Barrel(sku='SMALL_BLUE_BARREL', ml_per_barrel=500, potion_type=[0, 0, 1, 0], price=120, quantity=10), Barrel(sku='MINI_RED_BARREL', ml_per_barrel=200, potion_type=[1, 0, 0, 0], price=60, quantity=1), Barrel(sku='MINI_GREEN_BARREL', ml_per_barrel=200, potion_type=[1, 0, 0, 0], price=60, quantity=1), Barrel(sku='MINI_BLUE_BARREL', ml_per_barrel=200, potion_type=[1, 0, 0, 0], price=60, quantity=1)]
"""

"""
[{"sku":"MEDIUM_RED_BARREL", "ml_per_barrel":2500, "potion_type":[1, 0, 0, 0], "price":250, "quantity":10}, {"sku":"SMALL_RED_BARREL", "ml_per_barrel":500, "potion_type":[1, 0, 0, 0], "price":100, "quantity":10},{"sku":"MEDIUM_GREEN_BARREL", "ml_per_barrel":2500, "potion_type":[0, 1, 0, 0], "price":250, "quantity":10},{"sku":"SMALL_GREEN_BARREL", "ml_per_barrel":500, "potion_type":[0, 1, 0, 0], "price":100, "quantity":10},{"sku":"MEDIUM_BLUE_BARREL", "ml_per_barrel":2500, "potion_type":[0, 0, 1, 0], "price":300, "quantity":10},{"sku":"SMALL_BLUE_BARREL", "ml_per_barrel":500, "potion_type":[0, 0, 1, 0], "price":120, "quantity":10},{"sku":"MINI_RED_BARREL", "ml_per_barrel":200, "potion_type":[1, 0, 0, 0], "price":60, "quantity":1},{"sku":"MINI_GREEN_BARREL", "ml_per_barrel":200, "potion_type":[1, 0, 0, 0], "price":60, "quantity":1},{"sku":"MINI_BLUE_BARREL", "ml_per_barrel":200, "potion_type":[1, 0, 0, 0], "price":60, "quantity":1}]
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
    wholesale_catalog_list = []
    for barrel in wholesale_catalog:
        barrel_info = {
            "sku":barrel.sku,
            "ml_per_barrel":barrel.ml_per_barrel,
            "potion_type":barrel.potion_type,
            "price":barrel.price,
            "quantity":barrel.quantity

        }
        wholesale_catalog_list.append(barrel_info)
    barrel_catalog_json = dumps(wholesale_catalog_list)
    sql = f"INSERT INTO barrel_catalog_schedule(barrel_catalog) VALUES ('{barrel_catalog_json}')"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
        
    sql = "SELECT bottle_table.name,bottle_table.sku,bottle_table.price,bottle_table.r,bottle_table.g,bottle_table.b,bottle_table.d,bottle_table.make_more,COALESCE(SUM(bottle_ledger.amount),0)AS quantity FROM bottle_table LEFT JOIN bottle_ledger ON bottle_table.sku=bottle_ledger.sku GROUP BY bottle_table.name,bottle_table.sku,bottle_table.price,bottle_table.r,bottle_table.g,bottle_table.b,bottle_table.d,bottle_table.make_more ORDER BY quantity ASC;"
    restock_quantity = 15
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))


    #TODO: check balance of barrel ml when purchasing barrels. Change formula to take this into account

    #get result of SQL
    potions = result.all()
    #TODO: hash into table with r,g,b,d values instead of potion name
    potion_restock_dict = {}
    
    catalog_list = []  
    
    #find potions less than the desired restock quantity
    for potion in potions:
        rgbd_arr = (potion.r,potion.g,potion.b,potion.d)
        if rgbd_arr not in potion_restock_dict and int(potion.quantity) <=restock_quantity:
            potion_restock_dict[rgbd_arr] = True
            for barrel in wholesale_catalog:
                if potion.r > 0 and "RED" in barrel.sku and barrel not in catalog_list:
                    catalog_list.append(barrel)
                if potion.g > 0 and "GREEN" in barrel.sku and barrel not in catalog_list:
                    catalog_list.append(barrel)
                if potion.b > 0 and "BLUE" in barrel.sku and barrel not in catalog_list:
                    catalog_list.append(barrel)
                if potion.d > 0 and "DARK" in barrel.sku and barrel not in catalog_list:
                    catalog_list.append(barrel)
    


        

    sql = "SELECT SUM(amount) from cash_ledger"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    first_row = result.first()
    gold = first_row[0]
    
    # Calculate the total amount of gold required to purchase all of the barrels.
    total_gold_required = 0
    for barrel in catalog_list:
        total_gold_required += barrel.price * barrel.quantity

    # If there is enough gold to purchase all of the barrels, return the full list of barrels and the remaining gold.
    purchase_list = []
    if total_gold_required <= gold:
        for barrel in catalog_list:
            barrel_info = {
                "sku":barrel.sku,
                "quantity":barrel.quantity
            }
            purchase_list.append(barrel_info)
        # TODO: change back later
        return purchase_list

    # Otherwise, greedily purchase the most efficient barrels until we run out of gold.
    remaining_gold = gold

    # Sort the barrels by price per milliliter.
    catalog_list.sort(key=lambda barrel: barrel.price / barrel.ml_per_barrel)

    # Iterate over the sorted barrels and purchase as many as we can afford.
    for barrel in catalog_list:
        if barrel.price <= remaining_gold:
            
            potential_quantity = min(remaining_gold // barrel.price, barrel.quantity)
            barrel_info = {
                "sku":barrel.sku,
                "quantity":potential_quantity
            }
            purchase_list.append(barrel_info)
            remaining_gold -= barrel.price * potential_quantity
    #TODO: change this back
    return purchase_list



