# PR Title
`feat: add order create/cancel/update + stock update with sqlite compatibility migration`

# What Changed
- Added order management capabilities:
  - Create order: `POST /api/orders/create`
  - Cancel order: `POST /api/orders/cancel`
  - Update order items: `PATCH /api/orders/update-items`
- Added stock update capability:
  - Update stock: `PATCH /api/stock/update`
- Extended data model:
  - `orders.city` column
  - New `order_items` table and relations
- Extended agent intents:
  - `order_create`, `order_cancel`, `order_update`, `stock_update`
- Added SQLite compatibility migration on startup:
  - Auto-add `city` column for legacy local `orders` table
- Added regression tests for migration + order/stock flows.

# Why
- Moves backend from read-only support flow into actionable operations.
- Prevents startup failures on existing developer databases where `orders.city` is missing.

# Risk / Impact
- Database schema change (`orders.city`, `order_items`) affects all environments.
- Safe for legacy local SQLite due to startup migration.
- No API removal; only additive changes.

# Test Plan
1. Install test dependency:
   - `cd backend && pip install -r requirements-dev.txt`
2. Run tests:
   - `pytest -q`
3. Manual API checks from Swagger:
   - `POST /api/orders/create`
   - `PATCH /api/orders/update-items`
   - `POST /api/orders/cancel`
   - `PATCH /api/stock/update`

# Reviewer Notes
- Migration is intentionally lightweight and scoped to SQLite local DBs.
- For production-grade rollout, adding Alembic migrations is recommended in a follow-up.
