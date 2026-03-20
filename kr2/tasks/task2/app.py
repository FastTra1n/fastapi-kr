from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

product_1 = {
    "product_id": 123,
    "name": "Smartphone",
    "category": "Electronics",
    "price": 599.99
}

product_2 = {
    "product_id": 456,
    "name": "Phone Case",
    "category": "Accessories",
    "price": 19.99
}

product_3 = {
    "product_id": 789,
    "name": "Iphone",
    "category": "Electronics",
    "price": 1299.99
}

product_4 = {
    "product_id": 101,
    "name": "Headphones",
    "category": "Accessories",
    "price": 99.99
}

product_5 = {
    "product_id": 202,
    "name": "Smartwatch",
    "category": "Electronics",
    "price": 299.99
}

products = [product_1, product_2, product_3, product_4, product_5]


@app.get('/product/{product_id}')
async def get_product(product_id: int):
    for product in products:
        if product['product_id'] == product_id:
            return product
    else:
        raise HTTPException(
            status_code=404, detail="Product with entered id was not found")


@app.get('/products/search')
async def get_searched_product(
    keyword: str = Query(...),
    category: str | None = Query(''),
    limit: int | None = Query(10, le=100),
):
    return list(filter(lambda p: keyword.lower() in p["name"].lower() and category.lower() in p['category'].lower(), products))[:limit]
