"""
Flask API for REST Assured testing practice.

This is a simple in-memory REST API designed to be tested by the
Java REST Assured project in ../rest-assured-project.

Run with:
    python app.py

Default port: 5001
"""

import os
import re
import time
import random
import threading
from decimal import Decimal, ROUND_HALF_UP
from functools import wraps

from flask import Flask, redirect, request, jsonify
from flasgger import Swagger
from enum import Enum
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

app = Flask(__name__)

# Swagger / OpenAPI configuration
app.config["SWAGGER"] = {
    "title": "py-rest API",
    "description": "Flask API for REST Assured testing practice.",
    "version": "1.0.0",
    "specs_route": "/apidocs/",
    "uiversion": 3,
}
Swagger(app)

# ------------------------------------------------------------------
# Seed data (mirrors JSONPlaceholder so existing tests work out of the box)
# ------------------------------------------------------------------
SEED_USERS = {
    1: {
        "id": 1, "name": "Leanne Graham", "username": "Bret", "email": "Sincere@april.biz",
        "address": {
            "street": "Kulas Light", "suite": "Apt. 556", "city": "Gwenborough",
            "zipcode": "92998-3874", "geo": {"lat": "-37.3159", "lng": "81.1496"}
        },
        "phone": "1-770-736-8031 x56442", "website": "hildegard.org",
        "company": {"name": "Romaguera-Crona", "catchPhrase": "Multi-layered client-server neural-net", "bs": "harness real-time e-markets"}
    },
    2: {
        "id": 2, "name": "Ervin Howell", "username": "Antonette", "email": "Shanna@melissa.tv",
        "address": {"street": "Victor Plains", "suite": "Suite 879", "city": "Wisokyburgh", "zipcode": "90566-7771", "geo": {"lat": "-43.9509", "lng": "-34.4618"}},
        "phone": "010-692-6593 x09125", "website": "anastasia.net",
        "company": {"name": "Deckow-Crist", "catchPhrase": "Proactive didactic contingency", "bs": "synergize scalable supply-chains"}
    },
    3: {
        "id": 3, "name": "Clementine Bauch", "username": "Samantha", "email": "Nathan@yesenia.net",
        "address": {"street": "Douglas Extension", "suite": "Suite 847", "city": "McKenziehaven", "zipcode": "59590-4157", "geo": {"lat": "-68.6102", "lng": "-47.0653"}},
        "phone": "1-463-123-4447", "website": "ramiro.info",
        "company": {"name": "Romaguera-Jacobson", "catchPhrase": "Face to face bifurcated interface", "bs": "e-enable strategic applications"}
    },
    4: {"id": 4, "name": "Patricia Lebsack", "username": "Karianne", "email": "Julianne.OConner@kory.org", "address": {"street": "Hoeger Mall", "suite": "Apt. 692", "city": "South Elvis", "zipcode": "53919-4257", "geo": {"lat": "29.4572", "lng": "-164.2990"}}, "phone": "493-170-9623 x156", "website": "kale.biz", "company": {"name": "Robel-Corkery", "catchPhrase": "Multi-tiered zero tolerance productivity", "bs": "transition cutting-edge web services"}},
    5: {"id": 5, "name": "Chelsey Dietrich", "username": "Kamren", "email": "Lucio_Hettinger@annie.ca", "address": {"street": "Skiles Walks", "suite": "Suite 351", "city": "Roscoeview", "zipcode": "33263", "geo": {"lat": "-31.8129", "lng": "62.5342"}}, "phone": "(254)954-1289", "website": "demarco.info", "company": {"name": "Keebler LLC", "catchPhrase": "User-centric fault-tolerant solution", "bs": "revolutionize end-to-end systems"}},
    6: {"id": 6, "name": "Mrs. Dennis Schulist", "username": "Leopoldo_Corkery", "email": "Karley_Dach@jasper.info", "address": {"street": "Norberto Crossing", "suite": "Apt. 950", "city": "South Christy", "zipcode": "23505-1337", "geo": {"lat": "-71.4197", "lng": "38.5730"}}, "phone": "1-477-935-8478 x6430", "website": "ola.org", "company": {"name": "Considine-Lockman", "catchPhrase": "Synchronised bottom-line interface", "bs": "e-enable innovative applications"}},
    7: {"id": 7, "name": "Kurtis Weissnat", "username": "Elwyn.Skiles", "email": "Telly.Hoeger@billy.biz", "address": {"street": "Rex Trail", "suite": "Suite 280", "city": "South Elvis", "zipcode": "58804-1099", "geo": {"lat": "24.8918", "lng": "21.8984"}}, "phone": "210.067.6132", "website": "elvis.io", "company": {"name": "Johns Group", "catchPhrase": "Configurable multimedia task-force", "bs": "generate enterprise e-tailers"}},
    8: {"id": 8, "name": "Nicholas Runolfsdottir V", "username": "Maxime_Nienow", "email": "Sherwood@rosamond.me", "address": {"street": "Ellsworth Summit", "suite": "Suite 729", "city": "Aliyaview", "zipcode": "45169", "geo": {"lat": "-14.3990", "lng": "-120.7677"}}, "phone": "586.493.6943 x140", "website": "jacynthe.com", "company": {"name": "Abernathy Group", "catchPhrase": "Implemented secondary concept", "bs": "e-enable extensible e-tailers"}},
    9: {"id": 9, "name": "Glenna Reichert", "username": "Delphine", "email": "Chaim_McDermott@dana.io", "address": {"street": "Dayna Park", "suite": "Suite 449", "city": "Bartholomebury", "zipcode": "76495-3109", "geo": {"lat": "24.6463", "lng": "-168.8883"}}, "phone": "(775)976-6794 x41206", "website": "conrad.com", "company": {"name": "Yost and Sons", "catchPhrase": "Switchable contextually-based project", "bs": "aggregate real-time technologies"}},
    10: {"id": 10, "name": "Clementina DuBuque", "username": "Moriah.Stanton", "email": "Rey.Padberg@karina.biz", "address": {"street": "Kattie Turnpike", "suite": "Suite 198", "city": "Lebsackbury", "zipcode": "31428-2261", "geo": {"lat": "-38.2386", "lng": "57.2232"}}, "phone": "024-648-3804", "website": "ambrose.net", "company": {"name": "Hoeger LLC", "catchPhrase": "Centralized empowering instruction set", "bs": "target end-to-end models"}},
}

SEED_POSTS = {
    1: {"id": 1, "userId": 1, "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit", "body": "quia et suscipit"},
    2: {"id": 2, "userId": 1, "title": "qui est esse", "body": "est rerum tempore vitae sequi sint nihil reprehenderit dolor beatae ea dolores neque"},
    3: {"id": 3, "userId": 1, "title": "ea molestias quasi exercitationem repellat qui ipsa sit aut", "body": "et iusto sed quo iure voluptatem occaecati omnis eligendi aut ad voluptatem doloribus"},
    4: {"id": 4, "userId": 1, "title": "eum et est occaecati", "body": "ullam et saepe reiciendis voluptatem adipisci sit amet autem assumenda"},
    5: {"id": 5, "userId": 1, "title": "nesciunt quas odio", "body": "repudiandae veniam quaerat sunt sed alias aut fugiat sit autem"},
    6: {"id": 6, "userId": 1, "title": "dolorem eum magni eos aperiam quia", "body": "ut aspernatur corporis harum nihil quis provident sequi"},
    7: {"id": 7, "userId": 1, "title": "magnam facilis autem", "body": "dolore placeat quibusdam ea quo vitae magni quis"},
    8: {"id": 8, "userId": 1, "title": "dolorem dolore est ipsam", "body": "dignissimos aperiam dolorem qui eum facilis quibusdam animi sint"},
    9: {"id": 9, "userId": 1, "title": "nesciunt iure omnis dolorem tempora et accusantium", "body": "consectetur animi nesciunt iure dolore"},
    10: {"id": 10, "userId": 1, "title": "optio molestias id quia eum", "body": "quo et expedita modi cum officia vel magni doloribus"},
}

# Generate remaining posts for userIds 1-10 to reach 100 posts (mirrors JSONPlaceholder count).
for i in range(11, 101):
    SEED_POSTS[i] = {
        "id": i,
        "userId": ((i - 1) % 10) + 1,
        "title": f"Post title {i}",
        "body": f"Post body content for post {i}",
    }

SEED_COMMENTS = {
    1: {"id": 1, "postId": 1, "name": "id labore ex et quam laborum", "email": "Eliseo@gardner.biz", "body": "laudantium enim quasi est quidem magnam voluptate"},
    2: {"id": 2, "postId": 1, "name": "quo vero reiciendis velitsimiliqueearum", "email": "Jayne_Kuhic@sydney.com", "body": "est natus enim nihil est dolore omnis voluptatem"},
    3: {"id": 3, "postId": 1, "name": "odio adipisci rerum aut animi", "email": "Nikita@garfield.biz", "body": "quia molestiae reprehenderit quasi aspernatur"},
}

users = {}
posts = {}
comments = {}
next_user_id = 1
next_post_id = 1
next_comment_id = 1


def reset_data():
    """Reset in-memory stores to the original seed data."""
    global users, posts, comments, next_user_id, next_post_id, next_comment_id
    global payments, next_payment_id, wallets, payouts
    global idempotency_store, request_counters, wallet_locks, partial_failure_state
    users = {k: dict(v) for k, v in SEED_USERS.items()}
    posts = {k: dict(v) for k, v in SEED_POSTS.items()}
    comments = {k: dict(v) for k, v in SEED_COMMENTS.items()}
    next_user_id = max(users.keys(), default=0) + 1
    next_post_id = max(posts.keys(), default=0) + 1
    next_comment_id = max(comments.keys(), default=0) + 1

    payments = {}
    next_payment_id = 1
    wallets = {}
    payouts = {}
    idempotency_store = {}
    request_counters = {}
    wallet_locks = {}
    partial_failure_state = {}

# ------------------------------------------------------------------
# Authentication demo setup
# ------------------------------------------------------------------
# In production these would come from a secrets manager / environment.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
API_KEY = os.environ.get("API_KEY", "secret-key-123")

token_serializer = URLSafeTimedSerializer(SECRET_KEY)

# In-memory user store for Day 2 authentication exercises.
# Passwords are hashed so the demo still resembles real practice.
USERS_AUTH = {
    "alice": {"password": generate_password_hash("password123"), "role": "user"},
    "admin": {"password": generate_password_hash("admin123"), "role": "admin"},
}

# ------------------------------------------------------------------
# Day 2: manual request validation (no external dependencies)
# ------------------------------------------------------------------
class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))


_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
_ISO_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")


def _err(loc, msg, type_="value_error"):
    return {"loc": loc, "msg": msg, "type": type_}


def _require_string(errors, data, field, required=True, min_len=0, max_len=None, pattern=None):
    value = data.get(field)
    if value is None:
        if required:
            errors.append(_err([field], "field required", "missing"))
        return None
    if not isinstance(value, str):
        errors.append(_err([field], "must be a string", "type_error"))
        return None
    value = value.strip()
    if min_len and len(value) < min_len:
        errors.append(_err([field], f"must be at least {min_len} characters", "value_error"))
    if max_len is not None and len(value) > max_len:
        errors.append(_err([field], f"must be at most {max_len} characters", "value_error"))
    if pattern is not None and not pattern.match(value):
        errors.append(_err([field], "invalid format", "value_error"))
    return value


def _optional_string(errors, data, field, max_len=None):
    value = data.get(field)
    if value is None:
        return None
    return _require_string(errors, data, field, required=False, max_len=max_len)


def _require_email(errors, data, field, required=True):
    value = _require_string(errors, data, field, required=required, min_len=1, max_len=254)
    if value is not None and not _EMAIL_RE.match(value):
        errors.append(_err([field], "invalid email address", "value_error"))
    return value


def _require_positive_int(errors, data, field, required=True):
    value = data.get(field)
    if value is None:
        if required:
            errors.append(_err([field], "field required", "missing"))
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        errors.append(_err([field], "must be an integer", "type_error"))
        return None
    if value <= 0:
        errors.append(_err([field], "must be greater than 0", "value_error"))
    return value


def _require_positive_decimal(errors, data, field, required=True, decimal_places=2):
    value = data.get(field)
    if value is None:
        if required:
            errors.append(_err([field], "field required", "missing"))
        return None
    try:
        dec = Decimal(str(value))
    except Exception:
        errors.append(_err([field], "must be a valid decimal number", "type_error"))
        return None
    if dec <= 0:
        errors.append(_err([field], "must be greater than 0", "value_error"))
        return None
    # Validate decimal places.
    exponent = dec.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -decimal_places:
        errors.append(_err([field], f"must have at most {decimal_places} decimal places", "value_error"))
    return dec


def _require_iso_currency(errors, data, field, required=True):
    value = _require_string(errors, data, field, required=required, min_len=3, max_len=3)
    if value is not None:
        value = value.upper()
        if not _ISO_CURRENCY_RE.match(value):
            errors.append(_err([field], "must be a 3-letter ISO currency code", "value_error"))
    return value


class PaymentStatus(str, Enum):
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    REFUNDED = "refunded"
    REVERSED = "reversed"
    VOIDED = "voided"
    CHARGEBACK = "chargeback"
    SETTLED = "settled"


def validate_user_create(data):
    if not isinstance(data, dict):
        raise ValidationError([_err([], "expected an object", "type_error")])
    errors = []
    result = {
        "name": _require_string(errors, data, "name", min_len=1, max_len=100),
        "username": _require_string(errors, data, "username", min_len=1, max_len=50, pattern=re.compile(r"^[a-zA-Z0-9_]+$")),
        "email": _require_email(errors, data, "email"),
        "phone": _optional_string(errors, data, "phone", max_len=50),
        "website": _optional_string(errors, data, "website", max_len=100),
    }
    if errors:
        raise ValidationError(errors)
    return result


def validate_user_update(data):
    if not isinstance(data, dict):
        raise ValidationError([_err([], "expected an object", "type_error")])
    errors = []
    result = {}
    if "name" in data:
        result["name"] = _require_string(errors, data, "name", min_len=1, max_len=100)
    if "username" in data:
        result["username"] = _require_string(errors, data, "username", min_len=1, max_len=50, pattern=re.compile(r"^[a-zA-Z0-9_]+$"))
    if "email" in data:
        result["email"] = _require_email(errors, data, "email")
    if "phone" in data:
        result["phone"] = _optional_string(errors, data, "phone", max_len=50)
    if "website" in data:
        result["website"] = _optional_string(errors, data, "website", max_len=100)
    if errors:
        raise ValidationError(errors)
    return result


def validate_post_create(data):
    if not isinstance(data, dict):
        raise ValidationError([_err([], "expected an object", "type_error")])
    errors = []
    result = {
        "title": _require_string(errors, data, "title", min_len=1, max_len=200),
        "body": _optional_string(errors, data, "body", max_len=2000),
        "userId": _require_positive_int(errors, data, "userId"),
    }
    if errors:
        raise ValidationError(errors)
    return result


def validate_post_update(data):
    if not isinstance(data, dict):
        raise ValidationError([_err([], "expected an object", "type_error")])
    errors = []
    result = {}
    if "title" in data:
        result["title"] = _require_string(errors, data, "title", min_len=1, max_len=200)
    if "body" in data:
        result["body"] = _optional_string(errors, data, "body", max_len=2000)
    if "userId" in data:
        result["userId"] = _require_positive_int(errors, data, "userId")
    if errors:
        raise ValidationError(errors)
    return result


def validate_payment_create(data):
    if not isinstance(data, dict):
        raise ValidationError([_err([], "expected an object", "type_error")])
    errors = []
    result = {
        "amount": _require_positive_decimal(errors, data, "amount"),
        "currency": _require_iso_currency(errors, data, "currency"),
        "merchant_id": _require_string(errors, data, "merchant_id", min_len=1),
        "description": _optional_string(errors, data, "description", max_len=255),
        "idempotency_key": _optional_string(errors, data, "idempotency_key", max_len=100),
    }
    if errors:
        raise ValidationError(errors)
    return result


def validate_payout_create(data):
    if not isinstance(data, dict):
        raise ValidationError([_err([], "expected an object", "type_error")])
    errors = []
    result = {
        "wallet_id": _require_string(errors, data, "wallet_id", min_len=1),
        "amount": _require_positive_decimal(errors, data, "amount"),
        "currency": _require_iso_currency(errors, data, "currency"),
    }
    if errors:
        raise ValidationError(errors)
    return result


# ------------------------------------------------------------------
# Day 2: in-memory stores for fintech / reliability demos
# ------------------------------------------------------------------
payments = {}
next_payment_id = 1
wallets = {}
payouts = {}
fx_rates = {
    ("USD", "EUR"): Decimal("0.9200"),
    ("EUR", "USD"): Decimal("1.0870"),
    ("USD", "GBP"): Decimal("0.7900"),
    ("GBP", "USD"): Decimal("1.2658"),
}
idempotency_store = {}          # idempotency_key -> response payload
request_counters = {}           # for flaky endpoint
wallet_locks = {}               # wallet_id -> threading.Lock
partial_failure_state = {}      # idempotency_key -> success/failure counts


def _round_money(value: Decimal) -> Decimal:
    """Round a monetary amount to 2 decimal places (bankers rounding)."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_wallet_lock(wallet_id: str) -> threading.Lock:
    if wallet_id not in wallet_locks:
        wallet_locks[wallet_id] = threading.Lock()
    return wallet_locks[wallet_id]


# Simple in-memory rate limiter: track requests per IP.
rate_limit_window = 60  # seconds
rate_limit_max_requests = 5
rate_limit_log = {}


# Initialize all stores once every name above is defined.
reset_data()


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _get_next_id(store):
    global next_user_id, next_post_id, next_comment_id
    if store is users:
        new_id = next_user_id
        next_user_id += 1
        return new_id
    elif store is posts:
        new_id = next_post_id
        next_post_id += 1
        return new_id
    elif store is comments:
        new_id = next_comment_id
        next_comment_id += 1
        return new_id
    raise ValueError("unknown store")


def _not_found(resource):
    return jsonify({"error": f"{resource} not found"}), 404


def _issue_token(username, role):
    """Issue a signed bearer-style token for the given user."""
    return token_serializer.dumps({"sub": username, "role": role})


def _verify_bearer_token():
    """Validate an Authorization: Bearer <token> header and return its payload."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    try:
        return token_serializer.loads(token, max_age=3600)
    except (BadSignature, SignatureExpired):
        return None


def _validation_error_response(exc: ValidationError):
    """Convert a ValidationError into a Flask JSON 422 response."""
    return jsonify({
        "error": "validation failed",
        "details": exc.errors,
    }), 422


def _paginate(items, key=None):
    """
    Apply pagination, sorting, and simple filtering to a list of dicts.
    Query params: page, limit, sort, order (asc|desc)
    """
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    sort_field = request.args.get("sort")
    order = request.args.get("order", "asc").lower()

    if page < 1:
        page = 1
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100

    data = list(items)
    if sort_field:
        reverse = order == "desc"

        def _sort_key(x):
            val = x.get(sort_field)
            if isinstance(val, (int, float)):
                return (0, val)
            if isinstance(val, str):
                return (1, val)
            return (2, "")

        data = sorted(data, key=_sort_key, reverse=reverse)

    total = len(data)
    start = (page - 1) * limit
    end = start + limit
    page_data = data[start:end]

    return jsonify({
        "data": page_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
        },
    }), 200


def _get_payment_or_404(payment_id: int):
    payment = payments.get(payment_id)
    if not payment:
        return None, jsonify({"error": "payment not found"}), 404
    return payment, None, 200


# ------------------------------------------------------------------
# Health
# ------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """Redirect to the Swagger UI."""
    return redirect("/apidocs/")


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    ---
    responses:
      200:
        description: API is running
    """
    return jsonify({"status": "ok"}), 200


@app.route("/reset", methods=["POST"])
def reset():
    """Reset all in-memory data back to seed values."""
    reset_data()
    rate_limit_log.clear()
    return jsonify({"reset": True}), 200


# ------------------------------------------------------------------
# Users
# ------------------------------------------------------------------
@app.route("/users", methods=["GET"])
def get_users():
    """
    List all users with pagination, sorting, and filtering.
    ---
    parameters:
      - name: page
        in: query
        type: integer
        required: false
      - name: limit
        in: query
        type: integer
        required: false
      - name: sort
        in: query
        type: string
        required: false
      - name: order
        in: query
        type: string
        required: false
      - name: username
        in: query
        type: string
        required: false
    responses:
      200:
        description: Paginated list of users
    """
    result = list(users.values())
    username = request.args.get("username")
    if username:
        result = [u for u in result if username.lower() in (u.get("username") or "").lower()]

    # Preserve backward compatibility: return a flat list unless pagination params are requested.
    if any(k in request.args for k in ("page", "limit", "sort", "order")):
        return _paginate(result)
    return jsonify(result), 200


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Get a single user by ID.
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User found
      404:
        description: User not found
    """
    user = users.get(user_id)
    if not user:
        return _not_found("user")
    return jsonify(user), 200


@app.route("/users", methods=["POST"])
def create_user():
    """
    Create a new user (request validation enabled).
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            username:
              type: string
            email:
              type: string
    responses:
      201:
        description: User created
      400:
        description: Empty request body
      422:
        description: Validation error
    """
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "request body cannot be empty"}), 400
    try:
        validated = validate_user_create(data)
    except ValidationError as exc:
        return _validation_error_response(exc)

    new_id = _get_next_id(users)
    user = {"id": new_id, **validated}
    users[new_id] = user
    return jsonify(user), 201


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Replace an existing user (full update with validation).
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: User updated
      404:
        description: User not found
      422:
        description: Validation error
    """
    if user_id not in users:
        return _not_found("user")
    data = request.get_json(silent=True) or {}
    try:
        validated = validate_user_create(data)
    except ValidationError as exc:
        return _validation_error_response(exc)

    user = {"id": user_id, **validated}
    users[user_id] = user
    return jsonify(user), 200


@app.route("/users/<int:user_id>", methods=["PATCH"])
def patch_user(user_id):
    """
    Partially update an existing user (validation enabled).
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: User patched
      404:
        description: User not found
      422:
        description: Validation error
    """
    if user_id not in users:
        return _not_found("user")
    data = request.get_json(silent=True) or {}
    try:
        validated = validate_user_update(data)
    except ValidationError as exc:
        return _validation_error_response(exc)

    user = users[user_id]
    for field, value in validated.items():
        user[field] = value
    return jsonify(user), 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Delete a user.
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User deleted
      404:
        description: User not found
    """
    if user_id not in users:
        return _not_found("user")
    del users[user_id]
    return jsonify({"deleted": True}), 200


# ------------------------------------------------------------------
# Posts
# ------------------------------------------------------------------
@app.route("/posts", methods=["GET"])
def get_posts():
    """
    List all posts with pagination, sorting, and filtering.
    ---
    parameters:
      - name: userId
        in: query
        type: integer
        required: false
      - name: id
        in: query
        type: integer
        required: false
      - name: title_contains
        in: query
        type: string
        required: false
      - name: page
        in: query
        type: integer
        required: false
      - name: limit
        in: query
        type: integer
        required: false
      - name: sort
        in: query
        type: string
        required: false
      - name: order
        in: query
        type: string
        required: false
    responses:
      200:
        description: Paginated list of posts
    """
    result = list(posts.values())

    user_id = request.args.get("userId", type=int)
    post_id = request.args.get("id", type=int)
    title_contains = request.args.get("title_contains")

    if user_id is not None:
        result = [p for p in result if p.get("userId") == user_id]
    if post_id is not None:
        result = [p for p in result if p.get("id") == post_id]
    if title_contains:
        result = [p for p in result if title_contains.lower() in (p.get("title") or "").lower()]

    # Preserve backward compatibility: return a flat list unless pagination params are requested.
    if any(k in request.args for k in ("page", "limit", "sort", "order")):
        return _paginate(result, key=lambda x: x.get("id"))
    return jsonify(result), 200


@app.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    """
    Get a single post by ID.
    ---
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Post found
      404:
        description: Post not found
    """
    post = posts.get(post_id)
    if not post:
        return _not_found("post")
    return jsonify(post), 200


@app.route("/posts", methods=["POST"])
def create_post():
    """
    Create a new post (request validation enabled).
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
            body:
              type: string
            userId:
              type: integer
    responses:
      201:
        description: Post created
      400:
        description: Empty request body
      404:
        description: User not found
      422:
        description: Validation error
    """
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "request body cannot be empty"}), 400
    try:
        validated = validate_post_create(data)
    except ValidationError as exc:
        return _validation_error_response(exc)

    if validated["userId"] not in users:
        return _not_found("user")

    new_id = _get_next_id(posts)
    post = {"id": new_id, **validated}
    posts[new_id] = post
    return jsonify(post), 201


@app.route("/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    """
    Replace an existing post (full update with validation).
    ---
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Post updated
      404:
        description: Post not found
      422:
        description: Validation error
    """
    if post_id not in posts:
        return _not_found("post")
    data = request.get_json(silent=True) or {}
    try:
        validated = validate_post_create(data)
    except ValidationError as exc:
        return _validation_error_response(exc)

    if validated["userId"] not in users:
        return _not_found("user")

    post = {"id": post_id, **validated}
    posts[post_id] = post
    return jsonify(post), 200


@app.route("/posts/<int:post_id>", methods=["PATCH"])
def patch_post(post_id):
    """
    Partially update an existing post (validation enabled).
    ---
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Post patched
      404:
        description: Post not found
      422:
        description: Validation error
    """
    if post_id not in posts:
        return _not_found("post")
    data = request.get_json(silent=True) or {}
    try:
        validated = validate_post_update(data)
    except ValidationError as exc:
        return _validation_error_response(exc)

    post = posts[post_id]
    for field, value in validated.items():
        if field == "userId" and value not in users:
            return _not_found("user")
        post[field] = value
    return jsonify(post), 200


@app.route("/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """
    Delete a post.
    ---
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Post deleted
      404:
        description: Post not found
    """
    if post_id not in posts:
        return _not_found("post")
    del posts[post_id]
    return jsonify({"deleted": True}), 200


@app.route("/posts/<int:post_id>/comments", methods=["GET"])
def get_post_comments(post_id):
    """
    Get all comments for a specific post.
    ---
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: List of comments for the post
    """
    post_comments = [c for c in comments.values() if c.get("postId") == post_id]
    return jsonify(post_comments), 200


@app.route("/posts/<int:post_id>/comments", methods=["POST"])
def create_post_comment(post_id):
    """
    Add a comment to a specific post.
    ---
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
            body:
              type: string
    responses:
      201:
        description: Comment created
      404:
        description: Post not found
      400:
        description: Empty request body
    """
    if post_id not in posts:
        return _not_found("post")
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "request body cannot be empty"}), 400
    new_id = _get_next_id(comments)
    comment = {
        "id": new_id,
        "postId": post_id,
        "name": data.get("name", ""),
        "email": data.get("email", ""),
        "body": data.get("body", ""),
    }
    comments[new_id] = comment
    return jsonify(comment), 201


# ------------------------------------------------------------------
# Comments
# ------------------------------------------------------------------
@app.route("/comments", methods=["GET"])
def get_comments():
    return jsonify(list(comments.values())), 200


@app.route("/comments/<int:comment_id>", methods=["GET"])
def get_comment(comment_id):
    comment = comments.get(comment_id)
    if not comment:
        return _not_found("comment")
    return jsonify(comment), 200


# ------------------------------------------------------------------
# Day 2: Advanced API testing / Fintech endpoints
# ------------------------------------------------------------------

# ---------- Shared helpers ----------


def _generate_payment_id():
    global next_payment_id
    payment_id = next_payment_id
    next_payment_id += 1
    return payment_id


def _serialize_payment(payment):
    """Return a JSON-serializable copy of a payment dict."""
    return {
        **payment,
        "amount": str(payment["amount"]),
        "fee": str(payment["fee"]),
        "net_amount": str(payment["net_amount"]),
        "exchange_rate": str(payment["exchange_rate"]) if payment.get("exchange_rate") else None,
    }


def _check_idempotency(idempotency_key):
    """Return a stored response if the key has been seen before."""
    if idempotency_key and idempotency_key in idempotency_store:
        return idempotency_store[idempotency_key]
    return None


def _store_idempotency(idempotency_key, response_tuple):
    """Cache a response tuple under an idempotency key."""
    if idempotency_key:
        idempotency_store[idempotency_key] = response_tuple


# ---------- Payments lifecycle ----------


@app.route("/payments", methods=["POST"])
def create_payment():
    """
    Create a payment (authorization).
    Supports Idempotency-Key header to prevent duplicate payments.
    ---
    parameters:
      - name: Idempotency-Key
        in: header
        type: string
        required: false
      - name: body
        in: body
        required: true
    responses:
      201:
        description: Payment created
      400:
        description: Bad request
      422:
        description: Validation error
      409:
        description: Duplicate idempotency key with different payload
    """
    idempotency_key = request.headers.get("Idempotency-Key")
    cached = _check_idempotency(idempotency_key)
    if cached:
        return cached

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "request body cannot be empty"}), 400

    try:
        validated = validate_payment_create(data)
    except ValidationError as exc:
        return _validation_error_response(exc)

    amount = validated["amount"]
    fee = _round_money(amount * Decimal("0.029")) + Decimal("0.30")
    net = _round_money(amount - fee)

    payment_id = _generate_payment_id()
    payment = {
        "id": payment_id,
        "status": PaymentStatus.AUTHORIZED,
        "amount": amount,
        "currency": validated["currency"],
        "fee": fee,
        "net_amount": net,
        "merchant_id": validated["merchant_id"],
        "description": validated["description"],
        "idempotency_key": idempotency_key,
        "exchange_rate": None,
        "settled_at": None,
        "created_at": time.time(),
    }
    payments[payment_id] = payment

    response = jsonify(_serialize_payment(payment)), 201
    _store_idempotency(idempotency_key, response)
    return response


@app.route("/payments/<int:payment_id>", methods=["GET"])
def get_payment(payment_id):
    """Get a single payment by ID."""
    payment = payments.get(payment_id)
    if not payment:
        return _not_found("payment")
    return jsonify(_serialize_payment(payment)), 200


@app.route("/payments", methods=["GET"])
def list_payments():
    """
    List payments with pagination, filtering, and sorting.
    ---
    parameters:
      - name: status
        in: query
        type: string
        required: false
      - name: merchant_id
        in: query
        type: string
        required: false
      - name: page
        in: query
        type: integer
        required: false
      - name: limit
        in: query
        type: integer
        required: false
      - name: sort
        in: query
        type: string
        required: false
    responses:
      200:
        description: Paginated list of payments
    """
    result = list(payments.values())
    status_filter = request.args.get("status")
    merchant_filter = request.args.get("merchant_id")

    if status_filter:
        result = [p for p in result if p["status"] == status_filter]
    if merchant_filter:
        result = [p for p in result if p["merchant_id"] == merchant_filter]

    return _paginate(result, key=lambda x: x["id"])


@app.route("/payments/<int:payment_id>/capture", methods=["POST"])
def capture_payment(payment_id):
    """Move a payment from authorized -> captured."""
    payment = payments.get(payment_id)
    if not payment:
        return _not_found("payment")
    if payment["status"] != PaymentStatus.AUTHORIZED:
        return jsonify({"error": f"cannot capture payment in status {payment['status']}"}), 409

    payment["status"] = PaymentStatus.CAPTURED
    return jsonify(_serialize_payment(payment)), 200


@app.route("/payments/<int:payment_id>/void", methods=["POST"])
def void_payment(payment_id):
    """Void an authorized payment."""
    payment = payments.get(payment_id)
    if not payment:
        return _not_found("payment")
    if payment["status"] != PaymentStatus.AUTHORIZED:
        return jsonify({"error": f"cannot void payment in status {payment['status']}"}), 409

    payment["status"] = PaymentStatus.VOIDED
    return jsonify(_serialize_payment(payment)), 200


@app.route("/payments/<int:payment_id>/refund", methods=["POST"])
def refund_payment(payment_id):
    """Refund a captured payment (partial refund supported)."""
    payment = payments.get(payment_id)
    if not payment:
        return _not_found("payment")
    if payment["status"] != PaymentStatus.CAPTURED:
        return jsonify({"error": f"cannot refund payment in status {payment['status']}"}), 409

    data = request.get_json(silent=True) or {}
    refund_amount = data.get("amount")
    if refund_amount is None:
        refund_amount = payment["amount"]
    try:
        refund_amount = Decimal(str(refund_amount))
    except Exception:
        return jsonify({"error": "amount must be a valid decimal"}), 422

    if refund_amount <= 0 or refund_amount > payment["amount"]:
        return jsonify({"error": "refund amount must be positive and not exceed payment amount"}), 422

    payment["status"] = PaymentStatus.REFUNDED
    payment["refund_amount"] = refund_amount
    return jsonify({"refund_amount": str(refund_amount), "payment": _serialize_payment(payment)}), 200


@app.route("/payments/<int:payment_id>/reverse", methods=["POST"])
def reverse_payment(payment_id):
    """Reverse an authorized payment."""
    payment = payments.get(payment_id)
    if not payment:
        return _not_found("payment")
    if payment["status"] != PaymentStatus.AUTHORIZED:
        return jsonify({"error": f"cannot reverse payment in status {payment['status']}"}), 409

    payment["status"] = PaymentStatus.REVERSED
    return jsonify(_serialize_payment(payment)), 200


@app.route("/payments/<int:payment_id>/chargeback", methods=["POST"])
def chargeback_payment(payment_id):
    """Chargeback a captured payment."""
    payment = payments.get(payment_id)
    if not payment:
        return _not_found("payment")
    if payment["status"] not in (PaymentStatus.CAPTURED, PaymentStatus.SETTLED):
        return jsonify({"error": f"cannot chargeback payment in status {payment['status']}"}), 409

    payment["status"] = PaymentStatus.CHARGEBACK
    return jsonify(_serialize_payment(payment)), 200


@app.route("/payments/<int:payment_id>/settle", methods=["POST"])
def settle_payment(payment_id):
    """Mark a captured payment as settled."""
    payment = payments.get(payment_id)
    if not payment:
        return _not_found("payment")
    if payment["status"] != PaymentStatus.CAPTURED:
        return jsonify({"error": f"cannot settle payment in status {payment['status']}"}), 409

    payment["status"] = PaymentStatus.SETTLED
    payment["settled_at"] = time.time()
    return jsonify(_serialize_payment(payment)), 200


@app.route("/payments/<int:payment_id>/status-transitions", methods=["GET"])
def payment_status_transitions(payment_id):
    """Return the allowed next statuses for a payment (state machine helper)."""
    payment = payments.get(payment_id)
    if not payment:
        return _not_found("payment")

    transitions = {
        PaymentStatus.AUTHORIZED: ["capture", "void", "reverse"],
        PaymentStatus.CAPTURED: ["refund", "settle", "chargeback"],
        PaymentStatus.SETTLED: ["chargeback"],
        PaymentStatus.REFUNDED: [],
        PaymentStatus.REVERSED: [],
        PaymentStatus.VOIDED: [],
        PaymentStatus.CHARGEBACK: [],
    }
    return jsonify({"status": payment["status"], "allowed_next": transitions.get(payment["status"], [])}), 200


# ---------- FX conversion ----------


@app.route("/fx/convert", methods=["POST"])
def fx_convert():
    """
    Convert an amount between currencies, returning fee and rounded result.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            amount:
              type: number
            from_currency:
              type: string
            to_currency:
              type: string
    responses:
      200:
        description: Converted amount
      422:
        description: Validation error
    """
    data = request.get_json(silent=True) or {}
    try:
        amount = Decimal(str(data.get("amount")))
        from_currency = data.get("from_currency", "").upper()
        to_currency = data.get("to_currency", "").upper()
    except Exception:
        return jsonify({"error": "amount must be a valid number"}), 422

    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 422
    if len(from_currency) != 3 or len(to_currency) != 3:
        return jsonify({"error": "currency codes must be 3-letter ISO codes"}), 422

    if from_currency == to_currency:
        converted = amount
        rate = Decimal("1.00")
    else:
        rate = fx_rates.get((from_currency, to_currency))
        if not rate:
            return jsonify({"error": f"rate not available for {from_currency}->{to_currency}"}), 404
        converted = _round_money(amount * rate)

    fee = _round_money(converted * Decimal("0.015"))
    net = _round_money(converted - fee)

    return jsonify({
        "from_currency": from_currency,
        "to_currency": to_currency,
        "amount": str(amount),
        "exchange_rate": str(rate),
        "converted_amount": str(converted),
        "fee": str(fee),
        "net_amount": str(net),
    }), 200


# ---------- Wallets ----------


@app.route("/wallets/<wallet_id>", methods=["GET"])
def get_wallet(wallet_id):
    """Get wallet balance and currency."""
    wallet = wallets.get(wallet_id)
    if not wallet:
        return _not_found("wallet")
    return jsonify({
        "wallet_id": wallet_id,
        "balance": str(wallet["balance"]),
        "currency": wallet["currency"],
        "version": wallet["version"],
    }), 200


@app.route("/wallets/<wallet_id>/credit", methods=["POST"])
def credit_wallet(wallet_id):
    """Credit a wallet (thread-safe)."""
    data = request.get_json(silent=True) or {}
    try:
        amount = Decimal(str(data.get("amount")))
    except Exception:
        return jsonify({"error": "amount must be a valid decimal"}), 422
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 422

    lock = _get_wallet_lock(wallet_id)
    with lock:
        wallet = wallets.setdefault(wallet_id, {"balance": Decimal("0.00"), "currency": "USD", "version": 0})
        wallet["balance"] = _round_money(wallet["balance"] + amount)
        wallet["version"] += 1

    return jsonify({"wallet_id": wallet_id, "balance": str(wallet["balance"]), "version": wallet["version"]}), 200


@app.route("/wallets/<wallet_id>/debit", methods=["POST"])
def debit_wallet(wallet_id):
    """Debit a wallet (thread-safe, optimistic concurrency via version)."""
    data = request.get_json(silent=True) or {}
    try:
        amount = Decimal(str(data.get("amount")))
    except Exception:
        return jsonify({"error": "amount must be a valid decimal"}), 422
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 422

    expected_version = data.get("version")
    lock = _get_wallet_lock(wallet_id)
    with lock:
        wallet = wallets.get(wallet_id)
        if not wallet:
            return _not_found("wallet")
        if expected_version is not None and wallet["version"] != expected_version:
            return jsonify({
                "error": "concurrency conflict",
                "current_version": wallet["version"],
                "expected_version": expected_version,
            }), 409
        if wallet["balance"] < amount:
            return jsonify({"error": "insufficient funds"}), 422
        wallet["balance"] = _round_money(wallet["balance"] - amount)
        wallet["version"] += 1

    return jsonify({"wallet_id": wallet_id, "balance": str(wallet["balance"]), "version": wallet["version"]}), 200


@app.route("/wallets/<wallet_id>/payout", methods=["POST"])
def wallet_payout(wallet_id):
    """Payout from a wallet to an external destination."""
    data = request.get_json(silent=True) or {}
    destination = data.get("destination")
    if not destination:
        return jsonify({"error": "destination is required"}), 422

    try:
        amount = Decimal(str(data.get("amount")))
    except Exception:
        return jsonify({"error": "amount must be a valid decimal"}), 422
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 422

    lock = _get_wallet_lock(wallet_id)
    with lock:
        wallet = wallets.get(wallet_id)
        if not wallet:
            return _not_found("wallet")
        if wallet["balance"] < amount:
            return jsonify({"error": "insufficient funds"}), 422
        wallet["balance"] = _round_money(wallet["balance"] - amount)
        wallet["version"] += 1

    payout_id = len(payouts) + 1
    payout = {
        "id": payout_id,
        "wallet_id": wallet_id,
        "destination": destination,
        "amount": str(amount),
        "status": "completed",
        "created_at": time.time(),
    }
    payouts[payout_id] = payout

    return jsonify(payout), 201


# ---------- Reliability / failure simulations ----------


@app.route("/flaky", methods=["GET"])
def flaky_endpoint():
    """
    Randomly returns 500 or 200 to practice retries and idempotency.
    Success rate defaults to 50%; override with ?success_rate=0.8
    """
    try:
        success_rate = float(request.args.get("success_rate", 0.5))
    except ValueError:
        success_rate = 0.5
    success_rate = max(0.0, min(1.0, success_rate))

    if random.random() > success_rate:
        return jsonify({"error": "simulated downstream failure"}), 500
    return jsonify({"message": "success"}), 200


@app.route("/slow", methods=["GET"])
def slow_endpoint():
    """Wait for N seconds so clients can practice timeouts."""
    try:
        delay = float(request.args.get("delay", 3))
    except ValueError:
        delay = 3
    delay = max(0, min(delay, 30))
    time.sleep(delay)
    return jsonify({"message": f"responded after {delay}s"}), 200


@app.route("/downstream", methods=["GET"])
def downstream_failure():
    """Simulate failures returned by a downstream dependency."""
    mode = request.args.get("mode", "random")
    if mode == "502":
        return jsonify({"error": "bad gateway from downstream"}), 502
    if mode == "503":
        return jsonify({"error": "downstream service unavailable"}), 503
    if mode == "504":
        return jsonify({"error": "gateway timeout from downstream"}), 504

    code = random.choice([200, 200, 502, 503, 504])
    if code == 200:
        return jsonify({"message": "downstream ok"}), 200
    return jsonify({"error": f"downstream returned {code}"}), code


@app.route("/bulk-payments", methods=["POST"])
def bulk_payments():
    """
    Process multiple payments in one call. Some may succeed, some fail.
    Demonstrates partial failure handling.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      207:
        description: Multi-status response
    """
    data = request.get_json(silent=True) or {}
    items = data.get("payments", [])
    if not isinstance(items, list):
        return jsonify({"error": "payments must be a list"}), 422

    results = []
    for idx, item in enumerate(items):
        # Every third item fails deterministically for demo purposes.
        if idx % 3 == 2:
            results.append({"index": idx, "status": "failed", "error": "simulated processing failure"})
            continue
        try:
            payment = validate_payment_create(item)
        except ValidationError as exc:
            results.append({"index": idx, "status": "failed", "error": exc.errors})
            continue

        payment_id = _generate_payment_id()
        amount = payment["amount"]
        fee = _round_money(amount * Decimal("0.029")) + Decimal("0.30")
        payments[payment_id] = {
            "id": payment_id,
            "status": PaymentStatus.AUTHORIZED,
            "amount": amount,
            "currency": payment["currency"],
            "fee": fee,
            "net_amount": _round_money(amount - fee),
            "merchant_id": payment["merchant_id"],
            "description": payment["description"],
            "idempotency_key": None,
            "exchange_rate": None,
            "settled_at": None,
            "created_at": time.time(),
        }
        results.append({"index": idx, "status": "created", "payment_id": payment_id})

    return jsonify({"results": results}), 207


# ---------- Concurrency / race condition demo ----------


@app.route("/wallets/<wallet_id>/race", methods=["POST"])
def race_debit_wallet(wallet_id):
    """
    Debit endpoint without a lock to demonstrate race conditions.
    Not thread-safe on purpose — use for concurrency testing only.
    """
    data = request.get_json(silent=True) or {}
    try:
        amount = Decimal(str(data.get("amount")))
    except Exception:
        return jsonify({"error": "amount must be a valid decimal"}), 422
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 422

    wallet = wallets.get(wallet_id)
    if not wallet:
        return _not_found("wallet")

    # Intentionally read -> check -> write without a lock.
    if wallet["balance"] < amount:
        return jsonify({"error": "insufficient funds"}), 422
    # Small artificial delay to make race conditions more likely under load.
    time.sleep(0.05)
    wallet["balance"] = _round_money(wallet["balance"] - amount)
    wallet["version"] += 1

    return jsonify({"wallet_id": wallet_id, "balance": str(wallet["balance"]), "version": wallet["version"]}), 200


# ---------- Backward compatibility ----------


@app.route("/v1/users", methods=["GET"])
def users_v1():
    """Legacy response format: flat list, no pagination metadata."""
    return jsonify(list(users.values())), 200


@app.route("/v2/users", methods=["GET"])
def users_v2():
    """New response format: paginated, with metadata."""
    return _paginate(list(users.values()))


# ------------------------------------------------------------------
# File upload
# ------------------------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    if not request.files:
        return jsonify({"error": "no file part"}), 400

    extra_fields = request.form.to_dict()
    files_info = {}

    for field_name, uploaded in request.files.items():
        if uploaded.filename == "":
            continue

        content = uploaded.read().decode("utf-8", errors="ignore")
        size = len(content.encode("utf-8"))

        # Example server-side size check: reject files larger than 1 KB.
        if size > 1024:
            return jsonify({
                "error": "file too large",
                "filename": uploaded.filename,
                "maxSize": 1024,
                "received": size,
            }), 413

        # Example extension check: reject executables.
        filename = uploaded.filename.lower()
        if filename.endswith((".exe", ".bat", ".sh", ".cmd")):
            return jsonify({
                "error": "file type not allowed",
                "filename": uploaded.filename,
            }), 415

        files_info[field_name] = {
            "filename": uploaded.filename,
            "size": size,
            "contentType": uploaded.content_type,
        }

    if not files_info:
        return jsonify({"error": "no valid files"}), 400

    return jsonify({
        "files": files_info,
        "fields": extra_fields,
        "saved": True,
    }), 200


# ------------------------------------------------------------------
# Rate limiting
# ------------------------------------------------------------------
def _rate_limit_headers(remaining, reset):
    headers = {
        "X-RateLimit-Limit": str(rate_limit_max_requests),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(reset)),
    }
    return headers


@app.route("/rate-limit-headers", methods=["GET"])
def rate_limit_headers():
    """Always return rate limit headers without counting toward the limit."""
    response = jsonify({"message": "ok"})
    response.status_code = 200
    for name, value in _rate_limit_headers(rate_limit_max_requests, time.time() + rate_limit_window).items():
        response.headers[name] = value
    return response


@app.route("/rate-limited", methods=["GET"])
def rate_limited():
    client_ip = request.remote_addr
    now = time.time()

    # Remove entries outside the current window.
    window_start = now - rate_limit_window
    rate_limit_log[client_ip] = [ts for ts in rate_limit_log.get(client_ip, []) if ts > window_start]

    if len(rate_limit_log[client_ip]) >= rate_limit_max_requests:
        response = jsonify({"error": "too many requests"})
        response.status_code = 429
        response.headers["Retry-After"] = str(int(rate_limit_window))
        for name, value in _rate_limit_headers(0, now + rate_limit_window).items():
            response.headers[name] = value
        return response

    rate_limit_log[client_ip].append(now)

    remaining = rate_limit_max_requests - len(rate_limit_log[client_ip])
    response = jsonify({"message": "ok"})
    response.status_code = 200
    for name, value in _rate_limit_headers(remaining, now + rate_limit_window).items():
        response.headers[name] = value
    return response


# ------------------------------------------------------------------
# Authentication demo
# ------------------------------------------------------------------
@app.route("/protected", methods=["GET"])
def protected_resource():
    """
    Protected resource requiring an API key in the X-API-Key header.
    ---
    parameters:
      - name: X-API-Key
        in: header
        type: string
        required: true
    responses:
      200:
        description: Authorized
      401:
        description: Missing or invalid API key
    """
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"message": "protected data", "apiKeyValid": True}), 200


@app.route("/auth/basic", methods=["GET"])
def basic_auth_resource():
    """
    Protected resource using HTTP Basic Authentication.
    ---
    responses:
      200:
        description: Authenticated
      401:
        description: Missing or invalid credentials
    """
    auth = request.authorization
    if not auth:
        response = jsonify({"error": "missing basic auth credentials"})
        response.status_code = 401
        response.headers["WWW-Authenticate"] = 'Basic realm="Login Required"'
        return response

    user = USERS_AUTH.get(auth.username)
    if not user or not check_password_hash(user["password"], auth.password):
        response = jsonify({"error": "invalid credentials"})
        response.status_code = 401
        response.headers["WWW-Authenticate"] = 'Basic realm="Login Required"'
        return response

    return jsonify({"username": auth.username, "authenticated": True}), 200


@app.route("/auth/login", methods=["POST"])
def login():
    """
    Exchange username/password for a bearer token.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Token issued
      401:
        description: Invalid credentials
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    user = USERS_AUTH.get(username)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "invalid credentials"}), 401

    token = _issue_token(username, user["role"])
    return jsonify({"access_token": token, "token_type": "bearer"}), 200


@app.route("/profile", methods=["GET"])
def profile():
    """
    Protected resource requiring a valid Bearer token.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
    responses:
      200:
        description: Profile returned
      401:
        description: Missing or invalid token
    """
    payload = _verify_bearer_token()
    if not payload:
        return jsonify({"error": "missing or invalid bearer token"}), 401
    return jsonify({"username": payload["sub"], "role": payload["role"]}), 200


@app.route("/admin", methods=["GET"])
def admin_dashboard():
    """
    Admin-only resource requiring a Bearer token with role=admin.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
    responses:
      200:
        description: Admin data
      401:
        description: Missing or invalid token
      403:
        description: Insufficient privileges
    """
    payload = _verify_bearer_token()
    if not payload:
        return jsonify({"error": "missing or invalid bearer token"}), 401
    if payload.get("role") != "admin":
        return jsonify({"error": "forbidden"}), 403
    return jsonify({"message": "admin data", "user": payload["sub"]}), 200


# ------------------------------------------------------------------
# Status code simulator
# ------------------------------------------------------------------
@app.route("/status/<int:code>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def status_code(code):
    if code == 429:
        response = jsonify({"error": "too many requests"})
        response.headers["Retry-After"] = "10"
    else:
        response = jsonify({"status": code})
    response.status_code = code
    return response


# ------------------------------------------------------------------
# Error handlers
# ------------------------------------------------------------------
@app.errorhandler(404)
def not_found(error):
    """Return JSON instead of HTML for 404 errors."""
    return jsonify({"error": "resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Return JSON instead of HTML for 500 errors."""
    return jsonify({"error": "internal server error"}), 500


@app.after_request
def add_cors_headers(response):
    """Allow local cross-origin requests during demos."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-API-Key"
    return response


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=False)
