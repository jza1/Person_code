from sqlalchemy.orm import Session
from . import models, schemas


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_cart_by_user(db: Session, user_id: int):
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()


def get_cart_item(db: Session, cart_id: int):
    return db.query(models.CartItem).filter(models.CartItem.id == cart_id).first()


def get_cart_item_by_user_and_product(db: Session, user_id: int, product_id: int):
    return db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == product_id
    ).first()


def add_to_cart(db: Session, cart_item: schemas.CartItemCreate):
    existing = get_cart_item_by_user_and_product(db, cart_item.user_id, cart_item.product_id)
    if existing:
        existing.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing)
        return existing
    db_cart = models.CartItem(**cart_item.dict())
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart


def update_cart_item(db: Session, cart_id: int, quantity: int):
    db_cart = get_cart_item(db, cart_id)
    if not db_cart:
        return None
    db_cart.quantity = quantity
    db.commit()
    db.refresh(db_cart)
    return db_cart


def delete_cart_item(db: Session, cart_id: int):
    db_cart = get_cart_item(db, cart_id)
    if not db_cart:
        return None
    db.delete(db_cart)
    db.commit()
    return db_cart


def get_orders_by_user(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()


def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def create_order(db: Session, user_id: int, items: list, total_price: float):
    db_order = models.Order(user_id=user_id, total_price=total_price, status="paid")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    for item in items:
        product = get_product(db, item.product_id)
        order_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price if product else 0
        )
        db.add(order_item)
    db.commit()
    return db_order
