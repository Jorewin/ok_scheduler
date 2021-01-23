
def swap_two_random_elements_between_lists(list_1: list, list_2: list):
    index_1 = random.randrange(len(list_1))
    index_2 = random.randrange(len(list_2))
   
    value = list_1[index_1]
    list_1[index_1] = list_2[index_2]
    list_2[index_2] = value

