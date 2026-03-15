from fastapi import FastAPI, HTTPException

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 120, "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "in_stock": True}
]

cart = []
orders = []
order_counter = 1


@app.get("/products")
def get_products():
    return {"products": products}


@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["total_price"] = item["price"] * item["quantity"]
            return {"message": "Cart updated", "cart_item": item}

    cart_item = {
        "product_id": product_id,
        "name": product["name"],
        "price": product["price"],
        "quantity": quantity,
        "total_price": product["price"] * quantity
    }

    cart.append(cart_item)

    return {"message": "Item added to cart", "cart_item": cart_item}


@app.get("/cart")
def view_cart():

    grand_total = sum(item["total_price"] for item in cart)

    return {
        "cart_items": cart,
        "grand_total": grand_total
    }


@app.delete("/cart/{product_id}")
def remove_item(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    raise HTTPException(status_code=404, detail="Item not in cart")


@app.post("/cart/checkout")
def checkout(customer_name: str, delivery_address: str):

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    created_orders = []

    for item in cart:
        order = {
            "order_id": len(orders) + 1,
            "customer_name": customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": delivery_address
        }

        orders.append(order)
        created_orders.append(order)

    cart.clear()

    return {
        "orders_placed": len(created_orders),
        "orders": created_orders
    }


@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }
