from __future__ import absolute_import

from bson import ObjectId

from eduid_userdb.element import ElementList, DuplicateElementViolation
from eduid_userdb.exceptions import UserHasUnknownData
from eduid_userdb.credentials import Credential, Password, U2F, Webauthn


class CredentialList(ElementList):
    """
    Hold a list of authentication credential instances.

    Provide methods to add, update and remove elements from the list while
    maintaining some governing principles, such as ensuring there no duplicates in the list.

    :param credentials: List of credentials
    :type credentials: [dict | Password | U2F]
    """

    def __init__(self, creds):
        elements = []
        for this in creds:
            if isinstance(this, Credential):
                credential = this
            elif isinstance(this, dict) and 'salt' in this:
                credential = Password.from_dict(this)
            elif isinstance(this, dict) and 'keyhandle' in this:
                if 'public_key' in this:
                    credential = U2F.from_dict(this)
                else:
                    credential = Webauthn.from_dict(this)
            else:
                raise UserHasUnknownData('Unknown credential data (type {}): {!r}'.format(type(this), this))
            elements.append(credential)

        super().__init__(elements)

    def add(self, element):
        if self.find(element.key):
            raise DuplicateElementViolation("credential {!s} already in list".format(element.key))
        super().add(element)

    def find(self, key):
        if isinstance(key, ObjectId):
            # backwards compatible - Password.key (credential_id) changed from ObjectId to str
            key = str(key)
        return super().find(key)
