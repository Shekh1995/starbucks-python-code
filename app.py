
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import os

from data import (
    HANDCRAFTED_CURATIONS,
    PROMOTION_BANNERS,
    BARISTA_RECOMMENDS,
    ALL_MENU_ITEMS,
    GIFT_CARDS,
    STORES,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title='Starbucks Coffee India - Python Edition',
    description='Full-stack Python & FastAPI implementation of Starbucks Web App',
    version='1.0.0'
)

# Mount static directory for images and CSS
app.mount('/static', StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name='static')

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))

# In-memory Cart Storage (Session-like mock)
CART = []
USER_PAY_ACCOUNT = {
    'card_number': '6041 8888 7777 8821',
    'card_holder': 'Valued Starbucks Member',
    'stars': 125,
    'balance': 850.50,
    'tier': 'Gold Level'
}

class CartItemRequest(BaseModel):
    item_id: str
    quantity: int = 1

class TopUpRequest(BaseModel):
    amount: float

@app.get('/', response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request, 'home.html', {
        'request': request,
        'active_nav': 'home',
        'curations': HANDCRAFTED_CURATIONS,
        'banners': PROMOTION_BANNERS,
        'recommends': BARISTA_RECOMMENDS,
        'cart_count': sum(i['quantity'] for i in CART)
    })

@app.get('/ordering', response_class=HTMLResponse)
async def order_page(request: Request, cat: Optional[str] = Query(None)):
    categories = [
        {'id': 'all', 'label': 'All Items'},
        {'id': 'bestseller', 'label': 'Bestseller'},
        {'id': 'drinks', 'label': 'Drinks'},
        {'id': 'food', 'label': 'Food'},
        {'id': 'merchandise', 'label': 'Merchandise'},
        {'id': 'coffeeathome', 'label': 'Coffee At Home'},
        {'id': 'readytoeat', 'label': 'Ready to Eat'}
    ]
    
    selected_cat = cat if cat in [c['id'] for c in categories] else 'all'
    
    if selected_cat == 'all':
        filtered_items = ALL_MENU_ITEMS
    elif selected_cat == 'bestseller':
        filtered_items = BARISTA_RECOMMENDS
    else:
        filtered_items = [item for item in ALL_MENU_ITEMS if item.get('category') == selected_cat]

    return templates.TemplateResponse(request, 'order.html', {
        'request': request,
        'active_nav': 'order',
        'categories': categories,
        'selected_cat': selected_cat,
        'items': filtered_items,
        'cart': CART,
        'cart_count': sum(i['quantity'] for i in CART)
    })

@app.get('/giftcards', response_class=HTMLResponse)
async def gift_page(request: Request):
    return templates.TemplateResponse(request, 'gift.html', {
        'request': request,
        'active_nav': 'gift',
        'gift_cards': GIFT_CARDS,
        'cart_count': sum(i['quantity'] for i in CART)
    })

@app.get('/pay', response_class=HTMLResponse)
async def pay_page(request: Request):
    return templates.TemplateResponse(request, 'pay.html', {
        'request': request,
        'active_nav': 'pay',
        'account': USER_PAY_ACCOUNT,
        'cart_count': sum(i['quantity'] for i in CART)
    })

@app.get('/store', response_class=HTMLResponse)
async def store_page(request: Request):
    return templates.TemplateResponse(request, 'store.html', {
        'request': request,
        'active_nav': 'store',
        'stores': STORES,
        'cart_count': sum(i['quantity'] for i in CART)
    })

@app.get('/search', response_class=HTMLResponse)
async def search_page(request: Request, q: Optional[str] = ''):
    query = (q or '').strip().lower()
    if query:
        results = [
            i for i in ALL_MENU_ITEMS 
            if query in i['title'].lower() or query in i.get('description', '').lower()
        ]
    else:
        results = ALL_MENU_ITEMS[:6]

    return templates.TemplateResponse(request, 'search.html', {
        'request': request,
        'active_nav': 'search',
        'query': q or '',
        'results': results,
        'cart_count': sum(i['quantity'] for i in CART)
    })

# --- REST API Endpoints ---

@app.get('/api/menu')
async def api_get_menu(category: Optional[str] = None):
    if category:
        return [i for i in ALL_MENU_ITEMS if i.get('category') == category]
    return ALL_MENU_ITEMS

@app.get('/api/cart')
async def api_get_cart():
    total = sum(i['price'] * i['quantity'] for i in CART)
    return {
        'items': CART,
        'count': sum(i['quantity'] for i in CART),
        'total': round(total, 2)
    }

@app.post('/api/cart/add')
async def api_add_to_cart(payload: CartItemRequest):
    item = next((i for i in ALL_MENU_ITEMS if i['id'] == payload.item_id), None)
    if not item:
        return JSONResponse(status_code=404, content={'error': 'Item not found'})

    existing = next((i for i in CART if i['id'] == payload.item_id), None)
    if existing:
        existing['quantity'] += payload.quantity
    else:
        CART.append({
            'id': item['id'],
            'title': item['title'],
            'price': item['price'],
            'img': item['img'],
            'quantity': payload.quantity
        })
    total = sum(i['price'] * i['quantity'] for i in CART)
    return {'status': 'success', 'count': sum(i['quantity'] for i in CART), 'total': round(total, 2), 'cart': CART}

@app.post('/api/cart/remove')
async def api_remove_from_cart(payload: CartItemRequest):
    global CART
    CART = [i for i in CART if i['id'] != payload.item_id]
    total = sum(i['price'] * i['quantity'] for i in CART)
    return {'status': 'success', 'count': sum(i['quantity'] for i in CART), 'total': round(total, 2), 'cart': CART}

@app.post('/api/cart/clear')
async def api_clear_cart():
    global CART
    CART.clear()
    return {'status': 'success', 'count': 0, 'total': 0.0, 'cart': []}

@app.post('/api/pay/topup')
async def api_topup_balance(payload: TopUpRequest):
    if payload.amount <= 0:
        return JSONResponse(status_code=400, content={'error': 'Invalid amount'})
    USER_PAY_ACCOUNT['balance'] += payload.amount
    return {'status': 'success', 'new_balance': round(USER_PAY_ACCOUNT['balance'], 2)}

@app.get('/api/stores')
async def api_get_stores():
    return STORES

if __name__ == '__main__':
    import uvicorn
    print('Starting Starbucks Python Server at http://127.0.0.1:8000 ...')
    uvicorn.run('app:app', host='127.0.0.1', port=8000, reload=True)
