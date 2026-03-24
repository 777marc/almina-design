# Almina Design Co. (Django Store)

A modern Django store application for military memorabilia featuring Stripe Checkout integration, responsive e-commerce UI, and staff inventory management.

## Features

**Store & Storefront**

- Public storefront with category filtering and product grid layout.
- Product detail pages with full item information (era, condition, inventory status).
- Session-based shopping cart with add/remove functionality.
- Modern, responsive UI with smooth animations and accessibility.

**Payments**

- Stripe Checkout Session integration for secure card processing.
- EasyPost USPS live rate quote during checkout.
- Webhook-based payment confirmation (no polling).
- Order payment tracking (unpaid, paid, failed, refunded).
- Automatic inventory decrement on successful payment.
- Payment failure handling with retry workflow.

**Inventory & Admin**

- Category and memorabilia item models with SKU tracking.
- Django Admin interface for full CRUD operations.
- Staff-only inventory dashboard with low-stock alerts.
- Order management with payment and fulfillment status.
- Real-time inventory sync with SKU, era, condition, and pricing.

**Configuration & Security**

- Environment-based settings using python-dotenv (no hardcoded secrets).
- Support for development and production deployments.
- CSRF protection and secure webhook signature verification.
- Session-managed cart (no user registration required).

## Quick Start

### 1. Clone and Install Dependencies

```bash
git clone <repo-url> almina-design
cd almina-design
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your settings:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Django
DEBUG=True
SECRET_KEY=your-django-secret-key-here  (keep default for development)

# Stripe (from https://dashboard.stripe.com/test/apikeys)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...  (from Stripe CLI, see below)

# Stripe Configuration
STRIPE_CURRENCY=usd

# Site
SITE_URL=http://127.0.0.1:8000

# EasyPost (USPS shipping rates)
EASYPOST_API_KEY=EZAK_test_...
EASYPOST_ORIGIN_NAME=Almina Design Co.
EASYPOST_ORIGIN_STREET1=123 Warehouse St
EASYPOST_ORIGIN_STREET2=
EASYPOST_ORIGIN_CITY=Norfolk
EASYPOST_ORIGIN_STATE=VA
EASYPOST_ORIGIN_ZIP=23510
EASYPOST_ORIGIN_COUNTRY=US

# Default parcel used for quotes
EASYPOST_PARCEL_LENGTH_IN=10
EASYPOST_PARCEL_WIDTH_IN=8
EASYPOST_PARCEL_HEIGHT_IN=2
EASYPOST_PARCEL_WEIGHT_OZ=16
```

**Important:** `.env` is git-ignored; never commit API keys.

### 3. Initialize Database

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata store/fixtures/sample_inventory.json
```

### 4. Run Development Server

**Terminal 1** (Django server):

```bash
python manage.py runserver
```

**Terminal 2** (Stripe webhook forwarding, requires Stripe CLI):

```bash
stripe listen --forward-to localhost:8000/payments/stripe/webhook/
```

Visit http://127.0.0.1:8000 to see the storefront.

## Routes & Pages

### Customer Pages

- **`/`** — Storefront with category filtering and product grid
- **`/item/<slug>/`** — Product detail page with images, pricing, stock status
- **`/cart/`** — Shopping cart summary with add/remove controls
- **`/checkout/`** — Checkout form and Stripe Checkout Session creation
- **`/checkout/success/`** — Redirect target after Stripe completes payment
- **`/checkout/cancel/`** — User cancelled payment, return to cart option
- **`/order/<id>/confirmation/`** — Order confirmation with item summary (shown after successful payment)
- **`/accounts/login/`** — Staff login for admin features
- **`/accounts/logout/`** — Logout

### Admin/Staff Pages

- **`/inventory/`** — Staff-only inventory dashboard with low-stock alerts (requires login)
- **`/admin/`** — Django admin panel for full CRUD on categories, items, orders

### API/Webhooks

- **`/payments/stripe/webhook/`** — Stripe webhook endpoint for payment confirmation
  - Verifies webhook signature
  - Marks order as paid and confirmed
  - Decrements inventory on success
  - Idempotent (safe to retry)

## Admin Inventory & Order Management

### Django Admin (`/admin/`)

After creating a superuser and logging in, access:

**Store > Categories**

- Add/edit product categories (e.g., Patches, Medals, Uniforms)
- Auto-slug generation for URLs

**Store > Memorabilia Items**

- Create and manage inventory
- Edit name, SKU, price, quantity, images, era, condition
- Mark items as active/inactive
- Inline editing: price, stock quantity, status

**Store > Orders**

- View all orders with customer name, email, order date
- Track payment status: unpaid, paid, failed, refunded
- Track fulfillment status: pending, confirmed, shipped, cancelled
- View item breakdown and totals
- See Stripe session ID and payment intent ID for debugging

### Staff Inventory Dashboard (`/inventory/`)

Requires staff login. Shows:

- All items sorted by last updated
- Low-stock alerts (≤2 units)
- Quick summary of inventory levels
- Link to full Django Admin for editing

## Testing Stripe Payments

### Test Cards

Stripe provides test card numbers for development:

| Card Number           | Exp             | CVC          | Description             |
| --------------------- | --------------- | ------------ | ----------------------- |
| `4242 4242 4242 4242` | Any future date | Any 3 digits | Successful payment      |
| `4000 0000 0000 0002` | Any future date | Any 3 digits | Card declined           |
| `5555 5555 5555 4444` | Any future date | Any 3 digits | Visa card (alternative) |

### Local Webhook Testing

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Authenticate: `stripe login`
3. Forward webhooks:
   ```bash
   stripe listen --forward-to localhost:8000/payments/stripe/webhook/
   ```
4. Copy the `whsec_...` webhook secret and add to `.env` as `STRIPE_WEBHOOK_SECRET`
5. Complete a test checkout to trigger the webhook

The webhook will:

- Verify the Stripe signature for security
- Mark the order as paid/confirmed
- Decrement product inventory
- Redirect customer to confirmation page

## Project Structure

```
almina-design/
├── config/              # Django project settings
│   ├── settings.py      # Loads .env variables, Stripe config
│   ├── urls.py          # Root URL router
│   └── wsgi.py
├── store/               # Main app
│   ├── models.py        # Category, MemorabiliaItem, Order, OrderItem
│   ├── views.py         # Storefront, checkout, webhooks
│   ├── forms.py         # CheckoutForm
│   ├── urls.py          # Store app routes
│   ├── admin.py         # Django admin configuration
│   ├── migrations/      # Database schema changes
│   └── fixtures/        # sample_inventory.json
├── templates/           # HTML templates
│   ├── base.html        # Shared layout, styles, nav
│   ├── store/           # Store-specific templates
│   │   ├── storefront.html
│   │   ├── item_detail.html
│   │   ├── cart.html
│   │   ├── checkout.html
│   │   ├── order_confirmation.html
│   │   ├── inventory_dashboard.html
│   │   └── payment_cancelled.html
│   └── registration/    # Auth templates
│       └── login.html
├── .env                 # Local environment variables (git-ignored)
├── .env.example         # Template for .env
├── .gitignore
├── db.sqlite3           # Development database
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Data Models

### Category

- `name` — Category name (unique)
- `slug` — URL-friendly identifier

### MemorabiliaItem

- `category` (FK) — Product category
- `name` — Product name
- `slug` — URL-friendly identifier
- `sku` — Stock keeping unit (unique)
- `era` — Historical period (e.g., "WWI", "Cold War")
- `description` — Full product details
- `condition` — Item condition notes
- `unit_price` — Price in USD
- `quantity_in_stock` — Current inventory count
- `image` — Product photo upload
- `is_active` — Visibility toggle
- `created_at`, `updated_at` — Timestamps

### Order

- `full_name`, `email`, `address` — Customer details
- `status` — Fulfillment state: pending, confirmed, shipped, cancelled
- `payment_status` — Payment state: unpaid, paid, failed, refunded
- `stripe_session_id` — Stripe Checkout Session ID
- `stripe_payment_intent_id` — Stripe Payment Intent ID
- `paid_at` — Timestamp of payment confirmation
- `created_at` — Order creation timestamp

### OrderItem (Line Item)

- `order` (FK) — Associated order
- `item` (FK) — MemorabiliaItem purchased
- `quantity` — Units ordered
- `unit_price` — Locked price at purchase time

## Payment & Fulfillment Workflow

### Payment Flow

1. **Add to Cart** → Items stored in session
2. **Checkout** → Form collects shipping/billing info
3. **Create Order & Session** → Order created in DB with status "pending", Stripe Checkout Session initialized
4. **Redirect to Stripe** → Customer routed to Stripe-hosted payment page (test card: `4242 4242 4242 4242`)
5. **Payment Processing** → Stripe handles card details securely
6. **Webhook Confirmation** → Stripe sends `checkout.session.completed` to `/payments/stripe/webhook/`
7. **Validate & Update** → App verifies webhook signature, marks order "confirmed"/"paid", decrements inventory
8. **Redirect to Confirmation** → Customer sees order summary and confirmation email sent

### Order Status Transitions

| Status    | Meaning                         | Trigger                        |
| --------- | ------------------------------- | ------------------------------ |
| pending   | Order created, awaiting payment | Checkout form submitted        |
| confirmed | Payment received                | Stripe webhook confirms        |
| shipped   | Order dispatched                | Admin marks in Django Admin    |
| cancelled | Order cancelled                 | Admin cancel or payment failed |

| Payment Status | Meaning                                   |
| -------------- | ----------------------------------------- |
| unpaid         | Order awaiting payment                    |
| paid           | Payment confirmed via Stripe webhook      |
| failed         | Payment attempt failed or order cancelled |
| refunded       | Order refunded via Stripe dashboard       |

## Dependencies

See `requirements.txt`:

- **Django 6.0.3** — Web framework
- **Pillow** — Image processing
- **stripe** — Stripe API client
- **easypost** — EasyPost API client for USPS shipping rates
- **python-dotenv** — Environment variable management

## Development Notes

- **Cart Storage:** Session-based (no database, no login required)
- **Images:** Uploaded to `media/items/` directory
- **Styling:** Inline CSS in base template with Space Grotesk font
- **Time Zone:** UTC (configurable in `settings.py`)
- **Database:** SQLite for development (switch to PostgreSQL for production)

## Deployment Checklist

For production deployment:

- [ ] Set `DEBUG=False` in `.env`
- [ ] Update `SECRET_KEY` to a strong random value
- [ ] Set `ALLOWED_HOSTS` in `settings.py`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure HTTPS/SSL
- [ ] Set Stripe production keys (not test keys)
- [ ] Update `SITE_URL` to production domain
- [ ] Run `python manage.py collectstatic`
- [ ] Use a production-grade WSGI server (Gunicorn, uWSGI)
- [ ] Configure environment variables on hosting platform
