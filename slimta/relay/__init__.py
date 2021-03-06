# Copyright (c) 2012 Ian C. Good
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""Root package for relaying messages to their next destination. A relay could
be another SMTP hop, or it could be implemented as a final delivery mechanism.

"""

from slimta import SlimtaError
from slimta.policy import RelayPolicy

__all__ = ['PermanentRelayError', 'TransientRelayError', 'Relay']


class RelayError(SlimtaError):
    def __init__(self, msg, reply):
        super(RelayError, self).__init__(msg)
        self.reply = reply


class PermanentRelayError(RelayError):
    """Base exception for all relay errors that indicate a message will not
    be successfully delivered no matter how many times delivery is attempted.

    """
    pass


class TransientRelayError(RelayError):
    """Base exception for all relay errors that indicate the message may be
    successful if tried again later.

    """
    pass


class Relay(object):
    """Base class for objects that implement the relaying pattern. Included
    implementations are :class:`~slimta.relay.smtp.mx.MxSmtpRelay` and
    :class:`~slimta.relay.smtp.static.StaticSmtpRelay`.

    """

    def __init__(self):
        self.relay_policies = []

    def add_policy(self, policy):
        """Adds a |RelayPolicy| to be executed each time the relay attempts
        delivery for a message.

        :param policy: |RelayPolicy| object to execute.

        """
        if isinstance(policy, RelayPolicy):
            self.relay_policies.append(policy)
        else:
            raise TypeError('Argument not a RelayPolicy.')

    def _run_policies(self, envelope):
        for policy in self.relay_policies:
            policy.apply(envelope)

    def _attempt(self, envelope, attempts):
        self._run_policies(envelope)
        return self.attempt(envelope, attempts)

    def attempt(self, envelope, attempts):
        """This method must be overriden by sub-classes in order to be passed
        in to the |Queue| constructor.

        :param envelope: |Envelope| to attempt delivery for.
        :param attempts: Number of times the envelope has attempted delivery.
        :raises: :class:`PermanentRelayError`, :class:`TransientRelayError`

        """
        raise NotImplementedError()


# vim:et:fdm=marker:sts=4:sw=4:ts=4
