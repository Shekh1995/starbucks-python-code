import asyncio
from app import app
from data import ALL_MENU_ITEMS, HANDCRAFTED_CURATIONS

async def test_routes():
    print('Testing Starbucks Python backend...')
    assert len(HANDCRAFTED_CURATIONS) == 6, 'Curations count should be 6'
    assert len(ALL_MENU_ITEMS) >= 10, 'Menu items should have at least 10'
    print('[PASS] Dataset integrity validated')

    routes = [route.path for route in app.routes]
    expected = ['/', '/ordering', '/giftcards', '/pay', '/store', '/search', '/api/menu', '/api/cart', '/api/cart/add']
    for path in expected:
        assert path in routes, f'Route {path} missing in FastAPI app'
        print(f'[PASS] Route confirmed: {path}')

    print('ALL VERIFICATIONS PASSED SUCCESSFULLY!')

if __name__ == '__main__':
    asyncio.run(test_routes())
