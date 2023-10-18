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
    print(new_cart)
    print(new_cart.customer)
    #TODO: add customer info here
    sql = f"INSERT INTO cart_table (id,customer_name) VALUES (DEFAULT,'{new_cart.customer}') RETURNING id"
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
    #TODO Check for sku 
    """
    TODO
    
    Change SQL to this:

    UPDATE catalog
    SET inventory = catalog.inventory - cart_items.quantity
    FROM cart_items
    WHERE catalog.id = cart_items.catalog_id and cart_items.cart_id = :cart_id;
    """
    customer_name_sql = f"SELECT customer_name from cart_items where cart_id = {cart_id}"
    with db.engine.begin() as connection:
        customer_name = connection.execute(sqlalchemy.text(customer_name_sql))
    customer_name = customer_name.first()[0]


    # get items from cart_id
    sql = f"SELECT item_sku, quantity from cart_items where cart_id = {cart_id}"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))

    #items = result.all()
    total_potions_bought = 0
    total_gold_paid = 0
    results = result.all()
    for result in results:
        item_sku = result[0]
        item_quantity = result[1]

        total_potions_bought += item_quantity
        #update potions/bottle_table
        sql = f"UPDATE bottle_table SET quantity = quantity - {item_quantity} WHERE sku = '{item_sku}'"
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(sql))
    
        #get cost of potion
        sql = f"SELECT price, r, g, b, d from bottle_table WHERE sku = '{item_sku}'"
        with db.engine.begin() as connection:
            potion = connection.execute(sqlalchemy.text(sql))
        potion = potion.all()
        price = potion.price
        #add ledger for deposit


        total_cost = price * item_quantity
        total_gold_paid += total_cost
        

        add_cash_ledger_sql = f"INSERT INTO cash_ledger(type,description,amount,balance) VALUES ('deposit','Customer: {customer_name} with cart_id: {cart_id} purchased {item_quantity} amount of {item_sku} for ${total_cost} at ${price} per barrel',{total_cost},{total_cost} + SELECT SUM(amount) from cash_ledger"
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(add_cash_ledger_sql))


        purchase_history_sql = f"INSERT INTO purchase_history(customer_name, potion_sku, quantity, price_per_unit, total_amount, r, g, b, d) VALUES ({customer_name}, {item_sku}, {item_quantity}, {price}, {total_cost}, {potion.r},{potion.g},{potion.b},{potion.d})"
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(purchase_history_sql))



    #get cart_items


    # delete cart at the end
    # sql = f"DELETE FROM cart_table where id = {cart_id}"
    # with db.engine.begin() as connection:
    #     result = connection.execute(sqlalchemy.text(sql))
    
    # sql = f"DELETE FROM cart_items where cart_id = {cart_id}"
    # with db.engine.begin() as connection:
    #     result = connection.execute(sqlalchemy.text(sql))
    return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}
