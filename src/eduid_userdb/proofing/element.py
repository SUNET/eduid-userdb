# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 NORDUnet A/S
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
from __future__ import annotations

import copy
from six import string_types

from eduid_userdb.element import VerifiedElement, Element
from eduid_userdb.element import _set_something_by, _set_something_ts
from eduid_userdb.exceptions import UserDBValueError, ProofingHasUnknownData


__author__ = 'lundberg'


class ProofingElement(VerifiedElement):
    """
    Element for holding the state of a proofing flow. It should contain meta data needed for logging
    a proofing according to the Kantara specification.

    Properties of ProofingElement:

        created_by
        created_ts
        is_verified
        verified_by
        verified_ts
        verification_code
    """
    def __init__(self, verification_code: str,
                 created_by=None, created_ts=None,
                 verified=False, verified_by=None, verified_ts=None):
        super().__init__(created_by=created_by, created_ts=created_ts,
                         verified=verified, verified_by=verified_by, verified_ts=verified_ts,
                         )
        self.verification_code = verification_code

    @classmethod
    def from_dict(cls, data):
        _known_data = ['created_by', 'created_ts', 'verified', 'verified_by', 'verified_ts',
                       'verification_code']
        _leftovers = [x for x in data.keys() if x not in _known_data]
        if _leftovers:
            raise ProofingHasUnknownData('ProofingElement has unknown data: {!r}'.format(
                _leftovers,
            ))

        return cls(created_by=data.get('created_by'),
                   created_ts=data.get('created_ts'),
                   verified=data['verified'],
                   verified_by=data['verified_by'],
                   verified_ts=data['verified_ts'],
                   verification_code=data['verification_code'],
                   )

    @property
    def key(self):
        raise NotImplementedError('ProofingElement does not currently have a key')

    # -----------------------------------------------------------------
    @property
    def verification_code(self):
        """
        :return: Confirmation code used to verify this element.
        :rtype: str | unicode
        """
        return self._data['verification_code']

    @verification_code.setter
    def verification_code(self, value):
        """
        :param value: New verification_code
        :type value: str | unicode | None
        """
        if value is None:
            return
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'verification_code': {!r}".format(value))
        self._data['verification_code'] = value


class NinProofingElement(ProofingElement):
    """
    Element for holding the state of a nin proofing flow.

    Properties of NinProofingElement:

        number
        created_by
        created_ts
        is_verified
        verified_by
        verified_ts
        verification_code

    :param data: element parameters from database

    :type data: dict
    """
    def __init__(self, number, created_by=None, created_ts=None,
                 verified=False, verified_by=None, verified_ts=None,
                 verification_code=None):
        super().__init__(created_by=created_by, created_ts=created_ts,
                         verified=verified, verified_by=verified_by, verified_ts=verified_ts,
                         verification_code=verification_code)
        self.number = number

    @classmethod
    def from_dict(cls, data) -> NinProofingElement:
        _known_data = ['created_by', 'created_ts', 'verified', 'verified_by', 'verified_ts',
                       'verification_code', 'number']
        _leftovers = [x for x in data.keys() if x not in _known_data]
        if _leftovers:
            raise ProofingHasUnknownData('NinProofingElement has unknown data: {!r}'.format(
                _leftovers,
            ))

        return cls(created_by=data.get('created_by'),
                   created_ts=data.get('created_ts'),
                   verified=data['verified'],
                   verified_by=data['verified_by'],
                   verified_ts=data['verified_ts'],
                   verification_code=data['verification_code'],
                   number=data['number']
                   )

    @property
    def number(self):
        """
        This is the nin number.

        :return: nin number.
        :rtype: str | unicode
        """
        return self._data['number']

    @number.setter
    def number(self, value):
        """
        :param value: nin number.
        :type value: str | unicode
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'number': {!r}".format(value))
        self._data['number'] = str(value.lower())

    def to_dict(self):
        res = super(NinProofingElement, self).to_dict()
        res['number'] = self.number
        return res


class EmailProofingElement(ProofingElement):
    """
    Element for holding the state of an email proofing flow.

    Properties of EmailProofingElement:

        email
        created_by
        created_ts
        is_verified
        verified_by
        verified_ts
        verification_code

    :param data: element parameters from database

    :type data: dict
    """
    def __init__(self, email=None, created_by=None, created_ts=None,
                 verified=False, verification_code=None, data=None):

        data = copy.copy(data)
        if email is None:
            email = data.pop('email')

        super(EmailProofingElement, self).__init__(created_by=created_by,
                                                   created_ts=created_ts, verified=verified,
                                                   verification_code=verification_code, data=data)
        self.email = email

    @property
    def email(self):
        """
        This is the email.

        :return: nin number.
        :rtype: str | unicode
        """
        return self._data['email']

    @email.setter
    def email(self, value):
        """
        :param value: email.
        :type value: str | unicode
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'email': {!r}".format(value))
        self._data['email'] = str(value.lower())

    def to_dict(self):
        res = super(ProofingElement, self).to_dict()
        res['email'] = self.email
        return res


class PhoneProofingElement(ProofingElement):
    """
    Element for holding the state of a phone number proofing flow.

    Properties of PhoneProofingElement:

        number
        created_by
        created_ts
        is_verified
        verified_by
        verified_ts
        verification_code

    :param data: element parameters from database

    :type data: dict
    """
    def __init__(self, phone=None, created_by=None, created_ts=None,
                 verified=False, verification_code=None, data=None):

        data = copy.copy(data)
        if not phone:
            phone = data.pop('number')

        super(PhoneProofingElement, self).__init__(created_by=created_by,
                                                   created_ts=created_ts, verified=verified,
                                                   verification_code=verification_code, data=data)
        self.number = phone

    @property
    def number(self):
        """
        This is the phone number.

        :return: phone number.
        :rtype: str | unicode
        """
        return self._data['number']

    @number.setter
    def number(self, value):
        """
        :param value: number.
        :type value: str | unicode
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'phone number': {!r}".format(value))
        self._data['number'] = str(value.lower())

    def to_dict(self):
        res = super(ProofingElement, self).to_dict()
        res['number'] = self.number
        return res


class SentLetterElement(Element):
    """
    Properties of SentLetterElement:

    address
    is_sent
    sent_ts
    transaction_id
    created_by
    created_ts
    """
    def __init__(self, created_by=None, created_ts=None, is_sent=False, sent_ts=None,
                 transaction_id=None, address=None):
        super().__init__(created_by=created_by, created_ts=created_ts)
        self.is_sent = is_sent
        self.sent_ts = sent_ts
        self.transaction_id = transaction_id
        self.address = address

    @classmethod
    def from_dict(cls, data) -> SentLetterElement:
        _known_data = ['created_by', 'created_ts', 'is_sent', 'sent_ts', 'transaction_id', 'address']
        return cls._default_from_dict(data, _known_data)

    @property
    def key(self):
        raise NotImplementedError('SentLetterElement currently has no key')

    @property
    def is_sent(self):
        """
        :return: True if this is a verified element.
        :rtype: bool
        """
        return self._data['is_sent']

    @is_sent.setter
    def is_sent(self, value):
        """
        :param value: New verification status
        :type value: bool
        """
        if not isinstance(value, bool):
            raise UserDBValueError("Invalid 'is_sent': {!r}".format(value))
        self._data['is_sent'] = value

    @property
    def sent_ts(self):
        """
        :return: Timestamp of when letter was delivered to letter service.
        :rtype: datetime.datetime
        """
        return self._data.get('sent_ts')

    @sent_ts.setter
    def sent_ts(self, value):
        """
        :param value: Timestamp of when letter was delivered to letter service.
                      Value None is ignored, True is short for datetime.utcnow().
        :type value: datetime.datetime | True | None
        """
        _set_something_ts(self._data, 'sent_ts', value)

    @property
    def transaction_id(self):
        """
        :return: Transaction information from the letter service
        :rtype: str | unicode
        """
        return self._data.get('transaction_id', '')

    @transaction_id.setter
    def transaction_id(self, value):
        """
        :param value: Transaction information from letter service (None is no-op).
        :type value: str | unicode | None
        """
        _set_something_by(self._data, 'transaction_id', value)

    @property
    def address(self):
        """
        :return: Official address the letter should be sent to
        :rtype: str | unicode
        """
        return self._data.get('address', None)

    @address.setter
    def address(self, value):
        """
        :param value: Official address the letter should be sent to
        :type value: dict | None
        """
        self._data['address'] = value
