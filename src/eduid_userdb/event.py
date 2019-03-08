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
from __future__ import annotations
import copy

from bson import ObjectId
from six import string_types
from typing import Type, TypeVar, Union, Mapping, List

from eduid_userdb.element import Element, ElementList, DuplicateElementViolation
from eduid_userdb.exceptions import UserDBValueError, BadEvent, EventHasUnknownData



class Event(Element):
    """
    :param data: Event parameters from database

    :type data: dict
    """
    def __init__(self, created_by=None, created_ts=None, event_type=None, event_id=None):
        super().__init__(created_by=created_by, created_ts=created_ts)
        self.event_type = event_type
        self.event_id = event_id

    @classmethod
    def from_dict(cls, data) -> Element:
        _known_data = ['created_by', 'created_ts', 'event_id', 'event_type']
        _leftovers = [x for x in data.keys() if x not in _known_data]
        if _leftovers:
            raise EventHasUnknownData('Event has unknown data: {!r}'.format(
                _leftovers,
            ))

        return cls(created_by=data.get('created_by'),
                   created_ts=data.get('created_ts'),
                   event_id=data['event_id'],
                   event_type=data['event_type'],
                   )

    # -----------------------------------------------------------------
    @property
    def key(self):
        """
        Return the element that is used as key for events in an ElementList.
        """
        return self.event_id

    # -----------------------------------------------------------------
    @property
    def event_type(self) -> str:
        """
        This is the event type.

        :return: Event type.
        """
        return self._data['event_type']

    @event_type.setter
    def event_type(self, value: str):
        """
        :param value: event type.
        :type value: str
        """
        if value is None:
            return
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'event_type': {!r}".format(value))
        self._data['event_type'] = value.lower()

    @property
    def event_id(self) -> ObjectId:
        """
        This is a unique id for this event.

        :return: Unique ID of event.
        """
        return self._data['event_id']

    @event_id.setter
    def event_id(self, value: ObjectId):
        """
        :param value: Unique ID of event.
        """
        if not isinstance(value, ObjectId):
            raise UserDBValueError("Invalid 'event_id': {!r}".format(value))
        self._data['event_id'] = value

    # -----------------------------------------------------------------
    def to_dict(self, mixed_format=False):
        """
        Convert Element to a dict, that can be used to reconstruct the
        Element later.

        :param mixed_format: Tag each Event with the event_type. Used when list has multiple types of events.
        :type old_userdb_format: bool
        :type mixed_format: bool
        """
        res = copy.copy(self._data)  # avoid caller messing with our _data
        if not mixed_format and 'event_type' in res:
            del res['event_type']
        return res


EventType = TypeVar('EventType', bound=Event)


class EventList(ElementList):
    """
    Hold a list of Event instances.

    Provide methods to add, update and remove elements from the list while
    maintaining some governing principles, such as ensuring there no duplicates in the list.

    :param events: List of events
    :param raise_on_unknown: Raise EventHasUnknownData if unrecognized data is encountered
    :param event_class: Enforce all elements are of this type

    :type events: [dict | Event]
    :type raise_on_unknown: bool
    :type event_class: object
    """

    def __init__(self, events: Union[Mapping, EventType], event_class: Type[Event]=Event):
        self._event_class = event_class
        elements = []
        ElementList.__init__(self, elements)

        if not isinstance(events, list):
            raise UserDBValueError('events should be a list')

        for this in events:
            if isinstance(this, self._event_class):
                self.add(this)
            elif isinstance(this, dict):
                if 'event_type' in this:
                    event = event_from_dict(this)
                else:
                    event = event_class(**this)
                self.add(event)
            else:
                raise UserDBValueError(f'Bad event data: {this!r}')

    def add(self, event: EventType):
        """
        Add an event to the list.

        :param event: Event to add.
        :type event: Event
        """
        if not isinstance(event, self._event_class):
            raise UserDBValueError("Invalid event: {!r} (expected {!r})".format(event, self._event_class))
        existing = self.find(event.key)
        if existing:
            if event.to_dict() == existing.to_dict():
                # Silently accept duplicate identical events to clean out bad entrys from the database
                return
            raise DuplicateElementViolation("Event {!s} already in list".format(event.key))
        super(EventList, self).add(event)

    def to_list_of_dicts(self, mixed_format: bool=False) -> List[dict]:
        """
        Get the elements in a serialized format that can be stored in MongoDB.

        :param mixed_format: Tag each Event with the event_type. Used when list has multiple types of events.

        :return: List of dicts
        """
        return [this.to_dict(mixed_format=mixed_format) for this in self._elements]


def event_from_dict(data: dict):
    """
    Create an Event instance (probably really a subclass of Event) from a dict.

    :param data: Password parameters from database
    :param raise_on_unknown: Raise EventHasUnknownData if unrecognized data is encountered

    :type data: dict
    :rtype: Event
    """
    if not 'event_type' in data:
        raise UserDBValueError('No event type specified')
    if data['event_type'] == 'tou_event':
        from eduid_userdb.tou import ToUEvent  # avoid cyclic dependency by importing this here
        return ToUEvent.from_dict(data)
    raise BadEvent('Unknown event_type in data: {!s}'.format(data['event_type']))
