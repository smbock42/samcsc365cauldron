import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    #done
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))

    first_row = result.first()
    num_red_potions = first_row[0]



    # Can return a max of 20 items.
    if num_red_potions == 0: 
        return []
    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": num_red_potions,
                "price": 75,
                "potion_type": [100, 0, 0, 0],
            }
        ]
