from improv.actor import Actor, RunManager
from datetime import date  # used for saving
import numpy as np
import logging
import time  # Importing time module for the delay

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Generator(Actor):
    """
    Generates the initial coordinates for the Lorenz system.
    Intended to provide initial data for the LorenzProcessor.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None
        self.name = "lorenz_generator"
        self.frame_num = 0

    def __str__(self):
        return f"Name: {self.name}, Data: {self.data}"

    def setup(self):
        """
        Initializes the Lorenz system with the starting coordinates.
        """
        logger.info("Beginning setup for LorenzGenerator")
        self.data = np.array([[1.0, 1.0, 1.0]])  # Initial coordinates (x, y, z)
        logger.info(f"Initialized Lorenz system with coordinates: {self.data}")

    def stop(self):
        """
        Save the current Lorenz coordinates to a file for persistence.
        """
        logger.info("LorenzGenerator stopping")
        np.save("lorenz_initial_data.npy", self.data)
        return 0

    def runStep(self):
        """
        Sends the initial Lorenz system coordinates.
        """
        time.sleep(0.5)  # Delay for half a second

        if self.frame_num < np.shape(self.data)[0]:
            data_id = self.client.put(
                self.data[self.frame_num], str(f"Lorenz_Initial: {self.frame_num}")
            )
            try:
                self.q_out.put([[data_id, str(self.frame_num)]])
                logger.info(f"Sent initial Lorenz coordinate: {self.data[self.frame_num]}")
                self.frame_num += 1
            except Exception as e:
                logger.error(f"LorenzGenerator Exception: {e}")
