# -*- coding: utf-8 -*-
from __future__ import annotations

from six import string_types
from typing import List, Union, TypeVar

from eduid_userdb.element import Element, ElementList
from eduid_userdb.exceptions import UserDBValueError, EduIDUserDBError, UserHasUnknownData


__author__ = 'lundberg'


class LockedIdentityElement(Element):

    """
    Element that is used to lock an identity to a user

    Properties of LockedIdentityElement:

        identity_type
    """

    def __init__(self, created_by=None, created_ts=None, identity_type=None):
        super().__init__(created_by=created_by, created_ts=created_ts)
        self.identity_type = identity_type

    # -----------------------------------------------------------------
    @property
    def key(self):
        """
        :return: Type of identity
        :rtype: string_types
        """
        return self.identity_type

    # -----------------------------------------------------------------
    @property
    def identity_type(self):
        """
        :return: Type of identity
        :rtype: string_types
        """
        return self._data['identity_type']

    @identity_type.setter
    def identity_type(self, value):
        """
        :param value: Type of identity
        :type value: string_types
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'identity_type': {!r}".format(value))
        self._data['identity_type'] = value


class LockedIdentityNin(LockedIdentityElement):

    """
    Element that is used to lock a NIN to a user

    Properties of LockedNinElement:

        number
    """

    def __init__(self, number, created_by, created_ts):
        super().__init__(created_by=created_by, created_ts=created_ts, identity_type='nin')
        self.number = number

    @classmethod
    def from_dict(cls, data) -> LockedIdentityNin:
        _known_data = ['number', 'created_by', 'created_ts']
        _leftovers = [x for x in data.keys() if x not in _known_data]
        if _leftovers:
            raise UserHasUnknownData(f'LockedIdentityNin has unknown data: {_leftovers}')

        return cls(number=data['number'],
                   created_by=data.get('created_by'),
                   created_ts=data.get('created_ts'),
                   )

    # -----------------------------------------------------------------
    @property
    def number(self):
        """
        :return: Nin number
        :rtype: string_types
        """
        return self._data['number']

    @number.setter
    def number(self, value):
        """
        :param value: Nin number
        :type value: string_types
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'number': {!r}".format(value))
        self._data['number'] = value


# A type for an LockedIdentitytElementType or any of it's subclasses
LockedIdentityElementType = TypeVar('LockedIdentityElementType', bound='LockedIdentitytElement')


class LockedIdentityList(ElementList):
    """
    Hold a list of LockedIdentityElement instances.

    Provide methods to find and add to the list.
    """
    def __init__(self, locked_identities: List[Union[dict, LockedIdentityElementType]]):
        elements = []
        for item in locked_identities:
            if isinstance(item, LockedIdentityList):
                elements.append(item)
            else:
                if item['identity_type'] == 'nin':
                    elements.append(LockedIdentityNin(number=item['number'], created_by=item['created_by'],
                                                      created_ts=item['created_ts']))
        ElementList.__init__(self, elements)

    def remove(self, key):
        """
        Override remove method as an element should be set once, remove never.
        """
        raise EduIDUserDBError('Removal of LockedIdentityElements is not permitted')
