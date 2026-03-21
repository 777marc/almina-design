# Almina Design Co. (Django Store)

A Django store application for military memorabilia with an authenticated admin inventory workflow.

## Features

- Public storefront page listing active in-stock memorabilia.
- Inventory model with category, SKU, era, condition, price, and stock quantity.
- Django Admin controls for inventory management.
- Authentication with login/logout routes.
- Staff-only inventory dashboard.

## Setup

1. Install dependencies:
   `pip install -r requirements.txt`
2. Apply migrations:
   `python manage.py migrate`
3. Load sample inventory data:
   `python manage.py loaddata sample_inventory`
4. Create an admin user:
   `python manage.py createsuperuser`
5. Run server:
   `python manage.py runserver`

## Main URLs

- `/` storefront
- `/accounts/login/` login
- `/inventory/` staff-only inventory dashboard
- `/admin/` Django admin inventory management

## Admin Inventory Management

After logging in to `/admin/`, use:

- `Store > Categories`
- `Store > Memorabilia items`

From there, admins can add/edit inventory and control stock levels and active visibility.

## Sample Data

The project includes a fixture at `store/fixtures/sample_inventory.json` with starter categories and memorabilia items for local development.
