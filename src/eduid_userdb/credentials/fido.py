# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 NORDUnet A/S
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
from __future__ import absolute_import

import copy
from hashlib import sha256
from six import string_types
from eduid_userdb.credentials import Credential
from eduid_userdb.exceptions import UserHasUnknownData, UserDBValueError

__author__ = 'ft'


class FidoCredential(Credential):
    """
    Token authentication credential
    """

    def __init__(self, created_by, created_ts,
                 verified,
                 verified_by, verified_ts,
                 proofing_method, proofing_version,
                 keyhandle: str, app_id: str, description=''):

        super().__init__(created_by=created_by,
                         created_ts=created_ts,
                         verified=verified,
                         verified_by=verified_by,
                         verified_ts=verified_ts,
                         proofing_method=proofing_method,
                         proofing_version=proofing_version)
        self.keyhandle = keyhandle
        self.app_id = app_id
        self.description = description

    def __repr__(self):  # XXX was __repr__ what we settled on for Python3? Don't think so
        kh = self._data['keyhandle'][:8]
        if self.is_verified:
            return '<eduID {!s}: key_handle=\'{!s}...\', verified=True, proofing=({!r} v {!r})>'.format(
                self.__class__.__name__,
                kh,
                self.proofing_method,
                self.proofing_version
            )
        else:
            return '<eduID {!s}: key_handle=\'{!s}...\', verified=False>'.format(
                self.__class__.__name__, kh)

    @property
    def keyhandle(self) -> str:
        """
        This is the server side reference to the U2F token used.

        :return: U2F keyhandle.
        """
        return self._data['keyhandle']

    @keyhandle.setter
    def keyhandle(self, value: str):
        """
        :param value: U2F keyhandle.
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'keyhandle': {!r}".format(value))
        self._data['keyhandle'] = value

    @property
    def app_id(self) -> str:
        """
        The U2F app_id used when creating this credential.

        :return: U2F app_id
        """
        return self._data['app_id']

    @app_id.setter
    def app_id(self, value: str):
        """
        :param value: U2F app_id.
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'app_id': {!r}".format(value))
        self._data['app_id'] = value

    @property
    def description(self) -> str:
        """
        User description/name of this token.

        :return: description
        """
        return self._data['description']

    @description.setter
    def description(self, value: str):
        """
        :param value: U2F description.
        :type value: str
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'description': {!r}".format(value))
        self._data['description'] = value


class U2F(FidoCredential):
    """
    U2F token authentication credential
    """

    def __init__(self, created_by=None, created_ts=None,
                 verified=False, verified_by=None, verified_ts=None,
                 keyhandle=None, app_id=None, description=None,
                 proofing_method=None, proofing_version=None,
                 version=None, public_key=None, attest_cert=None):
        super().__init__(created_by=created_by, created_ts=created_ts,
                         verified=verified, verified_by=verified_by, verified_ts=verified_ts,
                         keyhandle=keyhandle, app_id=app_id, description=description,
                         proofing_method=proofing_method, proofing_version=proofing_version)
        self.version = version
        self.public_key = public_key
        self.attest_cert = attest_cert

    @classmethod
    def from_dict(cls, data):
        _known_data = ['created_by', 'created_ts', 'verified', 'verified_by', 'verified_ts',
                       'proofing_method', 'proofing_version',
                       'keyhandle', 'app_id', 'description', 'version', 'public_key', 'attest_cert']
        _leftovers = [x for x in data.keys() if x not in _known_data]
        if _leftovers:
            raise UserHasUnknownData('{!s} has unknown data: {!r}'.format(
                cls.__class__.__name__,
                _leftovers,
            ))

        return cls(created_by=data.get('created_by'),
                   created_ts=data.get('created_ts'),
                   verified=data.get('verified', False),
                   verified_by=data.get('verified_by', None),
                   verified_ts=data.get('verified_ts', None),
                   proofing_method=data.get('proofing_method', None),
                   proofing_version=data.get('proofing_version', None),
                   # FIDO generic
                   keyhandle=data['keyhandle'],
                   app_id=data['app_id'],
                   description=data.get('description', ''),
                   # FIDO1/U2f specific
                   version=data.get('version', ''),
                   public_key=data.get('public_key', ''),
                   attest_cert=data.get('attest_cert', ''),
                   )

    @property
    def key(self):
        """
        Return the element that is used as key.
        """
        return 'sha256:' + sha256(self.keyhandle.encode('utf-8') +
                                  self.public_key.encode('utf-8')
                                  ).hexdigest()

    @property
    def version(self) -> str:
        """
        This is the U2F version used by this token.

        :return: U2F version.
        """
        return self._data['version']

    @version.setter
    def version(self, value: str):
        """
        :param value: U2F version. E.g. 'U2F_V2'.
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'version': {!r}".format(value))
        self._data['version'] = value

    @property
    def attest_cert(self) -> str:
        """
        The U2F attest_cert from the credential.

        We should probably refine what we store here later on, but for now we just
        store the whole certificate.

        :return: U2F attest_cert
        """
        return self._data['attest_cert']

    @attest_cert.setter
    def attest_cert(self, value: str):
        """
        :param value: U2F attest_cert.
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'attest_cert': {!r}".format(value))
        self._data['attest_cert'] = value

    @property
    def public_key(self) -> str:
        """
        This is the public key of the U2F token.

        :return: U2F public_key.
        """
        return self._data['public_key']

    @public_key.setter
    def public_key(self, value: str):
        """
        :param value: U2F public_key.
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'public_key': {!r}".format(value))
        self._data['public_key'] = value


class Webauthn(FidoCredential):
    """
    Webauthn token authentication credential
    """

    def __init__(self, created_by=None, created_ts=None,
                 verified=False, verified_by=None, verified_ts=None,
                 keyhandle=None, app_id=None, description=None,
                 proofing_method=None, proofing_version=None,
                 credential_data=None, attest_obj=None):
        super().__init__(created_by=created_by, created_ts=created_ts,
                         verified=verified, verified_by=verified_by, verified_ts=verified_ts,
                         keyhandle=keyhandle, app_id=app_id, description=description,
                         proofing_method=proofing_method, proofing_version=proofing_version)
        self.attest_obj = attest_obj
        self.credential_data = credential_data

    @classmethod
    def from_dict(cls, data):
        _known_data = ['created_by', 'created_ts', 'verified', 'verified_by', 'verified_ts',
                       'proofing_method', 'proofing_version',
                       'keyhandle', 'app_id', 'description', 'credential_data', 'attest_obj']
        _leftovers = [x for x in data.keys() if x not in _known_data]
        if _leftovers:
            raise UserHasUnknownData('{!s} has unknown data: {!r}'.format(
                cls.__class__.__name__,
                _leftovers,
            ))

        return cls(created_by=data.get('created_by'),
                   created_ts=data.get('created_ts'),
                   verified=data.get('verified', False),
                   verified_by=data.get('verified_by', None),
                   verified_ts=data.get('verified_ts', None),
                   proofing_method=data.get('proofing_method', None),
                   proofing_version=data.get('proofing_version', None),
                   # FIDO generic
                   keyhandle=data['keyhandle'],
                   app_id=data['app_id'],
                   description=data.get('description', ''),
                   # FIDO2/Webauthn specific
                   attest_obj=data.get('attest_obj', ''),
                   credential_data=data.get('credential_data', ''),
                   )

    @property
    def key(self):
        """
        Return the element that is used as key.
        """
        return 'sha256:' + sha256(self.keyhandle.encode('utf-8') +
                                  self.credential_data.encode('utf-8')
                                  ).hexdigest()

    @property
    def attest_obj(self) -> str:
        """
        The Webauthn attestation object for the credential.

        We should probably refine what we store here later on, but for now we just
        store the whole object.

        :return: Webauthn attest_obj
        """
        return self._data['attest_obj']

    @attest_obj.setter
    def attest_obj(self, value: str):
        """
        :param value: Webauthn attest_obj.
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'attest_obj': {!r}".format(value))
        self._data['attest_obj'] = value

    @property
    def credential_data(self) -> str:
        """
        This is the credential data of the Webauthn token.

        :return: Webauthn credential data
        :rtype: str
        """
        return self._data['credential_data']

    @credential_data.setter
    def credential_data(self, value: str):
        """
        :param value: Webauthn credential data
        """
        if not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'credential_data': {!r}".format(value))
        self._data['credential_data'] = value
