from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# -----------------------
# DATA
# -----------------------
products = [
    {"id": 1, "name": "Casual Shirt", "brand": "Zara", "category": "Shirt", "price": 1200, "sizes_available": ["S","M","L"], "in_stock": True},
    {"id": 2, "name": "Denim Jeans", "brand": "Levis", "category": "Jeans", "price": 2000, "sizes_available": ["M","L"], "in_stock": True},
    {"id": 3, "name": "Running Shoes", "brand": "Nike", "category": "Shoes", "price": 3000, "sizes_available": ["8","9","10"], "in_stock": False},
    {"id": 4, "name": "Summer Dress", "brand": "H&M", "category": "Dress", "price": 1500, "sizes_available": ["S","M"], "in_stock": True},
    {"id": 5, "name": "Leather Jacket", "brand": "Puma", "category": "Jacket", "price": 4000, "sizes_available": ["M","L"], "in_stock": True},
    {"id": 6, "name": "Formal Shirt", "brand": "Allen Solly", "category": "Shirt", "price": 1800, "sizes_available": ["S","M","L"], "in_stock": False},

    # 🆕 Accessories
    {"id": 7, "name": "Luxury Perfume", "brand": "Dior", "category": "Perfume", "price": 5500, "sizes_available": ["100ml"], "in_stock": True},
    {"id": 8, "name": "Casual Cap", "brand": "Adidas", "category": "Cap", "price": 800, "sizes_available": ["Free Size"], "in_stock": True},
    {"id": 9, "name": "Analog Watch", "brand": "Fossil", "category": "Watch", "price": 7000, "sizes_available": ["Standard"], "in_stock": True},
    {"id": 10, "name": "Leather Belt", "brand": "Gucci", "category": "Belt", "price": 6000, "sizes_available": ["M","L"], "in_stock": False},
    {"id": 11, "name": "Sports Watch", "brand": "Casio", "category": "Watch", "price": 3500, "sizes_available": ["Standard"], "in_stock": True},
    {"id": 12, "name": "Premium Perfume", "brand": "Chanel", "category": "Perfume", "price": 7500, "sizes_available": ["50ml","100ml"], "in_stock": True},

    # 🆕 Kids Wear
    {"id": 13, "name": "Kids T-Shirt", "brand": "Mothercare", "category": "Kids Wear", "price": 700, "sizes_available": ["XS","S"], "in_stock": True},
    {"id": 14, "name": "Kids Jeans", "brand": "Gap Kids", "category": "Kids Wear", "price": 1200, "sizes_available": ["XS","S","M"], "in_stock": True},

    # 🆕 Jewelry
    {"id": 15, "name": "Gold Plated Necklace", "brand": "Tanishq Style", "category": "Jewelry", "price": 5000, "sizes_available": ["Standard"], "in_stock": True},
    {"id": 16, "name": "Gold Plated Bracelet", "brand": "Malabar Gold", "category": "Jewelry", "price": 3500, "sizes_available": ["Standard"], "in_stock": False},

    # 🆕 Sneaker Series
    {"id": 17, "name": "Air Max Series Shoes", "brand": "Nike", "category": "Sneaker Series", "price": 8000, "sizes_available": ["8","9","10"], "in_stock": True},
    {"id": 18, "name": "Ultraboost Series Shoes", "brand": "Adidas", "category": "Sneaker Series", "price": 9000, "sizes_available": ["8","9"], "in_stock": True}
]

orders = []
wishlist = []
order_counter = 1

# -----------------------
# MODELS
# -----------------------
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    size: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0, le=10)
    delivery_address: str = Field(..., min_length=10)
    gift_wrap: bool = False
    season_sale: bool = False

class NewProduct(BaseModel):
    name: str = Field(..., min_length=2)
    brand: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    sizes_available: List[str]
    in_stock: bool = True

# -----------------------
# HELPERS
# -----------------------
def find_product(product_id):
    for p in products:
        if p["id"] == product_id:
            return p
    return None

def calculate_order_total(price, quantity, gift_wrap, season_sale):
    base = price * quantity
    season_discount = 0
    bulk_discount = 0

    if season_sale:
        season_discount = 0.15 * base

    if quantity >= 5:
        bulk_discount = 0.05 * base

    gift_charge = 50 * quantity if gift_wrap else 0

    total = base - season_discount - bulk_discount + gift_charge

    return {
        "base_price": base,
        "season_discount": season_discount,
        "bulk_discount": bulk_discount,
        "gift_charge": gift_charge,
        "final_total": total
    }

# -----------------------
# Q1
# -----------------------
@app.get("/")
def home():
    return {"message": "Welcome to TrendZone Fashion Store"}

# -----------------------
# Q2
# -----------------------
@app.get("/products")
def get_products():
    return {
        "total_products": len(products),
        "in_stock": len([p for p in products if p["in_stock"]]),
        "out_of_stock": len([p for p in products if not p["in_stock"]])
    }

# -----------------------
# Q5
# -----------------------
@app.get("/products/summary")
def product_summary():
    brands = list(set([p["brand"] for p in products]))
    categories = {}

    for p in products:
        categories[p["category"]] = categories.get(p["category"], 0) + 1

    return {
        "total_products": len(products),
        "in_stock": len([p for p in products if p["in_stock"]]),
        "out_of_stock": len([p for p in products if not p["in_stock"]]),
        "brands": brands,
        "category_count": categories
    }

# -----------------------
# Q10 FILTER
# -----------------------
@app.get("/products/filter")
def filter_products(category: Optional[str] = None, brand: Optional[str] = None,
                    max_price: Optional[int] = None, in_stock: Optional[bool] = None):

    result = products

    if category is not None:
        result = [p for p in result if p["category"] == category]

    if brand is not None:
        result = [p for p in result if p["brand"] == brand]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return {"total_results": len(result), "products": result}

# -----------------------
# Q11 POST PRODUCT
# -----------------------
@app.post("/products", status_code=201)
def add_product(product: NewProduct):
    for p in products:
        if p["name"].lower() == product.name.lower() and p["brand"].lower() == product.brand.lower():
            raise HTTPException(status_code=400, detail="Product already exists")

    new_product = {"id": len(products)+1, **product.dict()}
    products.append(new_product)

    return {"message": "Product added", "product": new_product}

# -----------------------
# Q3 GET BY ID
# -----------------------
@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# -----------------------
# Q4 ORDERS
# -----------------------
@app.get("/orders")
def get_orders():
    return {
        "total_orders": len(orders),
        "total_revenue": sum(o["total_cost"] for o in orders),
        "orders": orders
    }

# -----------------------
# Q8 POST ORDER
# -----------------------
@app.post("/orders")
def place_order(order: OrderRequest):
    global order_counter

    product = find_product(order.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail="Out of stock")

    if order.size not in product["sizes_available"]:
        raise HTTPException(status_code=400, detail=f"Available sizes: {product['sizes_available']}")

    bill = calculate_order_total(product["price"], order.quantity, order.gift_wrap, order.season_sale)

    new_order = {
        "order_id": order_counter,
        "customer_name": order.customer_name,
        "product_name": product["name"],
        "brand": product["brand"],
        "size": order.size,
        "quantity": order.quantity,
        "total_cost": bill["final_total"]
    }

    orders.append(new_order)
    order_counter += 1

    return {"order": new_order, "bill": bill}

# -----------------------
# Q12 UPDATE
# -----------------------
@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if price is not None:
        product["price"] = price
    if in_stock is not None:
        product["in_stock"] = in_stock

    return {"message": "Updated", "product": product}

# -----------------------
# Q13 DELETE
# -----------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for o in orders:
        if o["product_name"] == product["name"]:
            raise HTTPException(status_code=400, detail="Cannot delete product with orders")

    products.remove(product)
    return {"message": "Deleted"}

# -----------------------
# Q14 WISHLIST ADD
# -----------------------
@app.post("/wishlist/add")
def add_to_wishlist(customer_name: str, product_id: int, size: str):

    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if size not in product["sizes_available"]:
        raise HTTPException(status_code=400, detail=f"Available sizes: {product['sizes_available']}")

    for item in wishlist:
        if item["customer_name"] == customer_name and item["product_id"] == product_id and item["size"] == size:
            raise HTTPException(status_code=400, detail="Already in wishlist")

    wishlist.append({
        "customer_name": customer_name,
        "product_id": product_id,
        "product_name": product["name"],
        "price": product["price"],
        "size": size
    })

    return {"message": "Added to wishlist"}

# -----------------------
# Q14 GET WISHLIST
# -----------------------
@app.get("/wishlist")
def get_wishlist():
    return {
        "total_items": len(wishlist),
        "total_value": sum(i["price"] for i in wishlist),
        "wishlist": wishlist
    }

# -----------------------
# Q15 REMOVE
# -----------------------
@app.delete("/wishlist/remove")
def remove_from_wishlist(customer_name: str, product_id: int):
    for item in wishlist:
        if item["customer_name"] == customer_name and item["product_id"] == product_id:
            wishlist.remove(item)
            return {"message": "Removed"}

    raise HTTPException(status_code=404, detail="Not found")

# -----------------------
# Q15 ORDER ALL
# -----------------------
@app.post("/wishlist/order-all")
def order_all(customer_name: str, delivery_address: str):
    global order_counter

    items = [i for i in wishlist if i["customer_name"] == customer_name]

    if not items:
        raise HTTPException(status_code=400, detail="No items in wishlist")

    total = 0
    new_orders = []

    for item in items:
        product = find_product(item["product_id"])

        bill = calculate_order_total(product["price"], 1, False, False)

        order = {
            "order_id": order_counter,
            "customer_name": customer_name,
            "product_name": product["name"],
            "quantity": 1,
            "total_cost": bill["final_total"]
        }

        orders.append(order)
        new_orders.append(order)
        total += bill["final_total"]
        order_counter += 1

    wishlist[:] = [w for w in wishlist if w["customer_name"] != customer_name]

    return {"orders": new_orders, "grand_total": total}
# -----------------------
# Q16 - PRODUCTS SEARCH
# -----------------------
@app.get("/products/search")
def search_products(keyword: str):

    keyword = keyword.lower()

    results = [
        p for p in products
        if keyword in p["name"].lower()
        or keyword in p["brand"].lower()
        or keyword in p["category"].lower()
    ]

    if not results:
        return {
            "message": "No products found",
            "total_found": 0,
            "products": []
        }

    return {
        "total_found": len(results),
        "products": results
    }


# -----------------------
# Q17 - PRODUCTS SORT
# -----------------------
@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):

    valid_fields = ["price", "name", "brand", "category"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Order must be asc or desc")

    reverse = True if order == "desc" else False

    sorted_products = sorted(products, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }


# -----------------------
# Q18 - PRODUCTS PAGINATION
# -----------------------
@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 3):

    total_items = len(products)
    total_pages = (total_items + limit - 1) // limit

    if page < 1 or page > total_pages:
        raise HTTPException(status_code=400, detail="Invalid page number")

    start = (page - 1) * limit
    end = start + limit

    data = products[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "products": data
    }


# -----------------------
# Q19 - ORDERS SEARCH
# -----------------------
@app.get("/orders/search")
def search_orders(customer_name: str):

    results = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not results:
        return {
            "message": "No orders found",
            "total_found": 0,
            "orders": []
        }

    return {
        "total_found": len(results),
        "orders": results
    }


# -----------------------
# Q19 - ORDERS SORT
# -----------------------
@app.get("/orders/sort")
def sort_orders(sort_by: str = "total_cost", order: str = "asc"):

    valid_fields = ["total_cost", "quantity"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Order must be asc or desc")

    reverse = True if order == "desc" else False

    sorted_orders = sorted(orders, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "orders": sorted_orders
    }


# -----------------------
# Q19 - ORDERS PAGINATION
# -----------------------
@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):

    total_items = len(orders)
    total_pages = (total_items + limit - 1) // limit

    if page < 1 or page > total_pages:
        raise HTTPException(status_code=400, detail="Invalid page")

    start = (page - 1) * limit
    end = start + limit

    data = orders[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "orders": data
    }


# -----------------------
# Q20 - FINAL BROWSE API
# -----------------------
@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    in_stock: Optional[bool] = None,
    max_price: Optional[int] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):

    result = products

    # 🔍 SEARCH
    if keyword is not None:
        keyword = keyword.lower()
        result = [
            p for p in result
            if keyword in p["name"].lower()
            or keyword in p["brand"].lower()
            or keyword in p["category"].lower()
        ]

    # 🎯 FILTER
    if category is not None:
        result = [p for p in result if p["category"] == category]

    if brand is not None:
        result = [p for p in result if p["brand"] == brand]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    # 🔄 SORT
    valid_fields = ["price", "name", "brand", "category"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    # 📄 PAGINATION
    total_items = len(result)
    total_pages = (total_items + limit - 1) // limit

    if page < 1 or (total_pages > 0 and page > total_pages):
        raise HTTPException(status_code=400, detail="Invalid page")

    start = (page - 1) * limit
    end = start + limit

    paginated = result[start:end]

    return {
        "total_results": total_items,
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
        "products": paginated
    }
