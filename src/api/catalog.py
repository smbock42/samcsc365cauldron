import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    #working - Oct 5th. 
    sql = "SELECT bottle_table.name, bottle_table.sell_in_catalog, bottle_table.sku, bottle_table.price, bottle_table.r, bottle_table.g, bottle_table.b, bottle_table.d, bottle_table.make_more, SUM(bottle_ledger.amount) AS quantity FROM bottle_table INNER JOIN bottle_ledger ON bottle_table.sku = bottle_ledger.sku GROUP BY bottle_table.name, bottle_table.sku, bottle_table.price, bottle_table.sell_in_catalog, bottle_table.r, bottle_table.g, bottle_table.b, bottle_table.d, bottle_table.make_more ORDER BY quantity ASC;"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
        available_potions = []
        potions = result.all()
    for potion in potions:
        if potion.quantity > 0 and potion.sell_in_catalog == True:
            potion_info = {
                "sku": potion.sku,
                "name": potion.name,
                "quantity": potion.quantity,
                "price": potion.price,
                "potion_type": [potion.r, potion.g, potion.b, potion.d]

            }
            available_potions.append(potion_info)


    #TODO: return max of 20 items. 

    # Can return a max of 20 items.
    return available_potions
