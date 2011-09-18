"""
This file contains some doodling on a standard API for
MIDI I/O.

The 'dev' paramenter to Input/Output is an implementation specific
device identifier. 
"""

#
# Base classes
#

class Input:
    """
    Functionality it should provide:

    - check if there is anything to read
    - get a messages
    - get all messages (iter)

    - message handlers?

    Implementation specific?

    - filtering (or maybe this should be handled by base class)
    - channel mask
    """

    def __init__(self, dev):
        pass

    def poll(self):
        """
        

        Return number of pending messages, or just True if
        there may be data on the input?
        
        Perhaps best to be conservative. Most implementations will not
        be able to tell how many messages are available without actually
        reading.
        """

    def recv(self):
        """
        Return the next pending message, or None
        if no messages are available.
        """

    def __iter__(self):
        """
        Yield all pending messages.
        """
        pass

    #
    # Message handlers
    #

    def dispatch(self):
        """
        Dispatch any pending messages to handlers.
        """
        pass

    def add_handler(self, predicate, handler):
        """
        predicate is a method that takes a message and
        returns True if the handler will handle it.
        
        handler is a handler that takes a message.

        Example:

            def print_msg(msg):
                print(msg)

            is_notemsg = lambda msg: msg.type in ['note_on', 'note_off']
            input.add_handler(is_notemsg, print_msg)
        """
        pass

class Output:
    def __init__(self, dev):
        pass

    def send(self, msg):
        """
        Send message to output.
        """
        pass
