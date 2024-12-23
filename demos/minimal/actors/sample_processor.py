# from improv.actor import Actor
# import numpy as np
# import logging

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


# class Processor(Actor):
#     """Sample processor used to calculate the average of an array of integers.

#     Intended for use with sample_generator.py.
#     """

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def setup(self):
#         """Initializes all class variables.

#         self.name (string): name of the actor.
#         self.frame (ObjectID): StoreInterface object id referencing data from the store.
#         self.avg_list (list): list that contains averages of individual vectors.
#         self.frame_num (int): index of current frame.
#         """

#         self.name = "Processor"
#         self.frame = None
#         self.avg_list = []
#         self.frame_num = 1
#         logger.info("Completed setup for Processor")

#     def stop(self):
#         """Trivial stop function for testing purposes."""

#         logger.info("Processor stopping")

#     def runStep(self):
#         """Gets from the input queue and calculates the average.

#         Receives an ObjectID, references data in the store using that
#         ObjectID, calculates the average of that data, and finally prints
#         to stdout.
#         """

#         frame = None
#         try:
#             frame = self.q_in.get(timeout=0.001)

#         except:
#             logger.error("Could not get frame!")
#             pass

#         if frame is not None and self.frame_num is not None:
#             self.done = False
#             self.frame = self.client.getID(frame[0][0])
#             avg = np.mean(self.frame[0])

#             # print(f"Average: {avg}")
#             self.avg_list.append(avg)
#             # print(f"Overall Average: {np.mean(self.avg_list)}")
#             # print(f"Frame number: {self.frame_num}")
#             self.frame_num += 1


from improv.actor import Actor
from queue import Empty
import logging;

logger = logging.getLogger(__name__)
import zmq

logger.setLevel(logging.INFO)
import numpy as np


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

        self.frame_num = 1

        logger.info('Completed setup for Processor')

    def stop(self):
        logger.info("Processor stopping")
        self.socket.close()
        return 0

    def runStep(self):
        """
        Gets the data_id to the store from the queue, fetches the frame from the data store,
        take the mean, sends a memoryview so the zmq subscriber can get the buffer to update
        the plot.
        """

        frame = None

        try:
            frame = self.q_in.get(timeout=0.05)
        except Empty:
            pass
        except:
            logger.error("Could not get frame!")

        if frame is not None:
            # get frame from data store
            self.frame = self.client.getID(frame[0][0])

            # do some processing
            self.frame.mean()

            frame_ix = self.frame_num % 10

            logger.info(self.frame.shape)

            # # send the buffer data and frame number as an array
            out = np.concatenate(
                [self.frame.ravel(), np.array([frame_ix])],  # Convert frame_ix to a 1D array
                dtype=np.float64
            )

            self.frame_num += 1
            self.socket.send(out)
            logger.info(f"Processed and sent frame number {frame_ix}")