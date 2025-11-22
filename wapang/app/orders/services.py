from typing import Annotated
from fastapi import Depends

from wapang.app.users.models import User
from wapang.app.orders.models import Order, OrderProduct, OrderStatus
from wapang.app.orders.repositories import OrderRepository
from wapang.app.orders.schemas import *
from wapang.app.orders.exceptions import *
from wapang.app.items.repositories import ItemRepository


class OrderService:
    def __init__(self, order_repository: Annotated[OrderRepository, Depends()], product_repository: Annotated[ItemRepository, Depends()]) -> None:
        self.order_repository = order_repository
        self.product_repository = product_repository

    async def create_order(self, request: OrderCreateRequest, user: User) -> tuple[Order, dict[str, OrderDetails]]:
        if not request.items:
            raise EmptyItemListException()
        
        item_ids = [item.item_id for item in request.items]
        products = await self.product_repository.get_items_by_ids(item_ids)
        
        request_map = {item.item_id: item.quantity for item in request.items}
        
        if len(products) != len(item_ids):
            raise ItemNotFoundException()
        
        stores_data = {}
        total_price = 0
        
        for product in products:
            item_id_str = str(product.id)
            quantity = request_map[item_id_str]
            
            if quantity < 1:
                raise InvalidFieldFormatException()

            if product.stock < quantity:
                raise NotEnoughStockException()

            subtotal = product.price * quantity
            store = product.store

            if store.id not in stores_data:
                stores_data[store.id] = OrderDetails(
                    store_id=str(store.id),
                    store_name=store.store_name,
                    delivery_fee=store.delivery_fee,
                    store_total_price=store.delivery_fee,
                    items=[]
                )
            
            stores_data[store.id].items.append(OrderItems(
                item_id=item_id_str,
                item_name=product.name,
                price=product.price,
                quantity=quantity,
                subtotal=subtotal
            ))
            stores_data[store.id].store_total_price += subtotal
        
        total_price = sum(store.store_total_price for store in stores_data.values())
        
        new_order = Order(
            status=OrderStatus.ORDERED, 
            total_price=total_price, 
            user_id=user.id
        )

        self.order_repository.session.add(new_order)
        
        products_to_update = []
        for product in products:
            quantity = request_map[str(product.id)]
            
            product.stock -= quantity
            products_to_update.append(product)
            
        self.order_repository.session.add_all(products_to_update)

        await self.order_repository.session.flush()

        order_products_to_save = []
        for product in products:
            quantity = request_map[str(product.id)]
            
            order_products_to_save.append(OrderProduct(
                order_id=new_order.id,
                product_id=product.id,
                quantity=quantity
            ))

        self.order_repository.session.add_all(order_products_to_save)

        return new_order, stores_data
    
    async def get_order(self, order_id: str, user: User) -> tuple[Order, dict[str, OrderDetails]]:
        order = await self.order_repository.get_order_by_id(order_id)
        
        if not order:
            raise OrderNotFoundException()
        if order.user_id != user.id:
            raise NotYourOrderException()
            
        order_products = await self.order_repository.get_order_products_with_details(order_id)
        
        stores_data = {}
        for op in order_products:
            product = op.product
            store = product.store
            
            if store.id not in stores_data:
                stores_data[store.id] = OrderDetails(
                    store_id=str(store.id),
                    store_name=store.store_name,
                    delivery_fee=store.delivery_fee,
                    store_total_price=store.delivery_fee,
                    items=[]
                )
                
            subtotal = product.price * op.quantity
            stores_data[store.id].items.append(OrderItems(
                item_id=str(product.id),
                item_name=product.name,
                price=product.price,
                quantity=op.quantity,
                subtotal=subtotal
            ))
            stores_data[store.id].store_total_price += subtotal
        
        return order, stores_data
    
    async def update_order(self, order_id: str, request: OrderPatchRequest, user: User) -> tuple[Order, dict[str, OrderDetails]]:
        order = await self.order_repository.get_order_by_id(order_id)
        if not order:
            raise OrderNotFoundException()
        if order.user_id != user.id:
            raise NotYourOrderException()
        if order.status != OrderStatus.ORDERED:
            raise InvalidOrderStatusException()
            
        objects_to_save = [order]

        if request.status == OrderStatus.CANCELED:
            order.status = OrderStatus.CANCELED

            order_products = await self.order_repository.get_order_products_for_restock(order_id)
            for op in order_products:
                if op.product:
                    op.product.stock += op.quantity
                    objects_to_save.append(op.product)        
        elif request.status == OrderStatus.COMPLETE:
            order.status = OrderStatus.COMPLETE 
        else:
            raise InvalidFieldFormatException() 
        
        await self.order_repository.add_objects_to_session(objects_to_save)
        
        order_products = await self.order_repository.get_order_products_with_details(order_id)
        
        stores_data = {}
        for op in order_products:
            product = op.product
            store = product.store
            
            if store.id not in stores_data:
                stores_data[store.id] = OrderDetails(
                    store_id=str(store.id),
                    store_name=store.store_name,
                    delivery_fee=store.delivery_fee,
                    store_total_price=store.delivery_fee,
                    items=[]
                )
                
            subtotal = product.price * op.quantity
            stores_data[store.id].items.append(OrderItems(
                item_id=str(product.id),
                item_name=product.name,
                price=product.price,
                quantity=op.quantity,
                subtotal=subtotal
            ))
            stores_data[store.id].store_total_price += subtotal
            
        return order, stores_data