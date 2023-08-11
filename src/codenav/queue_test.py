"""
module docstring here
"""

import time
import logging


def main():
    logging.basicConfig(
        format="    %(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
        level=logging.INFO,
    )
    logger = logging.getLogger("printlog")
    timestep = 0.02
    for i in range(100):
        time.sleep(timestep)
        logger.info("queue_test_index: %s" % (i))
    logger.info("queue_total_time: %s" % (timestep*100))
    # raise FileExistsError("dis for testing lol")
    # extra comment here

main()
