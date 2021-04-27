# Noah van der Vleuten (s1018323)
# Jozef Coldenhoff (s1017656)

import exceptions

fruit_prices = {'apples': 2.00,
                'oranges': 1.50,
                'pears': 1.75,
                'limes': 0.75,
                'strawberries': 1.00}


def order_price(order: list) -> float:
    """
    Calculate the total price of the order (the sum of the price of each fruit in the order times its amount).
    If any fruit in the order is not in store return None, else return the total price as a real.
    :param order: (list) a list of (fruit, amount) tuples
    :returns: (float) total price unless input invalid then None
    """
    price = 0

    for item, amount in order:
        if item not in fruit_prices:
            return None
        else:
            price += fruit_prices[item] * amount
    return price

"""
BONUS ASSIGNMENT
"""
def quicksort(lst: list) -> list:
    """
    Sort the input list in non-decreasing order by quicksort.
    :param lst: (list) a list of items that have an inherent order (numbers, strings etc.)
    :returns: (list) an ordered version of the input list
    """
    if len(lst) <= 1:
        return lst
    else:
        pivot = lst[0]
        smaller = [i for i in lst[1:] if i <= pivot]
        bigger = [i for i in lst[1:] if i > pivot]
        return quicksort(smaller) + [pivot] + quicksort(bigger)


if __name__ == '__main__':
    order1 = [('apples', 2), ('pears', 3), ('limes', 4)]
    print(f'Cost of {order1} is {order_price(order1)}')

    order2 = [('pears', 2), ('limes', 1), ('strawberries', 10), ('melons', 3)]
    print(f'Cost of {order2} is {order_price(order2)}')

    print("\nSorted on item for bonus:")
    print(quicksort(order1))
    print(quicksort(order2))