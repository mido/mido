Frozen Messages
---------------

(New in 1.2.)

Since Mido messages are mutable (can change) they can not be hashed or
put in dictionaries. This makes it hard to use them for things like
Markov chains.

In these situations you can use frozen messages:

.. code-block:: python

    from mido.frozen import FrozenMessage

    msg = FrozenMessage('note_on')
    d = {msg: 'interesting'}

Frozen messages are used and behave in exactly the same way as normal
messages with one exception: attributes are not settable.

There are also variants for meta messages (``FrozenMetaMessage`` and
``FrozenUnknownMetaMessage``).

You can freeze and thaw messages with:

.. code-block:: python

    from mido.frozen import freeze_message, thaw_message

    frozen = freeze_message(msg)
    thawed = thaw_message(frozen)

``thaw_message()`` will always return a copy. Passing a frozen message
to ``freeze_message()`` will return the original message.

Both functions return ``None`` if you pass ``None`` which is handy for
things like:

.. code-block:: python

    msg = freeze_message(port.receive())

    # Python 3 only:
    for msg in map(freeze_message, port):
        ...

    # Python 2 and 3:
    for msg in (freeze_message(msg) for msg in port):
        ...

To check if a message is frozen:

.. code-block:: python

    from mido.frozen import is_frozen

    if is_frozen(msg):
        ...

