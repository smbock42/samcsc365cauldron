import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """
    with db.engine.begin() as connection:
        sql = "SELECT purchase_history.created_at as timestamp, purchase_history.customer_name as customer_name, purchase_history.potion_sku as potion_sku, purchase_history.quantity as line_item_total, purchase_history.total_amount as total_amount, bottle_table.name as potion_name FROM purchase_history LEFT JOIN bottle_table ON bottle_table.sku = purchase_history.potion_sku"
        print(f"customer_name: {customer_name}\npotion_sku: {potion_sku}\nsearch_page: {search_page}\nsort_col: {sort_col.value}\nsort_order: {sort_order.value}")
        sort_col = sort_col.value
        sort_order = sort_order.value
        if customer_name != "" and potion_sku != "":
            sql += f" WHERE customer_name ILIKE :customer_name AND potion_sku ILIKE :potion_sku"
        elif customer_name != "":
            sql += f" WHERE customer_name ILIKE :customer_name"
        elif potion_sku != "":
            sql += f" WHERE potion_sku ILIKE :potion_sku"
        
        sql += f" ORDER BY {sort_col} {sort_order}"

        parameters = {
            "customer_name":f"{customer_name}%",
            "potion_sku":f"{potion_sku}%",
        }
        #print(sql)
        results = connection.execute(statement=sqlalchemy.text(sql),parameters=parameters)
    results = results.all()
    print("full_results: ", results)
    print("search_page: ",search_page)
    if search_page == "":
        search_page = 0
    search_page = int(search_page)
    offset = search_page * 5
    page_results = results[offset:offset+5]

    previous = "" if search_page == 0 else search_page -1
    next = "" if offset + 5 >= len(results) else search_page + 1
    results = [{"line_item_id":i, "item_sku":f"{item.line_item_total} {item.potion_sku}", "customer_name": {item.customer_name},"line_item_total":{item.total_amount}, "timestamp":{item.timestamp}} for i, item in enumerate(page_results)]
    print(f"previous: {previous}\nnext: {next}\nresults: {results}")
    return {
        "previous": previous,
        "next": next,
        "results": results,
    }


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
        parameters={
            "customer_name":new_cart.customer
        }
        result = connection.execute(statement=sql, parameters=parameters)
        cart_id = result.first()[0]
    return {"cart_id": cart_id}



@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    #TODO
    sql = "SELECT EXISTS (SELECT 1 FROM cart_table WHERE id = :cart_id);"
    with db.engine.begin() as connection:
        parameters={
            "cart_id":cart_id
        }
        result = connection.execute(statement=sqlalchemy.text(sql),parameters=parameters)
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
        parameters={
            "cart_id":cart_id
        }
        result = connection.execute(statement=sqlalchemy.text(cart_exists_sql),parameters=parameters)
        cart_exists = result.first()[0]

        if cart_exists:
            item_exists_sql = "SELECT EXISTS (SELECT 1 FROM cart_items WHERE item_sku = :item_sku and cart_id = :cart_id);"
            parameters={
                "item_sku":item_sku,
                "cart_id":cart_id
            }
            result = connection.execute(statement=sqlalchemy.text(item_exists_sql),parameters=parameters)
            item_exists = result.first()[0]

            if item_exists:
                update_cart_sql = f"UPDATE cart_items SET quantity = :cart_item_quantity WHERE item_sku = :item_sku and cart_id = :cart_id"
                parameters={
                    "cart_item_quantity":cart_item.quantity,
                    "item_sku":item_sku,
                    "cart_id":cart_id
                    }
                result = connection.execute(statement=sqlalchemy.text(update_cart_sql),parameters=parameters)
            else:
                sql = f"INSERT INTO cart_items ( cart_id, item_sku, quantity) VALUES (:cart_id, :item_sku, :cart_item_quantity)"
                parameters={
                    "cart_id":cart_id,
                    "item_sku":item_sku,
                    "cart_item_quantity":cart_item.quantity
                }
                result = connection.execute(statement=sqlalchemy.text(sql),parameters=parameters)

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
        parameters={
            "cart_id":cart_id
            }
        cart_info = connection.execute(statement=sqlalchemy.text(cart_sql),parameters=parameters)
        cart_info = cart_info.all()[0]
        customer_name = cart_info.customer_name
        total_potions_bought = 0
        total_gold_paid = 0
        if cart_info.checked_out == False:

            # get items from cart_id
            get_cart_items_sql = "SELECT item_sku, quantity from cart_items where cart_id = :cart_id"
            parameters={
                "cart_id":cart_id
            }
            result = connection.execute(statement=sqlalchemy.text(get_cart_items_sql),parameters=parameters)
            results = result.all()

            for result in results:
                item_sku = result[0]
                item_quantity = result[1]

                total_potions_bought += item_quantity
                #update potions/bottle_table                
                bottle_ledger_sql = "INSERT INTO bottle_ledger (type, description, sku, amount) VALUES ('Sold', :description, :item_sku, :item_quantity)"
                parameters={
                    "description":f"Sold {item_quantity} amount of {item_sku} to {customer_name}",
                    "item_sku":item_sku,
                    "item_quantity":-item_quantity
                }
                connection.execute(statement=sqlalchemy.text(bottle_ledger_sql),parameters=parameters)
            
                #get cost of potion
                get_potion_sql = "SELECT price, r, g, b, d from bottle_table WHERE sku = :item_sku"
                parameters={
                    "item_sku":item_sku
                }
                potion = connection.execute(statement=sqlalchemy.text(get_potion_sql),parameters=parameters)
                potion = potion.all()[0]
                price = potion.price
                #add ledger for deposit


                total_cost = price * item_quantity
                total_gold_paid += total_cost
                

                add_cash_ledger_sql = "INSERT INTO cash_ledger(type,description,amount) VALUES ('deposit',:description,:total_cost)"
                parameters={
                    "description":f"Customer: {customer_name} with cart_id: {cart_id} purchased {item_quantity} amount of {item_sku} for ${total_cost} at ${price} per barrel",
                    "total_cost":total_cost}
                result = connection.execute(statement=sqlalchemy.text(add_cash_ledger_sql),parameters=parameters)


                purchase_history_sql = "INSERT INTO purchase_history(customer_name, potion_sku, quantity, price_per_unit, total_amount, r, g, b, d) VALUES (:customer_name, :item_sku, :item_quantity, :price, :total_cost, :potion_r,:potion_g,:potion_b,:potion_d)"
                parameters={
                    "customer_name":customer_name,
                    "item_sku":item_sku,
                    "item_quantity":item_quantity,
                    "price":price,
                    "total_cost":total_cost,
                    "potion_r":potion.r,
                    "potion_g":potion.g,
                    "potion_b":potion.b,
                    "potion_d":potion.d
                }
                result = connection.execute(statement=sqlalchemy.text(purchase_history_sql),parameters=parameters)



        #get cart_items


        # delete cart at the end
        # sql = f"DELETE FROM cart_table where id = {cart_id}"
        # with db.engine.begin() as connection:
        #     result = connection.execute(sqlalchemy.text(sql))
        
        # sql = f"DELETE FROM cart_items where cart_id = {cart_id}"
        # with db.engine.begin() as connection:
        #     result = connection.execute(sqlalchemy.text(sql))
        checked_out_cart_sql = "UPDATE cart_table SET checked_out = TRUE where id = :cart_id"
        parameters={
            "cart_id":cart_id
        }
        result = connection.execute(statement=sqlalchemy.text(checked_out_cart_sql),parameters=parameters)
    return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}
