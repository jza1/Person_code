from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 100, category: str = None, search: str = None):
    query = db.query(models.Product)
    if category and category != "全部":
        query = query.filter(models.Product.category == category)
    if search:
        query = query.filter(
            or_(
                models.Product.name.contains(search),
                models.Product.description.contains(search)
            )
        )
    return query.offset(skip).limit(limit).all()


def get_categories(db: Session):
    products = db.query(models.Product).all()
    categories = list(set([p.category for p in products if p.category]))
    categories.sort()
    return ["全部"] + categories


def get_hot_products(db: Session, limit: int = 10):
    return db.query(models.Product).filter(
        models.Product.is_hot == 1
    ).order_by(
        models.Product.sales.desc()
    ).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    db.delete(db_product)
    db.commit()
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


def get_all_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()


def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def create_order(db: Session, user_id: int, items: list, total_price: float, address_data: dict = None):
    # 先检查并扣减库存，同时增加销量
    for item in items:
        product = get_product(db, item.product_id)
        if not product:
            raise ValueError(f"商品 {item.product_id} 不存在")
        if product.stock < item.quantity:
            raise ValueError(f"商品 {product.name} 库存不足，当前库存: {product.stock}")
        product.stock -= item.quantity
        product.sales += item.quantity  # 增加销量

    db_order = models.Order(user_id=user_id, total_price=total_price, status="paid")
    if address_data:
        db_order.address_name = address_data.get("name")
        db_order.address_phone = address_data.get("phone")
        db_order.address_province = address_data.get("province")
        db_order.address_city = address_data.get("city")
        db_order.address_district = address_data.get("district")
        db_order.address_detail = address_data.get("detail")
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


def get_favorites_by_user(db: Session, user_id: int):
    return db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()


def get_favorite(db: Session, user_id: int, product_id: int):
    return db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.product_id == product_id
    ).first()


def add_favorite(db: Session, favorite: schemas.FavoriteCreate):
    existing = get_favorite(db, favorite.user_id, favorite.product_id)
    if existing:
        return existing
    db_favorite = models.Favorite(**favorite.dict())
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


def remove_favorite(db: Session, user_id: int, product_id: int):
    db_favorite = get_favorite(db, user_id, product_id)
    if not db_favorite:
        return None
    db.delete(db_favorite)
    db.commit()
    return db_favorite


def remove_favorite_by_id(db: Session, favorite_id: int):
    db_favorite = db.query(models.Favorite).filter(models.Favorite.id == favorite_id).first()
    if not db_favorite:
        return None
    db.delete(db_favorite)
    db.commit()
    return db_favorite


def get_messages_by_user(db: Session, user_id: int, other_user_id: int = None):
    query = db.query(models.Message).filter(
        (models.Message.from_user_id == user_id) | (models.Message.to_user_id == user_id)
    )
    if other_user_id:
        query = query.filter(
            (models.Message.from_user_id == other_user_id) | (models.Message.to_user_id == other_user_id)
        )
    return query.order_by(models.Message.created_at.asc()).all()


def get_unread_count(db: Session, user_id: int):
    return db.query(models.Message).filter(
        models.Message.to_user_id == user_id,
        models.Message.is_read == 0
    ).count()


def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def mark_as_read(db: Session, message_id: int):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message:
        db_message.is_read = 1
        db.commit()
        db.refresh(db_message)
    return db_message


def mark_conversation_as_read(db: Session, user_id: int, other_user_id: int):
    db.query(models.Message).filter(
        models.Message.from_user_id == other_user_id,
        models.Message.to_user_id == user_id,
        models.Message.is_read == 0
    ).update({"is_read": 1})
    db.commit()


def get_conversation_users(db: Session, user_id: int):
    messages = db.query(models.Message).filter(
        (models.Message.from_user_id == user_id) | (models.Message.to_user_id == user_id)
    ).all()
    user_ids = set()
    for msg in messages:
        if msg.from_user_id != user_id:
            user_ids.add(msg.from_user_id)
        if msg.to_user_id != user_id:
            user_ids.add(msg.to_user_id)
    return list(user_ids)
