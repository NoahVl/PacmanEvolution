class FruitShop:
    """
    A class to represent a fruitshop, with a name and a dictionary mapping fruits to prices.
    E.g. {'apples': 2.00, 'oranges': 1.50, 'pears': 1.75}
    """

    def __init__(self, name, prices):
        print(f'Welcome to {name} fruit shop.')
        self.prices = prices
        self.name = name

    def cost_per_unit(self, fruit):
        if fruit not in self.prices:
            print(f"Sorry, we don't have {fruit}.") # Note the double quotes because of don't
            return None
        return self.prices[fruit]

if __name__ == '__main__':
    aldi_name = 'Aldi'
    aldi_prices = {'apples': 1.00, 'oranges': 1.50, 'pears': 1.75}
    aldi_shop = FruitShop(aldi_name, aldi_prices)
    aldi_apples = aldi_shop.cost_per_unit('apples')
    print(f'Apples cost €{aldi_apples:.2f} at {aldi_shop.name}.')

    albert_name = 'Albert Heijn'
    albert_prices = {'kiwis': 6.00, 'apples': 4.50, 'peaches': 8.75}
    albert_shop = FruitShop(albert_name, albert_prices)
    albert_apples = albert_shop.cost_per_unit('apples')
    print(f'Apples cost €{albert_apples:.2f} at {albert_shop.name}.')
