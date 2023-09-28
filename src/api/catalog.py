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
    print(first_row)
    num_red_potions = first_row[0]
    print(num_red_potions)


    # Can return a max of 20 items.

    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": num_red_potions,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
