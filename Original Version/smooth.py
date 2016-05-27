import numpy
import random
from bisect import bisect


def weighted_choice(choices):
    values, weights = zip(*choices)
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)
    x = random.random() * total
    i = bisect(cum_weights, x)
    return values[i]


#using numpy, determine the Euclidean distance between the vectors, float
def dist(p, q):
    return numpy.linalg.norm(numpy.array(p)-numpy.array(q))


def identity_tuples(n):
    # Identity matrix as a list of tuples
    return map(tuple, list(numpy.identity(n, int)))


def smooth(p, gendrop=False, equalcase=False):
    '''
    Error smoothing function
    Takes the vector output by the neural network
    Partitions it into the relevant datasets
    Converts those partitions to the closest unit vectors
    '''
    # partition the input vector into gender, declension
    gender = p[0:3]
    declension = p[3:8]
    case = p[8:11]
    numbers = p[11:13]

    # Determine the dimension of the vectors
    gender_dimension = len(gender)
    declension_dimension = len(declension)
    case_dimension = len(case)
    number_dimension = len(numbers)

    # Modified identity matrix
    gender_space = identity_tuples(gender_dimension)
    declension_space = identity_tuples(declension_dimension)
    number_space = identity_tuples(number_dimension)
    case_space = identity_tuples(case_dimension)

    # Dictionaries keyed by the distance from the given value to the closest unit vector, valued by those unit vectors
    genders = {dist(gender, gender_space[i]): gender_space[i] for i in range(gender_dimension)}
    decs = {dist(declension, declension_space[i]): declension_space[i] for i in range(declension_dimension)}
    nums = {dist(numbers, number_space[i]): number_space[i] for i in range(number_dimension)}

    if not equalcase:
        case_vectors = [
            # nom
            (1, 0, 0),
            # acc
            (1, 1, 0),
            # gen
            (1, 1, 1)
        ]

        cases = {dist(case, tup): tup for tup in case_vectors}
    else:
        cases = {dist(case, case_space[i]): case_space[i] for i in range(case_dimension)}

    if gendrop:
        # delete the genitive
        cases = {key: value for key, value in cases.iteritems() if value not in [(1, 1, 1), (0, 1, 0)]}

    smoothed_vectors = [
        genders[min(genders.keys())],
        decs[min(decs.keys())],
        cases[min(cases.keys())],
        nums[min(nums.keys())]
    ]
    # print smoothed_vectors

    # flatten to one list
    return [item for vector in smoothed_vectors for item in vector]


def gendrop_smooth(p):
    return smooth(p, gendrop=False, equalcase=True)


def equalcase_smooth(p):
    return smooth(p, gendrop=False, equalcase=True)


def equalcase_gendrop_smooth(p):
    return smooth(p, gendrop=True, equalcase=True)
