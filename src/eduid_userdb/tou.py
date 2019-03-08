#
# Copyright (c) 2015 NORDUnet A/S
# Copyright (c) 2018 SUNET
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
#     3. Neither the name of the NORDUnet nor the names of its
#        contributors may be used to endorse or promote products derived
#        from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Author : Fredrik Thulin <fredrik@thulin.net>
#

from six import string_types

from eduid_userdb.event import Event, EventList
from eduid_userdb.exceptions import BadEvent, EventHasUnknownData


class ToUEvent(Event):
    """
    A record of a user's acceptance of a particular version of the Terms of Use.
    """
    def __init__(self, version, created_by=None, created_ts=None, event_id=None):
        if created_ts is None:
            raise BadEvent('ToUEvent requires created_ts')
        super().__init__(created_by=created_by,
                         created_ts=created_ts,
                         event_type='tou_event',
                         event_id=event_id,
                         )
        self.version = version

    @classmethod
    def from_dict(cls, data):
        _known_data = ['created_by', 'created_ts', 'event_id', 'version', 'event_type']
        _leftovers = [x for x in data.keys() if x not in _known_data]
        if _leftovers:
            raise EventHasUnknownData('ToUEvent has unknown data: {!r}'.format(
                _leftovers,
            ))

        if data['event_type'] != 'tou_event':
            raise BadEvent('Event of type ToU got event_type {!r}'.format(data['event_type']))

        return cls(created_by=data.get('created_by'),
                   created_ts=data.get('created_ts'),
                   event_id=data['event_id'],
                   version=data['version'],
                   )


    # -----------------------------------------------------------------
    @property
    def version(self):
        """
        This is the version of the ToU that was accepted.

        :return: ToU version.
        :rtype: string_types
        """
        return self._data['version']

    @version.setter
    def version(self, value):
        """
        :param value: Unique ID of event.
        :type value: bson.ObjectId | string_types
        """
        if not isinstance(value, str) and not isinstance(value, string_types):
            raise BadEvent("Invalid tou_event 'version': {!r}".format(value))
        self._data['version'] = value

    # -----------------------------------------------------------------


class ToUList(EventList):
    """
    List of ToUEvents.
    """
    def __init__(self, events, event_class=ToUEvent):
        EventList.__init__(self, events, event_class=event_class)

    def has_accepted(self, version: str) -> bool:
        """
        Check if the user has accepted a particular version of the ToU.

        :param version: Version of ToU

        :return: True or False
        """
        # All users have implicitly accepted the first ToU version (info stored in another collection)
        if version in ['2014-v1', '2014-dev-v1']:
            return True
        for this in self._elements:
            if this.version == version:
                return True
        return False
