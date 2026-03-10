# API прикладного сервиса

Сценарии (`use-cases`) `PizzeriaService`:

- `create_dine_in_order(...)`
- `create_delivery_order(...)`
- `confirm_order(order_id)`
- `send_order_to_kitchen(order_id)`
- `tick_kitchen(minutes)`
- `start_delivery(order_id)`
- `tick_delivery(minutes)`
- `pay_order(order_id)`
- `complete_order(order_id)`
- `cancel_order(order_id)`
- `list_orders()`
- `list_active_orders()`
- `list_orders_for_confirmation()`
- `list_orders_for_kitchen()`
- `list_orders_in_kitchen()`
- `list_ready_and_completed_orders()`
- `list_ready_for_delivery()`
- `list_active_deliveries()`
- `list_arrived_delivery_unpaid()`
- `list_orders_for_payment()`
- `list_orders_for_completion()`
- `list_free_tables()`
- `suggest_table(guests_count)`
- `list_employees()`
- `set_employee_active(employee_id, active)`
- `finance_report()`
- `snapshot()`
