from improv.actor import Actor, RunManager
from datetime import date  # used for saving
import numpy as np
import logging
import time  # Importing time module for the delay

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Generator(Actor):
    """Sample actor to generate data to pass into a sample processor.

    Intended for use along with sample_processor.py.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None
        self.name = "Generator"
        self.frame_num = 0

    def __str__(self):
        return f"Name: {self.name}, Data: {self.data}"

    def setup(self):
        """Generates an array that serves as an initial source of data.

        Initial array is a 100 row, 5 column numpy matrix that contains
        integers from 1-99, inclusive.
        """

        logger.info("Beginning setup for Generator")
        self.data = np.random.randint(10, size=(1, 5))  # Initialize data
        logger.info("Completed setup for Generator")

    def stop(self):
        """Save current randint vector to a file."""

        logger.info("Generator stopping")
        np.save("sample_generator_data.npy", self.data)
        return 0

    def runStep(self):
        """Generates additional data after initial setup data is exhausted.

        Data is a 5x1 vector uniformly distributed in [1, 10].
        """

        time.sleep(0.5)  # Delay for half a second

        if self.frame_num < np.shape(self.data)[0]:
            data_id = self.client.put(
                self.data[self.frame_num], str(f"Gen_raw: {self.frame_num}")
            )
            try:
                self.q_out.put([[data_id, str(self.frame_num)]])
                logger.info("Sent message on")
                self.frame_num += 1
            except Exception as e:
                logger.error(f"--------------------------------Generator Exception: {e}")
        else:
            new_data = np.random.randint(10, size=(1, 5))
            self.data = np.concatenate((self.data, new_data), axis=0)
