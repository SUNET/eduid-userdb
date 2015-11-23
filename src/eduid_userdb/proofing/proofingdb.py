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

from bson import ObjectId
from bson.errors import InvalidId

from eduid_userdb.db import BaseDB
from eduid_userdb.exceptions import DocumentOutOfSync
from . import LetterProofingState

import logging
logger = logging.getLogger(__name__)

__author__ = 'lundberg'


class ProofingStateDB(BaseDB):

    ProofingStateClass = None

    def __init__(self, db_uri, db_name, collection='proofing_data'):
        BaseDB.__init__(self, db_uri, db_name, collection)

    def get_state_by_user_id(self, user_id, raise_on_missing=True):
        """
        Locate a state in the db given the state's user_id.

        :param user_id: User identifier
        :type user_id: bson.ObjectId | str | unicode
        :return: ProofingStateClass instance | None
        :rtype: ProofingStateClass | None

        :raise self.DocumentDoesNotExist: No user match the search criteria
        :raise self.MultipleDocumentsReturned: More than one user matches the search criteria
        """
        if not isinstance(user_id, ObjectId):
            try:
                user_id = ObjectId(user_id)
            except InvalidId:
                return None
        state = self._get_document_by_attr('user_id', user_id, raise_on_missing)
        if state:
            return self.ProofingStateClass(state)

    def save(self, state, check_sync=True):
        """

        :param state: ProofingStateClass object
        :type state: ProofingStateClass
        :param check_sync: Ensure the document hasn't been updated in the database since it was loaded
        :type check_sync: bool
        :return:
        """
        assert isinstance(state.user_id, ObjectId)

        modified = state.modified_ts
        state.modified_ts = True  # update to current time
        if modified is None:
            # document has never been modified
            result = self._coll.insert(state.to_dict())
            logging.debug("{!s} Inserted new state {!r} into {!r}): {!r})".format(
                self, state, self._coll_name, result))
        else:
            test_doc = {'user_id': state.user_id}
            if check_sync:
                test_doc['modified_ts'] = modified
            result = self._coll.update(test_doc, state.to_dict(), upsert=(not check_sync))
            if check_sync and result['n'] == 0:
                db_ts = None
                db_state = self._coll.find_one({'user_id': state.user_id})
                if db_state:
                    db_ts = db_state['modified_ts']
                logging.debug("{!s} FAILED Updating state {!r} (ts {!s}) in {!r}). "
                              "ts in db = {!s}".format(self, state, modified, self._coll_name, db_ts))
                raise DocumentOutOfSync('Stale state object can\'t be saved')
            logging.debug("{!s} Updated state {!r} (ts {!s}) in {!r}): {!r}".format(
                self, state, modified, self._coll_name, result))


class LetterProofingStateDB(ProofingStateDB):

    ProofingStateClass = LetterProofingState

    def __init__(self, db_uri, db_name='eduid_idproofing_letter'):
        ProofingStateDB.__init__(self, db_uri, db_name)
