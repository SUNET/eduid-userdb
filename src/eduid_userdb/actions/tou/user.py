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

__author__ = 'eperez'

from dataclasses import dataclass
from typing import Any, Dict

from eduid_userdb.exceptions import UserMissingData
from eduid_userdb.user import User


@dataclass
class ToUUser(User):
    """
    Subclass of eduid_userdb.User with
    the eduid-actions plugin for ToU specific data.

    :param userid: user id
    :param eppn: eppn
    :param tou: ToU  list
    :param data: userid, eppn and tou
    """

    @classmethod
    def check_or_use_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check that the provided data dict contains all needed keys.
        """
        if '_id' not in data or data['_id'] is None:
            raise UserMissingData('Attempting to record a ToU acceptance ' 'for an unidentified user.')
        if 'eduPersonPrincipalName' not in data or data['eduPersonPrincipalName'] is None:
            raise UserMissingData('Attempting to record a ToU acceptance ' 'for a user without eppn.')
        if 'tou' not in data or data['tou'] is None:
            raise UserMissingData(
                'Attempting to record the acceptance of '
                'an unknown version of the ToU for '
                'the user with eppn ' + str(data.get('eduPersonPrincipalName', data.get('eppn')))
            )
        return data
