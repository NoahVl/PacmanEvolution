# Noah van der Vleuten (s1018323)
# Jozef Coldenhoff (s1017656)

import exceptions
import shop


def shop_loop(fruit: str):
    """
    Prints the same output as running `python shop.py` when called as "shop_loop('apples')".
    A for-loop is used for iterating over shops.
    This function does not have a returnvalue.
    :param fruit: (str) name of a fruit
    """
    shop_names = ['Aldi', 'Albert Heijn']
    shop_prices = [{'apples': 1.00, 'oranges': 1.50, 'pears': 1.75},
                   {'kiwis': 6.00, 'apples': 4.50, 'peaches': 8.75}]

    for index, store in enumerate(shop_names):
        new_shop = shop.FruitShop(store, shop_prices[index])
        shop_fruit = new_shop.cost_per_unit(fruit)
        print(f'{fruit.title()} cost €{shop_fruit:.2f} at {new_shop.name}.')



if __name__ == '__main__':
    shop_loop('apples')
