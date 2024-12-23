from improv.actor import Actor
from queue import Empty
import logging
import zmq
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lorenz(xyz, s=10, r=28, b=2.667):
    """
    Parameters
    ----------
    xyz : array-like, shape (3,)
       Point of interest in three-dimensional space.
    s, r, b : float
       Parameters defining the Lorenz attractor.

    Returns
    -------
    xyz_dot : array, shape (3,)
       Values of the Lorenz attractor's partial derivatives at *xyz*.
    """
    x, y, z = xyz
    x_dot = s * (y - x)
    y_dot = r * x - y - x * z
    z_dot = x * y - b * z
    return np.array([x_dot, y_dot, z_dot])


class Processor(Actor):
    """
    Process data, calculate updated Lorenz coordinates, and send them via ZMQ.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        """
        Creates and binds the socket for ZMQ and initializes the Lorenz system.
        """
        self.name = "lorenz_processor"

        # Set up ZMQ PUB socket
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://127.0.0.1:5555")

        self.frame_num = 1
        self.current_coords = None  # Will be initialized with generator data
        self.dt = 0.01  # Small time step for Euler's method

        logger.info("Completed setup for Processor")

    def stop(self):
        logger.info("Processor stopping")
        self.socket.close()
        return 0

    def runStep(self):
        """
        Receives initial coordinates from the Generator, calculates updated Lorenz coordinates,
        and sends them via ZMQ.
        """
        if self.current_coords is None:
            # Get initial coordinates from the queue
            try:
                frame = self.q_in.get(timeout=0.05)
                data_id = frame[0][0]  # Data ID in the store
                # Fetch data and make a writable copy
                self.current_coords = np.array(self.client.getID(data_id), copy=True)

                logger.info(f"Initialized Lorenz coordinates: {self.current_coords}")

            except Empty:
                logger.info("Waiting for initial Lorenz coordinates...")
                return
            except Exception as e:
                logger.error(f"Failed to initialize Lorenz coordinates: {e}")
                return

        try:
            # Calculate the Lorenz derivatives
            derivatives = lorenz(self.current_coords)

            # Update coordinates using Euler's method
            self.current_coords += derivatives * self.dt
            frame_ix = self.frame_num

            logger.info(f"Frame {frame_ix}: Updated Lorenz coordinates: {self.current_coords}")

            # Combine the updated coordinates and frame index for sending
            out = np.concatenate([self.current_coords, [frame_ix]], dtype=np.float64)

            # Send the data via ZMQ
            self.socket.send(out.tobytes())
            logger.info(f"Sent frame {frame_ix}: {self.current_coords}")

            self.frame_num += 1

        except Exception as e:
            logger.error(f"Error during processing: {e}")


# from improv.actor import Actor
# from queue import Empty
# import logging
# import zmq
# import numpy as np

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


# class Processor(Actor):
#     """
#     Process data and send it through zmq to be visualized in Jupyter Notebook.
#     """

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def setup(self):
#         """
#         Creates and binds the socket for zmq.
#         """
#         self.name = "lorenz_processor"

#         # Set up ZMQ PUB socket
#         context = zmq.Context()
#         self.socket = context.socket(zmq.PUB)
#         self.socket.bind("tcp://127.0.0.1:5555")

#         self.frame_num = 1

#         logger.info("Completed setup for Processor")

#     def stop(self):
#         logger.info("Processor stopping")
#         self.socket.close()
#         return 0

#     def runStep(self):
#         """
#         Fetches data from the queue, processes it, and sends it via ZMQ.
#         """
#         frame = None
#         try:
#             frame = self.q_in.get(timeout=0.05)
#         except Empty:
#             logger.info("Queue is empty; no frame to process.")
#         except Exception as e:
#             logger.error(f"Could not get frame! Exception: {e}")

#         if frame is not None:
#             try:
#                 # Fetch the data from the store
#                 self.frame = self.client.getID(frame[0][0])
#                 coordinates = self.frame.ravel()
#                 frame_ix = self.frame_num

#                 logger.info(f"Retrieved coordinates: {coordinates}")
#                 logger.info(f"Sending frame {frame_ix}")

#                 # Combine the coordinates and frame index for sending
#                 out = np.concatenate([coordinates, [frame_ix]], dtype=np.float64)

#                 # Send the data
#                 self.socket.send(out.tobytes())  # Send as bytes
#                 logger.info(f"Sent frame {frame_ix}: {coordinates}")

#                 self.frame_num += 1

#             except Exception as e:
#                 logger.error(f"Error during processing: {e}")
