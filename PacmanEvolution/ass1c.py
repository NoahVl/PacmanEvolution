# Noah van der Vleuten (s1018323)
# Jozef Coldenhoff (s1017656)

import exceptions
import shop  # contains FruitShop class definition


def shop_smart(order: list, shops: list) -> shop.FruitShop:
    """
    Calculate at which shop the given order is cheapest.
    :param order: (list) a list of (fruit, amount) tuples
    :param shops: (list) a list of FruitShops
    :returns: (shop.FruitShop) the shop that at which the order is cheapest
    """

    total = -1
    new_total = 0
    best_shop = shops[0]

    # Keep track of which shop is cheapest, once another shop is cheaper, assign that one to best_shop.
    for supermarket in shops:
        for item, amount in order:
            new_total += supermarket.cost_per_unit(item) * amount
        if (new_total < total) | (total == -1):
            best_shop = supermarket
            total = new_total
        new_total = 0

    return best_shop



def main():
    fruits1 = {'apples': 2.0, 'oranges': 1.0}
    fruits2 = {'apples': 1.0, 'oranges': 5.0}
    shop1 = shop.FruitShop('shop1', fruits1)
    shop2 = shop.FruitShop('shop2', fruits2)
    shops = [shop1, shop2]
    order1 = [('apples', 1.0), ('oranges', 3.0)]
    order2 = [('apples', 3.0)]
    print(f'For order {order1} the best shop is {shop_smart(order1, shops).name}.')
    print(f'For order {order2} the best shop is {shop_smart(order2, shops).name}.')


if __name__ == '__main__':
    main()
