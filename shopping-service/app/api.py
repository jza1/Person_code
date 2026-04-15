from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas
from .database import get_db
from .user_client import verify_user_exists

router = APIRouter()


def success_response(data=None):
    return {"code": 200, "message": "ok", "data": data}


@router.get("/api/products")
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return success_response([schemas.ProductResponse.from_orm(p) for p in products])


@router.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return success_response(schemas.ProductResponse.from_orm(product))


@router.post("/api/products")
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    created = crud.create_product(db=db, product=product)
    return success_response(schemas.ProductResponse.from_orm(created))


@router.get("/api/cart/{user_id}")
def get_cart(user_id: int, db: Session = Depends(get_db)):
    cart_items = crud.get_cart_by_user(db, user_id=user_id)
    result = []
    for item in cart_items:
        item_dict = schemas.CartItemResponse.from_orm(item).dict()
        product = crud.get_product(db, item.product_id)
        if product:
            item_dict["product"] = schemas.ProductResponse.from_orm(product)
        result.append(item_dict)
    return success_response(result)


@router.post("/api/cart")
def add_to_cart(cart_item: schemas.CartItemCreate, db: Session = Depends(get_db)):
    product = crud.get_product(db, cart_item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    added = crud.add_to_cart(db=db, cart_item=cart_item)
    return success_response(schemas.CartItemResponse.from_orm(added))


@router.put("/api/cart/{cart_id}")
def update_cart(cart_id: int, update: schemas.CartItemUpdate, db: Session = Depends(get_db)):
    updated = crud.update_cart_item(db, cart_id=cart_id, quantity=update.quantity)
    if updated is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return success_response(schemas.CartItemResponse.from_orm(updated))


@router.delete("/api/cart/{cart_id}")
def delete_cart_item(cart_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_cart_item(db, cart_id=cart_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return success_response(schemas.CartItemResponse.from_orm(deleted))


@router.post("/api/orders")
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    user_exists = await verify_user_exists(order.user_id)
    if not user_exists:
        raise HTTPException(status_code=400, detail="User not found")
    total_price = 0.0
    for item in order.items:
        product = crud.get_product(db, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        total_price += product.price * item.quantity
    created_order = crud.create_order(db, user_id=order.user_id, items=order.items, total_price=total_price)
    for item in order.items:
        cart_item = crud.get_cart_item_by_user_and_product(db, order.user_id, item.product_id)
        if cart_item:
            crud.delete_cart_item(db, cart_item.id)
    order_data = schemas.OrderResponse.from_orm(created_order)
    return success_response(order_data)


@router.get("/api/orders/{user_id}")
def get_orders(user_id: int, db: Session = Depends(get_db)):
    orders = crud.get_orders_by_user(db, user_id=user_id)
    result = []
    for order in orders:
        order_dict = schemas.OrderResponse.from_orm(order).dict()
        order_dict["items"] = [schemas.OrderItemResponse.from_orm(i) for i in order.items]
        result.append(order_dict)
    return success_response(result)


@router.get("/api/orders/detail/{order_id}")
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order_dict = schemas.OrderResponse.from_orm(order).dict()
    order_dict["items"] = [schemas.OrderItemResponse.from_orm(i) for i in order.items]
    return success_response(order_dict)
