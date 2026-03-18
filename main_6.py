from fastapi import FastAPI, HTTPException,Query

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Accessories", "in_stock": True},
    {"id": 2, "name": "USB-C Charger", "price": 899, "category": "Accessories", "in_stock": True},
    {"id": 3, "name": "Bluetooth Speaker", "price": 1499, "category": "Audio", "in_stock": True},
    {"id": 4, "name": "Phone Stand", "price": 299, "category": "Accessories", "in_stock": False},
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Accessories", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 3499, "category": "Accessories", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1999, "category": "Electronics", "in_stock": True}
]

cart = []
orders = []
order_counter = 1


@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f'{product["name"]} is out of stock')

    # update quantity if item already exists
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["unit_price"] * item["quantity"]

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "unit_price": product["price"],
        "quantity": quantity,
        "subtotal": product["price"] * quantity
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }


@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }
@app.get("/orders/search")
def search_orders(customer_name: str):

    results = [
        order for order in orders
        if customer_name.lower() in order["customer_name"].lower()
    ]

    if not results:
        return {
            "message": f"No orders found for: {customer_name}"
        }

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f'{item["product_name"]} removed from cart'}

    raise HTTPException(status_code=404, detail="Item not found in cart")


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
@app.delete("/orders/{order_id}")
def delete_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            orders.remove(order)
            return {"message": f"Order {order_id} deleted successfully"}

    raise HTTPException(status_code=404, detail="Order not found")
@app.get("/products/search")
def search_products(keyword: str):

    results = [
        product for product in products
        if keyword.lower() in product["name"].lower()
    ]

    if not results:
        return {"message": f"No products found for: {keyword}"}

    return {
        "products": results,
        "total_found": len(results)
    }
@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):

    if sort_by not in ["price", "name"]:
        raise HTTPException(
            status_code=400,
            detail="sort_by must be 'price' or 'name'"
        )

    reverse = True if order == "desc" else False

    sorted_products = sorted(
        products,
        key=lambda x: x[sort_by],
        reverse=reverse
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }
@app.get("/products/sort-by-category")
def sort_by_category():

    sorted_products = sorted(
        products,
        key=lambda x: (x["category"], x["price"])
    )

    return {
        "products": sorted_products
    }
@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):

    start = (page - 1) * limit
    end = start + limit

    paginated_products = products[start:end]

    total_products = len(products)
    total_pages = (total_products + limit - 1) // limit  # ceiling division

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "products": paginated_products
    }

@app.get("/products/browse")
def browse_products(
    keyword: str = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):

    result = products.copy()

    # 🔍 1. FILTER (Search)
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p["name"].lower()
        ]

    # ⚠️ If no results after search
    if keyword and not result:
        return {
            "message": f"No products found for: {keyword}"
        }

    # 🔄 2. SORT
    if sort_by not in ["price", "name"]:
        raise HTTPException(
            status_code=400,
            detail="sort_by must be 'price' or 'name'"
        )

    reverse = True if order == "desc" else False

    result = sorted(
        result,
        key=lambda x: x[sort_by],
        reverse=reverse
    )

    # 📄 3. PAGINATION
    total_found = len(result)
    total_pages = (total_found + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    paginated_result = result[start:end]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total_found,
        "total_pages": total_pages,
        "products": paginated_result
    }
@app.get("/orders/page")
def get_orders_paged(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    
    # Optional: handle empty orders
    if not orders:
        return {"message": "No orders available"}

    start = (page - 1) * limit

    return {
        "page": page,
        "limit": limit,
        "total": len(orders),
        "total_pages": -(-len(orders) // limit),  # ceiling division
        "orders": orders[start: start + limit],
    }
