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
        add_cash_ledger_sql = f"INSERT INTO cash_ledger(type,description,amount,balance) VALUES ('withdrawl','Purchased {barrel.quantity} amount of {color}_potions for ${total_cost} at ${barrel.price} per barrel',-{total_cost},-{total_cost} + COALESCE((SELECT balance FROM cash_ledger ORDER BY id DESC LIMIT 1), 0))"
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(add_cash_ledger_sql))
        
        #update global gold variable based on most recent ledger
        update_global_gold = f"UPDATE global_values SET gold = (SELECT balance FROM cash_ledger WHERE id = (SELECT MAX(id) FROM cash_ledger))"
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(update_global_gold))

        # update barrel table
        update_barrel_sql = f"UPDATE barrel_table SET quantity = quantity + {barrel.quantity*barrel.ml_per_barrel} WHERE sku = '{color}_barrel'"
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
    sql = "SELECT * FROM bottle_table"
    restock_quantity = 15
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    #get result of SQL
    potions = result.all()
    potion_restock_dict = {
        "Red Potion":False,
        "Green Potion":False,
        "Blue Potion":False
    }
    
    #find potions less than the desired restock quantity
    for potion in potions:
        if potion.quantity <= restock_quantity:
            potion_restock_dict[potion.name] = True

    # go through wholesale_catalog and sort by color to see how much to buy of each color
    catalog_list = []
    for barrel in wholesale_catalog:
        if "RED" in barrel.sku and potion_restock_dict["Red Potion"] == True:
            catalog_list.append(barrel)
        elif "GREEN" in barrel.sku and potion_restock_dict["Green Potion"] == True:
            catalog_list.append(barrel)
        elif "BLUE" in barrel.sku and potion_restock_dict["Blue Potion"] == True:
            catalog_list.append(barrel)

        

    sql = "SELECT gold FROM global_values"
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
        return purchase_list

    # Otherwise, greedily purchase the most efficient barrels until we run out of gold.
    remaining_gold = gold

    # Sort the barrels by price per milliliter.
    wholesale_catalog.sort(key=lambda barrel: barrel.price / barrel.ml_per_barrel)

    # Iterate over the sorted barrels and purchase as many as we can afford.
    for barrel in wholesale_catalog:
        if barrel.price <= remaining_gold:
            
            potential_quantity = min(remaining_gold / barrel.price, barrel.quantity)
            barrel_info = {
                "sku":barrel.sku,
                "quantity":potential_quantity
            }
            purchase_list.append(barrel_info)
            remaining_gold -= barrel.price * potential_quantity

    return purchase_list



