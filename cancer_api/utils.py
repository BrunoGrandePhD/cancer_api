"""
utils.py
========
This submodule contains convenience classes and functions
used in cancer_api internally, but also available for
external usage.
"""

import sys
import logging
import time


def setup_logging():
    """Setup logging in standard format. Once setup,
    simply log messages using the logging module:
        logging.info("Current step: ...")
        logging.warning("Warn user about...")
    """
    log_format = '%(asctime)s - %(levelname)s (%(module)s.%(funcName)s):  %(message)s'
    date_format = '%Y/%m/%d %H:%M:%S'  # 2010/12/12 13:46:36
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt=date_format,
                        stream=sys.stderr)


class Chronometer(object):
    """Convenience class for profiling code.
    Uses the logging module to output times.
    """

    def __init__(self):
        """Set start time"""
        self.start_time = time.time()
        self.last_time = self.start_time
        zero_time = time.time() - time.time()
        self.laps = [("start time", zero_time)]

    def reset(self):
        """Reset start time"""
        self.start_time = time.time()
        self.last_time = self.start_time

    def lap(self, label=""):
        """Record and print time"""
        current_time = time.time()
        delta = current_time - self.last_time
        self.laps.append((label, delta))
        # Set template according to whether a label is specified
        template = "{delta} sec" if label is "" else "{label}: {delta:.8f} sec"
        logging.info(template.format(label=label, delta=delta))
        self.last_time = current_time
