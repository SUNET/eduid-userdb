# -*- coding: utf-8 -*-
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
# Author : Johan Lundberg <lundberg@nordu.net>
#
from __future__ import annotations

from bson.objectid import ObjectId
from six import string_types

from eduid_userdb.credentials import Credential
from eduid_userdb.exceptions import UserHasUnknownData, UserDBValueError

__author__ = 'lundberg'


class Password(Credential):

    def __init__(self, credential_id: str, salt: str, created_by=None, created_ts=None):
        super().__init__(created_by=created_by, created_ts=created_ts,
                         verified=False,
                         verified_by=None,
                         verified_ts=None,
                         proofing_method=None,
                         proofing_version=None,
                         )
        self.credential_id = credential_id
        self.salt = salt

    @classmethod
    def from_dict(cls, data) -> Password:
        _known_data = ['credential_id', 'salt', 'created_by', 'created_ts']
        _leftovers = [x for x in data.keys() if x not in _known_data]
        if _leftovers:
            raise UserHasUnknownData('Password has unknown data: {!r}'.format(
                _leftovers,
            ))

        return cls(credential_id=data['credential_id'],
                   salt=data['salt'],
                   created_by=data.get('created_by'),
                   created_ts=data.get('created_ts'),
                   )

    @property
    def key(self):
        """
        Return the element that is used as key.
        """
        return self.credential_id

    @property
    def credential_id(self):
        """
        This is a reference to the ObjectId in the authentication private database.

        :return: Unique ID of password.
        :rtype: string_types
        """
        return self._data['credential_id']

    @credential_id.setter
    def credential_id(self, value):
        """
        :param value: Reference to the password credential in the authn backend db.
        :type value: string_types
        """
        if isinstance(value, ObjectId):
            # backwards compatibility
            value = str(value)
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'credential_id': {!r}".format(value))
        self._data['credential_id'] = value

    @property
    def salt(self):
        """
        This is a reference to the ObjectId in the authentication private database.

        :return: Password salt.
        :rtype: str
        """
        return self._data['salt']

    @salt.setter
    def salt(self, value):
        """
        :param value: Password salt.
        :type value: str
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'salt': {!r}".format(value))
        self._data['salt'] = value
