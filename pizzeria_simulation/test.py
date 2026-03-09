#!/usr/bin/env python3
"""Quick test of models and serialization."""
from src.models import create_default_state
from src.utils.storage import state_to_dict, dict_to_state
import json

print("Testing pizzeria...\n")

# Test 1: Create state
print("1. Creating default state...")
state = create_default_state()
print(f"   next_id: {state.next_id}")
print(f"   Tables: {len(state.dining_hall.tables)}")
print(f"   Staff: {len(state.staff_team.employees)}")
print(f"   Menu items: {len(state.order_desk.menu.items)}")

# Test 2: Serialize to JSON
print("\n2. Serializing to JSON...")
data = state_to_dict(state)
print(f"   Keys: {list(data.keys())}")
print(f"   Menu items: {len(data['order_desk']['menu']['items'])}")

# Test 3: Deserialize from JSON
print("\n3. Deserializing from JSON...")
json_str = json.dumps(data, ensure_ascii=False, indent=2)
loaded_data = json.loads(json_str)
restored_state = dict_to_state(loaded_data)
print(f"   next_id: {restored_state.next_id}")
print(f"   Orders: {len(restored_state.orders)}")

# Test 4: Create order
print("\n4. Creating order...")
from src.models import Order, OrderItem, OrderType, OrderStatus

item = OrderItem(
    id=state.next_id,
    menu_item_id=1,
    quantity=2,
    unit_price=10.0,
    total_price=20.0
)
state.next_id += 1

order = Order(
    id=state.next_id,
    type=OrderType.ON_SITE,
    customer_phone=None,
    table_id=1,
    delivery_address=None,
    items=[item],
    status=OrderStatus.CREATED,
    created_at="2026-03-09T20:30:00",
    estimated_ready_time=None,
    total_price=20.0,
    tips_amount=0.0
)
state.next_id += 1
state.orders.append(order)
print(f"   Order #{order.id} created")
print(f"   Total: {order.total_price}r")
print(f"   Status: {order.status.value}")

# Test 5: Check enums
print("\n5. Checking enums...")
from src.enums import OrderType, OrderStatus, PaymentMethod, EmployeeRole

print(f"   OrderType.ON_SITE = {OrderType.ON_SITE.value}")
print(f"   OrderStatus.CREATED = {OrderStatus.CREATED.value}")
print(f"   PaymentMethod.CASH = {PaymentMethod.CASH.value}")
print(f"   EmployeeRole.COOK = {EmployeeRole.COOK.value}")

print("\nAll tests passed!")
