from improv.actor import Actor, RunManager
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
        self.name = "Generator"
        self.frame_num = 0  # Initialize frame counter
        # Generate xs (x-coordinates)
        self.xs = np.linspace(-10, 10, 100)

    def __str__(self):
        return f"Name: {self.name}"

    def setup(self):
        """Initial setup for Generator."""
        logger.info("Beginning setup for Generator")
        logger.info("Completed setup for Generator")

    def stop(self):
        """Actions to perform on stopping."""
        logger.info("Generator stopping")
        return 0

    def runStep(self):
        """Sends a dictionary containing frame number and 2D array with x and y coordinates."""
        time.sleep(0.5)  # Delay for half a second

        # Generate sine or cosine values based on frame number
        if self.frame_num % 2 == 0:
            # Even frame: Generate sine wave
            ys = np.sin(self.xs)
        else:
            # Odd frame: Generate cosine wave
            ys = np.cos(self.xs)

        # Combine x and y into a 2D array
        values = np.column_stack((self.xs, ys))  # Shape (100, 2)

        # Prepare the data to send
        data_to_send = {
            "frame_num": self.frame_num,
            "values": values,  # 2D array with x and y coordinates
        }

        # Send the dictionary
        try:
            data_id = self.client.put(data_to_send, f"Frame: {self.frame_num}")
            self.q_out.put([[data_id, f"Frame: {self.frame_num}"]])
            logger.info(f"Sent frame {self.frame_num} with x and y coordinates")
        except Exception as e:
            logger.error(f"Generator Exception: {e}")

        # Increment frame number
        self.frame_num += 1
