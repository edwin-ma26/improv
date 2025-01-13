from improv.actor import Actor
from queue import Empty
import logging
import zmq
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Processor(Actor):
    """
    Process data and send it through zmq to be visualized.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        """
        Creates and binds the socket for zmq.
        """
        self.name = "Processor"

        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://127.0.0.1:5555")

        logger.info("Completed setup for Processor")

    def stop(self):
        logger.info("Processor stopping")
        self.socket.close()
        return 0

    def runStep(self):
        """
        Receives data from the queue, prepares 2D data with x and y coordinates,
        and sends it through the socket along with the frame number.
        """
        try:
            # Retrieve data from the queue
            frame = self.q_in.get(timeout=0.05)
        except Empty:
            return  # No data received, skip this step
        except Exception as e:
            logger.error(f"Error retrieving frame: {e}")
            return

        if frame is not None:
            try:
                # Fetch the dictionary from the data store
                data_dict = self.client.getID(frame[0][0])

                # Extract frame number and values (2D array with x and y)
                frame_num = data_dict["frame_num"]
                values = data_dict["values"]  # Shape (N, 2), with columns [x, y]

                # Combine frame number and flattened data into a single array
                flat_data = np.concatenate(([frame_num], values.ravel())).astype(np.float64)

                # Send the serialized buffer through the socket
                self.socket.send(flat_data.tobytes())
                logger.info(f"Frame {frame_num}: Sent {values.shape[0]} points")

            except Exception as e:
                logger.error(f"Error processing frame: {e}")
