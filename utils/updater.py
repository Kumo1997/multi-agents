# utils/updater.py
import random

def update_shop_prices(food_shops, price_variation=2):
    """Randomly adjust shop prices slightly each day."""
    for shop_name, shop_info in food_shops.items():
        change = random.randint(-price_variation, price_variation)
        new_cost = max(1, shop_info["cost"] + change)
        shop_info["cost"] = new_cost