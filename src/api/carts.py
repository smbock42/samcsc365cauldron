import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    sql = "INSERT INTO cart_table (id) VALUES (DEFAULT) RETURNING id"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))

    first_row = result.first()
    cart_id = first_row[0]
    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    #TODO
    sql = f"SELECT EXISTS (SELECT 1 FROM cart_table WHERE id = {cart_id});"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    first_row = result.first()
    exists = first_row[0]
    return {exists}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    #TODO
    sql = f"SELECT EXISTS (SELECT 1 FROM cart_table WHERE id = {cart_id});"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    first_row = result.first()
    exists = first_row[0]
    if exists:
        sql = f"INSERT INTO cart_items ( cart_id, item_sku, quantity) VALUES ({cart_id}, '{item_sku}', {cart_item.quantity})"

        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql))

        return "OK"

    return f"No Active Cart for ID: {cart_id}"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    #TODO

    # get items from cart_id
    sql = f"SELECT item_sku, quantity from cart_items where cart_id = {cart_id}"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))

    #items = result.all()

    first_row = result.first()
    red_quantity
    


    # subtract potions and add gold


    #get cart_items


    # delete cart at the end
    sql = f"DELETE FROM cart_table where id = {cart_id}"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
    return {"total_potions_bought": 1, "total_gold_paid": 50}
