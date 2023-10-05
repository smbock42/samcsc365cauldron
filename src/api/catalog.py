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
    sql = "SELECT * FROM bottle_table"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))

    available_potions = []
    potions = result.all()
    for potion in potions:
        if potion.quantity > 0:
            potion_info = {
                "sku": potion.SKU,
                "name": potion.name,
                "quantity": potion.quantity,
                "price": potion.price,
                "potion_type": [potion.R, potion.B, potion.G, potion.D]

            }
            available_potions.append(potion_info)




    # Can return a max of 20 items.
    return available_potions
