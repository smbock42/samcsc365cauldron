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
    sql = sqlalchemy.text("INSERT INTO cart_table (customer_name) VALUES (:customer_name) RETURNING id")
    with db.engine.begin() as connection:
        result = connection.execute(statement=sql, parameters={"customer_name":new_cart.customer})
        cart_id = result.first()[0]
    return {"cart_id": cart_id}



@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    #TODO
    sql = "SELECT EXISTS (SELECT 1 FROM cart_table WHERE id = :cart_id);"
    with db.engine.begin() as connection:
        result = connection.execute(statement=sqlalchemy.text(sql),parameters={"cart_id":cart_id})
        exists = result.first()[0]
    return {exists}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    #TODO
    cart_exists_sql = "SELECT EXISTS (SELECT 1 FROM cart_table WHERE id = :cart_id);"
    with db.engine.begin() as connection:
        result = connection.execute(statement=sqlalchemy.text(cart_exists_sql),parameters={"cart_id":cart_id})
        cart_exists = result.first()[0]

        if cart_exists:
            item_exists_sql = "SELECT EXISTS (SELECT 1 FROM cart_items WHERE item_sku = :item_sku and cart_id = :cart_id);"
            result = connection.execute(statement=sqlalchemy.text(item_exists_sql),parameters={"item_sku":item_sku,"cart_id":cart_id})
            item_exists = result.first()[0]

            if item_exists:
                update_cart_sql = f"UPDATE cart_items SET quantity = :cart_item_quantity WHERE item_sku = ':item_sku' and cart_id = :cart_id"
                result = connection.execute(statement=sqlalchemy.text(update_cart_sql),parameters={"cart_item_quantity":cart_item.quantity,"item_sku":item_sku,"cart_id":cart_id})
            else:
                sql = f"INSERT INTO cart_items ( cart_id, item_sku, quantity) VALUES (:cart_id, :item_sku, :cart_item_quantity)"
                result = connection.execute(statement=sqlalchemy.text(sql),parameters={"cart_id":cart_id,"item_sku":item_sku,"cart_item_quantity":cart_item.quantity})

            return "OK"

    return f"No Active Cart for ID: {cart_id}"


class CartCheckout(BaseModel):
    payment: str
#TODO: Make Cases for Unit Tests Make StaleQuery DB class
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
    cart_sql = "SELECT customer_name, checked_out from cart_table where id = :cart_id"
    with db.engine.begin() as connection:
        cart_info = connection.execute(statement=sqlalchemy.text(cart_sql),parameters={"cart_id":cart_id})
        cart_info = cart_info.all()[0]
        customer_name = cart_info.customer_name
        total_potions_bought = 0
        total_gold_paid = 0
        if cart_info.checked_out == False:

            # get items from cart_id
            get_cart_items_sql = "SELECT item_sku, quantity from cart_items where cart_id = :cart_id"
            result = connection.execute(statement=sqlalchemy.text(get_cart_items_sql),parameters={"cart_id":cart_id})
            results = result.all()

            for result in results:
                item_sku = result[0]
                item_quantity = result[1]

                total_potions_bought += item_quantity
                #update potions/bottle_table                
                bottle_ledger_sql = "INSERT INTO bottle_ledger (type, description, sku, amount) VALUES ('Sold', :description, ':item_sku', :item_quantity)"
                connection.execute(statement=sqlalchemy.text(bottle_ledger_sql),parameters={"description":f"Sold {item_quantity} amount of {item_sku} to {customer_name}","item_sku":item_sku,"item_quantity":-item_quantity})
            
                #get cost of potion
                get_potion_sql = "SELECT price, r, g, b, d from bottle_table WHERE sku = ':item_sku'"
                potion = connection.execute(statement=sqlalchemy.text(get_potion_sql),parameters={"item_sku":item_sku})
                potion = potion.all()[0]
                price = potion.price
                #add ledger for deposit


                total_cost = price * item_quantity
                total_gold_paid += total_cost
                

                add_cash_ledger_sql = "INSERT INTO cash_ledger(type,description,amount) VALUES ('deposit',:description,:total_cost)"
                result = connection.execute(statement=sqlalchemy.text(add_cash_ledger_sql),parameters={"description":f"Customer: {customer_name} with cart_id: {cart_id} purchased {item_quantity} amount of {item_sku} for ${total_cost} at ${price} per barrel","total_cost":total_cost})


                purchase_history_sql = "INSERT INTO purchase_history(customer_name, potion_sku, quantity, price_per_unit, total_amount, r, g, b, d) VALUES (':customer_name', ':item_sku', :item_quantity, :price, :total_cost, :potion_r,:potion_g,:potion_b,:potion_d)"
                result = connection.execute(statement=sqlalchemy.text(purchase_history_sql),parameters={"customer_name":customer_name,"item_sku":item_sku,"item_quantity":item_quantity,"price":price,"total_cost":total_cost,"potion_r":potion.r,"potion_g":potion.g,"potion_b":potion.b,"potion_d":potion.d})



        #get cart_items


        # delete cart at the end
        # sql = f"DELETE FROM cart_table where id = {cart_id}"
        # with db.engine.begin() as connection:
        #     result = connection.execute(sqlalchemy.text(sql))
        
        # sql = f"DELETE FROM cart_items where cart_id = {cart_id}"
        # with db.engine.begin() as connection:
        #     result = connection.execute(sqlalchemy.text(sql))
        checked_out_cart_sql = "UPDATE cart_table SET checked_out = TRUE where id = :cart_id"
        result = connection.execute(statement=sqlalchemy.text(checked_out_cart_sql),parameters={"cart_id":cart_id})
    return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}
