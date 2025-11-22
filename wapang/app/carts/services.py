from typing import Annotated
from fastapi import Depends

from wapang.app.users.models import User
from wapang.app.carts.models import CartProduct
from wapang.app.carts.repositories import CartRepository
from wapang.app.carts.schemas import *
from wapang.app.carts.exceptions import *
from wapang.app.orders.models import Order, OrderProduct, OrderStatus
from wapang.app.orders.repositories import OrderRepository
from wapang.app.orders.schemas import OrderDetails, OrderItems
from wapang.app.items.models import Product
from wapang.app.items.repositories import ItemRepository


class CartService:
    def __init__(
        self, 
        cart_repository: Annotated[CartRepository, Depends()], 
        item_repository: Annotated[ItemRepository, Depends()],
        order_repository: Annotated[OrderRepository, Depends()] 
    ) -> None:
        self.cart_repository = cart_repository
        self.item_repository = item_repository
        self.order_repository = order_repository

    async def update_cart(
        self, request: CartProductRequest, user: User
    ) -> tuple[dict[str, CartDetails], int]:
        
        item = await self.item_repository.get_item_by_id(request.item_id)
        if not item:
            raise ItemNotFoundException()
        
        cart_product = await self.cart_repository.get_cart_product(user.id, request.item_id)
        
        if request.quantity > 0:
            if cart_product:
                cart_product.count = request.quantity
                await self.cart_repository.session.flush()
            else:
                new_cart_product = CartProduct(
                    count=request.quantity, 
                    product_id=request.item_id, 
                    user_id=user.id
                )
                await self.cart_repository.add(new_cart_product)
        elif request.quantity == 0:
            if cart_product:
                await self.cart_repository.delete(cart_product)
        else:
            raise InvalidFieldFormatException()

    
        all_cart_products = await self.cart_repository.get_all_cart_products_with_details(user.id)
        
        stores_data = {}
        for cp in all_cart_products:
            product = cp.product
            store = product.store
            
            if store.id not in stores_data:
                stores_data[store.id] = CartDetails(
                    store_id=str(store.id),
                    store_name=store.store_name,
                    delivery_fee=store.delivery_fee,
                    store_total_price=store.delivery_fee,
                    items=[]
                )
            
            subtotal = product.price * cp.count
            stores_data[store.id].items.append(
                CartItems(
                    item_id=str(product.id),
                    item_name=product.name,
                    price=product.price,
                    quantity=cp.count,
                    subtotal=subtotal
                )
            )
            stores_data[store.id].store_total_price += subtotal
        

        total_price = sum(store.store_total_price for store in stores_data.values())
        
        return stores_data, total_price
    
    async def get_cart(self, user: User) -> tuple[dict[str, CartDetails], int]:

        all_cart_products = await self.cart_repository.get_all_cart_products_with_details(user.id)
        
        if not all_cart_products:
            return {}, 0
        
        stores_data = {}
        for cp in all_cart_products:
            product = cp.product
            store = product.store
            
            if store.id not in stores_data:
                stores_data[store.id] = CartDetails(
                    store_id=str(store.id),
                    store_name=store.store_name,
                    delivery_fee=store.delivery_fee,
                    store_total_price=store.delivery_fee,
                    items=[]
                )
            
            subtotal = product.price * cp.count
            stores_data[store.id].items.append(
                CartItems(
                    item_id=str(product.id),
                    item_name=product.name,
                    price=product.price,
                    quantity=cp.count,
                    subtotal=subtotal
                )
            )
            stores_data[store.id].store_total_price += subtotal
        
        total_price = sum(store.store_total_price for store in stores_data.values())
        
        return stores_data, total_price
    
    async def clear_cart(self, user: User) -> None:
        await self.cart_repository.delete_all_cart_products(user.id)
        
    async def checkout(self, user: User) -> tuple[Order, dict[str, OrderDetails]]:
        all_cart_products = await self.cart_repository.get_all_cart_products_with_details(user.id)
        
        if not all_cart_products:
            raise EmptyItemListException()

        stores_data: dict[str, OrderDetails] = {}
        products_to_update: list[Product] = []
        for cp in all_cart_products:
            product = cp.product
            store = product.store
            
            if product.stock < cp.count:
                raise NotEnoughStockException()
            
            if store.id not in stores_data:
                stores_data[store.id] = OrderDetails(
                    store_id=str(store.id),
                    store_name=store.store_name,
                    delivery_fee=store.delivery_fee,
                    store_total_price=store.delivery_fee,
                    items=[]
                )
            
            subtotal = product.price * cp.count
            stores_data[store.id].items.append(
                OrderItems(
                    item_id=str(product.id),
                    item_name=product.name,
                    price=product.price,
                    quantity=cp.count,
                    subtotal=subtotal
                )
            )
            stores_data[store.id].store_total_price += subtotal
            
            product.stock -= cp.count
            products_to_update.append(product)

        total_price = sum(store.store_total_price for store in stores_data.values())

        new_order = Order(
            status=OrderStatus.ORDERED,
            total_price=total_price,
            user_id=user.id
        )

        self.order_repository.session.add(new_order)
        self.order_repository.session.add_all(products_to_update)
        
        await self.order_repository.session.flush()
        
        order_products_to_save: list[OrderProduct] = []
        for cp in all_cart_products:
            order_products_to_save.append(
                OrderProduct(
                    order_id=new_order.id,
                    product_id=cp.product_id,
                    quantity=cp.count
                )
            )
        
        self.order_repository.session.add_all(order_products_to_save)
        
        await self.cart_repository.delete_all_cart_products(user.id)
        
        return new_order, stores_data