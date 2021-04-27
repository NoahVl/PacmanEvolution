# Noah van der Vleuten (s1018323)
# Jozef Coldenhoff (s1017656)

import albertHeijn  # contains AlbertHeijn class definition


def permutations(elements: list, current=None) -> list:
    """
    Given a list of elements, recursively calculate all possible orderings of those elements.
    For example given three elements A, B and C, the result is:
    [[A, B, C], [A, C, B], [B, A, C], [B, C, A], [C, A, B], [C, B, A]]
    :param elements: (list) the list of elements
    :param current: (list) the list that is currently being recursively constructed
    :returns: (list) all permutations
    """
    if current is None:
        current = []
    orderings = []
    if len(elements) == 0:  # if there are no more elements to add:
        orderings.append(current.copy())  # add a copy of the current ordering to the list of orderings
    for i in range(len(elements)):  # for each index in remaining elements, do:
        current.append(
            elements.pop(i))  # prepare: move the element at the index from the remaining list to the current ordering
        orderings += permutations(elements, current)  # recursively generate all following orderings
        # repair: move the element from the current ordering back to the index on the remaining list
        elements.insert(i, current.pop())
    return orderings  # return all generated orderings


def path_distance(ahpath: list) -> float:
    """
    Given a path (list) of Albert Heijns, return the total distance of the path.
    :param ahpath: (list) a list of Albert Heijns
    :returns: (float) the total distance of the path
    """
    total_dist = 0
    for i in range(1, len(ahpath)):  # 'i' starts at 1, ends at last index of 'ahpath'
        total_dist += albertHeijn.distance(ahpath[i - 1].position(), ahpath[i].position())
    return total_dist

# some Albert Heijns in Nijmegen
albertheijns = [
    albertHeijn.AlbertHeijn('Daalseweg', 85, 77),
    albertHeijn.AlbertHeijn('Groenestraat', 68, 69),
    albertHeijn.AlbertHeijn('van Schevichavenstraat', 79, 83),
    albertHeijn.AlbertHeijn('St. Jacobslaan', 70, 58),
    albertHeijn.AlbertHeijn('Stationsplein', 70, 82)
]


def main():
    shop_size = len(albertheijns)

    # print the path along all Albert Heijns with the minimum total distance
    # start by generating all possible paths along all Albert Heijns
    paths = permutations(albertheijns)

    # take the minimum of the paths, using the path distance function to compare paths
    min_distance_path = min(paths, key=path_distance)

    # print the index (starting at 1) followed by the name of each Albert Heijn in the path
    for i, ah in enumerate(min_distance_path):
        print(i + 1, ah.name)


if __name__ == '__main__':
    main()
