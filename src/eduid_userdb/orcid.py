# -*- coding: utf-8 -*-

from __future__ import annotations

import copy
from six import string_types
from eduid_userdb.exceptions import UserDBValueError, UserHasUnknownData
from eduid_userdb.element import Element, VerifiedElement

__author__ = 'lundberg'


class OidcIdToken(Element):
    """
    OpenID Connect ID token data
    """

    def __init__(self, iss=None, sub=None, aud=None, exp=None, iat=None, nonce=None, auth_time=None, acr=None, amr=None,
                 azp=None, created_by=None, created_ts=None):
        # TODO: created_ts=None means "don't set" in Element. Maybe not special-case created_ts in this class.
        if created_ts is None:
            created_ts = True
        super().__init__(created_by=created_by, created_ts=created_ts)
        self.iss = iss
        self.sub = sub
        self.aud = aud
        self.exp = exp
        self.iat = iat
        self.nonce = nonce
        self.auth_time = auth_time
        self.acr = acr
        self.amr = amr
        self.azp = azp

    @classmethod
    def from_dict(cls, data: dict) -> OidcIdToken:
        _known_data = ['created_by', 'created_ts',
                       'iss', 'sub', 'aud', 'exp', 'iat', 'nonce', 'auth_time', 'acr', 'amr', 'azp']
        _leftovers = [x for x in data.keys() if x not in _known_data]
        if _leftovers:
            raise UserHasUnknownData(f'OidcIdToken has unknown data: {_leftovers}')

        return cls(created_by=data.get('created_by'),
                   created_ts=data.get('created_ts'),
                   iss=data['iss'],
                   sub=data['sub'],
                   aud=data['aud'],
                   exp=data['exp'],
                   iat=data['iat'],
                   nonce=data.get('nonce'),
                   auth_time=data.get('auth_time'),
                   acr=data.get('acr'),
                   amr=data.get('amr'),
                   azp=data.get('azp'),
                   )

    @property
    def key(self):
        """
        :return: Unique identifier
        :rtype: six.string_types
        """
        return '{}{}'.format(self.iss, self.sub)

    # -----------------------------------------------------------------
    @property
    def iss(self):
        """
        Issuer identifier

        :return: Issuer url
        :rtype: six.string_types
        """
        return self._data['iss']

    @iss.setter
    def iss(self, value):
        """
        :param value: Issuer
        :type value: six.string_types
        """
        if not value or not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'iss': {!r}".format(value))
        self._data['iss'] = value

    # -----------------------------------------------------------------
    @property
    def sub(self):
        """
        Subject identifier

        :return: subject id
        :rtype: six.string_types
        """
        return self._data['sub']

    @sub.setter
    def sub(self, value):
        """
        :param value: Subject id
        :type value: six.string_types
        """
        if not value or not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'sub': {!r}".format(value))
        self._data['sub'] = value

    # -----------------------------------------------------------------
    @property
    def aud(self):
        """
        Audience(s)

        :return: audience list
        :rtype: list
        """
        return self._data['aud']

    @aud.setter
    def aud(self, value):
        """
        :param value: audience list
        :type value: list
        """
        if not isinstance(value, list):
            raise UserDBValueError("Invalid 'aud': {!r}".format(value))
        self._data['aud'] = value

    # -----------------------------------------------------------------
    @property
    def exp(self):
        """
        Expiration time

        :return: expiration time
        :rtype: int
        """
        return self._data['exp']

    @exp.setter
    def exp(self, value):
        """
        :param value: expiration time
        :type value: int
        """
        if not isinstance(value, int):
            raise UserDBValueError("Invalid 'exp': {!r}".format(value))
        self._data['exp'] = value

    # -----------------------------------------------------------------
    @property
    def iat(self):
        """
        Expiration time

        :return: expiration time
        :rtype: int
        """
        return self._data['iat']

    @iat.setter
    def iat(self, value):
        """
        :param value: expiration time
        :type value: int
        """
        if not isinstance(value, int):
            raise UserDBValueError("Invalid 'iat': {!r}".format(value))
        self._data['iat'] = value

    # -----------------------------------------------------------------
    @property
    def nonce(self):
        """
        Nonce used to associate a Client session with an ID Token, and to mitigate replay attacks.

        :return: nonce
        :rtype: six.string_types
        """
        return self._data.get('nonce')

    @nonce.setter
    def nonce(self, value):
        """
        :param value: nonce
        :type value: six.string_types | None
        """
        if value is not None:  # No op for value None
            if not isinstance(value, string_types):
                raise UserDBValueError("Invalid 'nonce': {!r}".format(value))
            self._data['nonce'] = value

    # -----------------------------------------------------------------
    @property
    def auth_time(self):
        """
        Time when the End-User authentication occurred.

        :return: auth time
        :rtype: int
        """
        return self._data.get('auth_time')

    @auth_time.setter
    def auth_time(self, value):
        """
        :param value: auth time
        :type value: int
        """
        if value is not None:  # No op for value None
            if not isinstance(value, int):
                raise UserDBValueError("Invalid 'auth_time': {!r}".format(value))
            self._data['auth_time'] = value

    # -----------------------------------------------------------------
    @property
    def acr(self):
        """
        Authentication Context Class Reference

        :return: acr
        :rtype: six.string_types
        """
        return self._data.get('acr')

    @acr.setter
    def acr(self, value):
        """
        :param value: acr
        :type value: six.string_types
        """
        if value is not None:  # No op for value None
            if not isinstance(value, string_types):
                raise UserDBValueError("Invalid 'acr': {!r}".format(value))
            self._data['acr'] = value

    # -----------------------------------------------------------------
    @property
    def amr(self):
        """
        Authentication Methods References

        :return: nin number.
        :rtype: list
        """
        return self._data.get('amr')

    @amr.setter
    def amr(self, value):
        """
        :param value: nin number.
        :type value: list
        """
        if value is not None:  # No op for value None
            if not isinstance(value, list):
                raise UserDBValueError("Invalid 'amr': {!r}".format(value))
            self._data['amr'] = value

    # -----------------------------------------------------------------
    @property
    def azp(self):
        """
        Authorized party

        :return: acr
        :rtype: six.string_types
        """
        return self._data.get('azp')

    @azp.setter
    def azp(self, value):
        """
        :param value: acr
        :type value: six.string_types
        """
        if value is not None:  # No op for value None
            if not isinstance(value, string_types):
                raise UserDBValueError("Invalid 'azp': {!r}".format(value))
            self._data['azp'] = value


class OidcAuthorization(Element):
    """
    OpenID Connect Authorization data
    """
    def __init__(self, access_token=None, token_type=None, id_token=None, expires_in=None, refresh_token=None,
                 created_by=None, created_ts=None):
        # TODO: created_ts=None means "don't set" in Element. Maybe not special-case created_ts in this class.
        if created_ts is None:
            created_ts = True
        super().__init__(created_by=created_by, created_ts=created_ts)
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        # Parse ID token
        if isinstance(id_token, dict):
            self.id_token = OidcIdToken.from_dict(id_token)
        if isinstance(id_token, OidcIdToken):
            self.id_token = id_token

    @classmethod
    def from_dict(cls, data: dict) -> OidcAuthorization:
        _known_data = ['created_by', 'created_ts',
                       'access_token', 'token_type', 'id_token', 'expires_in', 'refresh_token']
        _leftovers = [x for x in data.keys() if x not in _known_data]
        if _leftovers:
            raise UserHasUnknownData(f'OidcAuthorization has unknown data: {_leftovers}')

        return cls(created_by=data.get('created_by'),
                   created_ts=data.get('created_ts'),
                   access_token=data['access_token'],
                   token_type=data['token_type'],
                   id_token=data['id_token'],
                   expires_in=data['expires_in'],
                   refresh_token=data['refresh_token'],
                   )

    @property
    def key(self):
        """
        :return: Unique identifier
        :rtype: six.string_types
        """
        return self.id_token.key

    # -----------------------------------------------------------------
    @property
    def access_token(self):
        """
        Access token

        :return: access token
        :rtype: six.string_types
        """
        return self._data['access_token']

    @access_token.setter
    def access_token(self, value):
        """
        :param value: Access token
        :type value: six.string_types
        """
        if not value or not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'access_token': {!r}".format(value))
        self._data['access_token'] = value

    # -----------------------------------------------------------------
    @property
    def token_type(self):
        """
        Token type

        :return: token type
        :rtype: six.string_types
        """
        return self._data['sub']

    @token_type.setter
    def token_type(self, value):
        """
        :param value: token type
        :type value: six.string_types
        """
        if not value or not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'token_type': {!r}".format(value))
        self._data['token_type'] = value.lower()  # Case insensitive

    # -----------------------------------------------------------------
    @property
    def id_token(self):
        """
        ID Token

        :return: id token
        :rtype: six.string_types
        """
        return self._data['id_token']

    @id_token.setter
    def id_token(self, value):
        """
        :param value: id token
        :type value: six.string_types
        """
        if not isinstance(value, OidcIdToken):
            raise UserDBValueError("Invalid 'id_token': {!r}".format(value))
        self._data['id_token'] = value

    # -----------------------------------------------------------------
    @property
    def expires_in(self):
        """
        The lifetime in seconds of the access token.

        :return: expires in
        :rtype: int
        """
        return self._data.get('expires_in')

    @expires_in.setter
    def expires_in(self, value):
        """
        :param value: expires in
        :type value: int
        """
        if value is not None:  # No op for value None
            if not isinstance(value, int):
                raise UserDBValueError("Invalid 'expires_in': {!r}".format(value))
            self._data['expires_in'] = value

    # -----------------------------------------------------------------
    @property
    def refresh_token(self):
        """
        Refresh token

        :return: refresh token
        :rtype: six.string_types
        """
        return self._data.get('refresh_token')

    @refresh_token.setter
    def refresh_token(self, value):
        """
        :param value: refresh token
        :type value: six.string_types
        """
        if value is not None:  # No op for value None
            if not isinstance(value, string_types):
                raise UserDBValueError("Invalid 'refresh_token': {!r}".format(value))
            self._data['refresh_token'] = value

    def to_dict(self, old_userdb_format=False):
        """
        Convert OidcAuthorization to a dict

        :param old_userdb_format: Set to True to get data back in legacy format.
        :type old_userdb_format: bool

        :return data dict
        :rtype dict
        """
        data = copy.deepcopy(self._data)
        data['id_token'] = self.id_token.to_dict()
        return data


class Orcid(VerifiedElement):
    """
    :param data: Orcid parameters from database
    :param raise_on_unknown: Raise exception on unknown values in `data' or not.

    :type data: dict
    :type raise_on_unknown: bool
    """
    def __init__(self, id=None, name=None, given_name=None, family_name=None, oidc_authz=None,
                 created_by=None, verified=False, created_ts=None):
        # TODO: created_ts=None means "don't set" in Element. Maybe not special-case created_ts in this class.
        if created_ts is None:
            created_ts = True
        super().__init__(created_by=created_by, created_ts=created_ts, verified=verified)
        self.id = id
        self.name = name
        self.given_name = given_name
        self.family_name = family_name

        # Parse ID token
        if isinstance(oidc_authz, dict):
            self.oidc_authz = OidcAuthorization.from_dict(oidc_authz)
        elif isinstance(oidc_authz, OidcAuthorization):
            self.oidc_authz = oidc_authz
        else:
            raise UserDBValueError(f'Unknown oidc_authz in Orcid: {oidc_authz!r}')

    @classmethod
    def from_dict(cls, data: dict) -> Orcid:
        _known_data = ['created_by', 'created_ts', 'verified',
                       'id', 'name', 'given_name', 'family_name', 'oidc_authz']
        _leftovers = [x for x in data.keys() if x not in _known_data]
        if _leftovers:
            raise UserHasUnknownData(f'Orcid has unknown data: {_leftovers}')

        return cls(created_by=data.get('created_by'),
                   created_ts=data.get('created_ts'),
                   verified=data.get('verified'),
                   id=data['id'],
                   name=data['name'],
                   given_name=data['given_name'],
                   family_name=data['family_name'],
                   oidc_authz=data['oidc_authz'],
                   )

    # -----------------------------------------------------------------
    @property
    def key(self):
        """
        Unique id
        """
        return self.id

    # -----------------------------------------------------------------
    @property
    def id(self):
        """
        Users ORCID

        :return: orcid
        :rtype: six.string_types
        """
        return self._data['id']

    @id.setter
    def id(self, value):
        """
        :param value: ORCID
        :type value: str | unicode
        """
        if not value or not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'id': {!r}".format(value))
        self._data['id'] = str(value.lower())  # Case insensitive

    # -----------------------------------------------------------------
    @property
    def name(self):
        """
        Users name

        :return: name
        :rtype: six.string_types
        """
        return self._data['name']

    @name.setter
    def name(self, value):
        """
        :param value: name
        :type value: str | unicode | None
        """
        if value is not None and not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'name': {!r}".format(value))
        self._data['name'] = value

    # -----------------------------------------------------------------
    @property
    def given_name(self):
        """
        Users given_name

        :return: given name
        :rtype: six.string_types
        """
        return self._data['given_name']

    @given_name.setter
    def given_name(self, value):
        """
        :param value: given name
        :type value: str | unicode | None
        """
        if value is not None and not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'given_name': {!r}".format(value))
        self._data['given_name'] = value

    # -----------------------------------------------------------------
    @property
    def family_name(self):
        """
        Users family name

        :return: family name
        :rtype: six.string_types
        """
        return self._data['family_name']

    @family_name.setter
    def family_name(self, value):
        """
        :param value: family name
        :type value: str | unicode | None
        """
        if value is not None and not isinstance(value, string_types):
            raise UserDBValueError("Invalid 'family_name': {!r}".format(value))
        self._data['family_name'] = value

    # -----------------------------------------------------------------
    @property
    def oidc_authz(self):
        """
        Users ORCID OIDC authorization data

        :return: oidc authorization data
        :rtype: OidcAuthorization
        """
        return self._data['oidc_authz']

    @oidc_authz.setter
    def oidc_authz(self, value):
        """
        :param value: oidc authorization data
        :type value: OidcAuthorization
        """
        if not isinstance(value, OidcAuthorization):
            raise UserDBValueError("Invalid 'oidc_authz': {!r}".format(value))
        self._data['oidc_authz'] = value

    # -----------------------------------------------------------------
    def to_dict(self, old_userdb_format=False):
        """
        Convert Element to a dict, that can be used to reconstruct the
        Element later.

        :param old_userdb_format: Set to True to get data back in legacy format.
        :type old_userdb_format: bool
        """
        data = copy.deepcopy(self._data)
        data['oidc_authz'] = self.oidc_authz.to_dict()
        return data
