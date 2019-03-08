from __future__ import absolute_import

from eduid_userdb.credentials.base import Credential
from eduid_userdb.credentials.password import Password
from eduid_userdb.credentials.fido import U2F
from eduid_userdb.credentials.fido import Webauthn
from eduid_userdb.credentials.list import CredentialList

# well-known proofing methods
METHOD_SWAMID_AL2_MFA    = 'SWAMID_AL2_MFA'
METHOD_SWAMID_AL2_MFA_HI = 'SWAMID_AL2_MFA_HI'
