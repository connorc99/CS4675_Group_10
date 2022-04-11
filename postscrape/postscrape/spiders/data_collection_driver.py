from itertools import product
from multiple_spiders import crawl
import datetime

import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)


subprocesses_counts = [1, 2, 4]
initial_depths = [2, 3]
filter_depths = [5, 8]
max_depths = [10, 15]

# subprocesses_counts = [2]
# initial_depths = [2]
# filter_depths = [5]
# max_depths = [10]
NAME_OF_THIS_MACHINE = "Cys_2015_MacBook_Pro"

params_list = product(subprocesses_counts, initial_depths, filter_depths, max_depths)

for params in params_list:

    number_of_failures = 0
    iteration = 0
    print("\n\n---------------------\nRUNNING MAIN FILE: {}\n\n\n------------------------------".format(iteration))
    iteration += 1

    subprocesses, initial_depth, filter_depth, max_depth = params
    start = datetime.datetime.now()
    response = crawl(subprocesses, initial_depth, filter_depth, max_depth, NAME_OF_THIS_MACHINE)
    end = datetime.datetime.now()
    logging.debug("start:" + str(start) + "end:" + str(end))