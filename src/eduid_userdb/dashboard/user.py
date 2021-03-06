#
# Copyright (c) 2014 NORDUnet A/S
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
# Authors : Enrique Perez Arnaud <enrique@cazalla.net>
#           Fredrik Thulin <fredrik@thulin.net>
#

import copy
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

import bson

from eduid_userdb import User
from eduid_userdb.exceptions import UserDBValueError, UserOutOfSync

log = logging.getLogger('eduiddashboard')


@dataclass
class DashboardUser(User):
    """
    Subclass of eduid_userdb.User with eduid Dashboard application specific data.
    """

    def add_letter_proofing_data(self, data):
        """
        Add letter proofing data about the user.

        This is data from the time a user successfully verified their NIN using
        the letter proofing service. We keep it on the users for now, but expect
        to move it somewhere else and have a reference to it as metadata on the
        verified Nin instead.

        NOTE: The User.__init__ function will actually accept and copy the
              'letter_proofing_data', although ordinary User objects doesn't do
              anything else with this data.

        :param data: Proofing data from the letter id proofing service
        :type  data: [dict]
        """
        if not isinstance(data, dict):
            raise TypeError('letter_proofing_data must be dict, not {!s}'.format(type(data)))
        old_data = self._data.get('letter_proofing_data', [])
        self._data['letter_proofing_data'] = old_data + [data]


class DashboardLegacyUser(object):
    """
    Class to embody users as they are stored on MongoDB,
    that provides methods to access their attributes.

    :param data: MongoDB document representing a user
    :type  data: dict
    """

    def __init__(self, data):
        if type(data) is DashboardLegacyUser:
            self._mongo_doc = data._mongo_doc
        else:
            self._mongo_doc = data

    def __repr__(self):
        return '<DashboardLegacyUser: {!s}/{!s}>'.format(self.get_eppn(), self.get('_id'))

    def __getitem__(self, key):
        return self._mongo_doc[key]

    def items(self):
        return self._mongo_doc.items()

    def keys(self):
        return self._mongo_doc.keys()

    def save(self, request, check_sync=True, update_doc=None):
        '''
        Save the user in MongoDB.

        :param request: the HTTP request
        :type  request: webob.request.BaseRequest
        :param check_sync: whether we want to check that the user is in sync
        :type check_sync: bool
        :param update_doc: if we want to save a doc other that self._mongo_doc.
                           if it is a partial doc, it must carry the '$set' key.
        :type update_doc: dict
        '''
        # Flush out any postalAddress that might exist on really old users.
        # The user will not be parsed by the code in eduid-dashboard-amp if
        # we put postalAddress in profiles documents.
        if 'postalAddress' in self._mongo_doc:
            del self._mongo_doc['postalAddress']
        modified = self.get_modified_ts()
        self.set_modified_ts(datetime.utcnow())
        if update_doc is None:
            update_doc = self._mongo_doc
        test_doc = {'_id': self.get_id()}
        if check_sync and modified:
            test_doc['modified_ts'] = modified
        result = request.db.profiles.update_one(test_doc, update_doc, upsert=(not check_sync))
        if result['n'] == 0:
            if check_sync:
                raise UserOutOfSync('The user data has been modified ' 'since you started editing it.')
            log.info("Tried saving user {!s} (test_doc {!s}) but failed (no check_sync)".format(self, test_doc))
        request.context.propagate_user_changes(self)

    def get_doc(self):
        '''
        Retrieve the MongoDB document.

        :return: dict
        '''
        return self._mongo_doc

    def get(self, attr, default=''):
        '''
        Get the value of an attribute of the user by name.

        :param attr: name of the attribute
        :param default: default value to return if the attr is missing
        :type attr: str
        :type default: object

        :return: str | list
        '''
        return self._mongo_doc.get(attr, default)

    def get_id(self):
        '''
        Get the user's oid in MongoDB.

        :return: bson.ObjectId
        '''
        if not '_id' in self._mongo_doc:
            raise UserDBValueError('No user_id in user')
        return self._mongo_doc['_id']

    def get_preferred_language(self):
        '''
        Get the ISO 639-1 code (2 letter code)
        of the user's preferred language

        :return: str
        '''
        return self._mongo_doc.get('preferredLanguage', None)

    def get_modified_ts(self):
        '''
        Get the timestamp for the last modification time of the user
        in the dashboard.

        :return: datetime
        :rtype: datetime
        '''
        return self._mongo_doc.get('modified_ts', None)

    def retrieve_modified_ts(self, profiles):
        try:
            userid = self.get_id()
        except UserDBValueError:
            log.debug("User {!s} has no id, setting modified_ts to None".format(self))
            self._mongo_doc['modified_ts'] = None
        else:
            profiles_user = profiles.find_one({'_id': userid})
            if profiles_user is None:
                log.debug("User {!s} not found in profiles ({!s}), setting modified_ts to None".format(self, profiles))
                self._mongo_doc['modified_ts'] = None
            else:
                try:
                    self._mongo_doc['modified_ts'] = profiles_user['modified_ts']
                    log.debug("Using modified_ts from profiles user {!s}: {!s}".format(self, self.get_modified_ts()))
                except KeyError:
                    self._mongo_doc['modified_ts'] = datetime.utcnow()
                    log.debug(
                        "Updating user {!s} in profiles {!s} with new modified_ts: {!s}".format(
                            self, profiles, self.get_modified_ts()
                        )
                    )
                    profiles.replace_one({'_id': userid,}, self._mongo_doc)

    def set_modified_ts(self, ts):
        '''
        Set the timestamp for the last modification of the user.

        :param ts:  present timestamp
        :type  ts: datetime
        '''
        self._mongo_doc['modified_ts'] = ts

    def get_given_name(self):
        '''
        Get the user's givenName.

        :return: str
        '''
        return self._mongo_doc.get('givenName', '')

    def set_given_name(self, name):
        '''
        Set the user's givenName.

        :param name: the givenName to set
        :type  name: str
        '''
        self._mongo_doc['givenName'] = name

    def get_display_name(self):
        '''
        Get the user's displayName.

        :return: str
        '''
        return self._mongo_doc.get('displayName', '')

    def set_display_name(self, name):
        '''
        Set the user's displayName.

        :param name: the displayName to set
        :type  name: str
        '''
        self._mongo_doc['displayName'] = name

    def get_sn(self):
        '''
        Get the user's sn (family name).

        :return: str
        '''
        return self._mongo_doc.get('sn', '')

    def set_sn(self, sn):
        '''
        Set the user's sn (family name).

        :param sn: the sn to set
        :type  sn: str
        '''
        self._mongo_doc['sn'] = sn

    def get_mail(self):
        '''
        Get the user's main email address.

        :return: str
        '''
        return self._mongo_doc.get('mail', '')

    def set_mail(self, mail):
        '''
        Set the user's main email address.

        :param mail: the email address to set
        :type  mail: str
        '''
        self._mongo_doc['mail'] = mail

    def get_mail_aliases(self):
        '''
        Get the user's email addresses,
        as a list of dictionaries with the form:
            {
            'email': 'johnsmith@example.com',
            'verified': False,
            }

        :return: list
        '''
        return self._mongo_doc.get('mailAliases', [])

    def set_mail_aliases(self, emails):
        '''
        Set the user's email addresses,
        given as a list of dictionaries with the form:
            {
            'email': 'johnsmith@example.com',
            'verified': False,
            }
        This removes any previous list of email addresses
        that the user might have had.

        :param emails: the email addresses to set
        :type  emails: list
        '''
        self._mongo_doc['mailAliases'] = emails

    def add_verified_email(self, verified_email):
        '''
        Pick one email address from the user's list
        and set it as verified.
        If it is the only email address the user has,
        set it as the user's primary address.

        :param verified_email: the verified address
        :type verified_email: str
        '''
        emails = self._mongo_doc['mailAliases']
        for email in emails:
            if email['email'] == verified_email:
                email['verified'] = True
                if len(emails) == 1:
                    self.set_mail(email['email'])

    def get_nins(self):
        '''
        Get the user's National Identification Numbers,
        as a list of strings.

        :return: list
        '''
        return self._mongo_doc.get('norEduPersonNIN', [])

    def set_nins(self, nins):
        '''
        Set the user's National Identification Numbers,
        given as a list of strings.
        This removes any previous list
        that the user might have had.

        :param nins: the National Identification Numbers to set
        :type  nins: list
        '''
        self._mongo_doc['norEduPersonNIN'] = nins

    def has_nin(self):
        '''
        Check whether the user has any National Identification Numbers.

        :return: bool
        '''
        if self._mongo_doc.get('norEduPersonNIN', []):
            return True
        return False

    def add_verified_nin(self, verified_nin):
        '''
        Add a verified National Identification Number to the user's list

        :param verified_nin: the verified NIN
        :type  verified_nin: str
        '''
        if self.has_nin():
            self._mongo_doc['norEduPersonNIN'].append(verified_nin)
        else:
            self._mongo_doc['norEduPersonNIN'] = [verified_nin]

    def get_addresses(self):
        '''
        Get the user's postal addresses,
        as a list of dictionaries with the form:
            {
            'type': 'home',
            'country': 'SE',
            'address': "Long street, 48",
            'postalCode': "123456",
            'locality': "Stockholm",
            'verified': True,
            }

        :return: list
        '''
        return self._mongo_doc.get('postalAddress', [])

    def set_addresses(self, addresses):
        '''
        Set the user's postal addresses,
        given as a list of dictionaries with the form:
            {
            'type': 'home',
            'country': 'SE',
            'address': "Long street, 48",
            'postalCode': "123456",
            'locality': "Stockholm",
            'verified': True,
            }
        This removes any previous list of addresses
        that the user might have had.

        :param addresses: the addresses to set
        :type  addresses: list
        '''
        self._mongo_doc['postalAddress'] = addresses

    def retrieve_address(self, request, verified_nin):
        """ 
        Get the official postal address for a user
        from the government service,
        remove any previous official address that the user might have,
        and set the retrieved address
        as her new official and verified postal address.

        :param request: HTTP request
        :type  request: webob.request.BaseRequest
        :param verified_nin: The verified NIN that identifies the user
        :type  verified_nin: str
        """

        if not request.registry.settings.get('enable_postal_address_retrieve', True):
            return

        address = request.msgrelay.get_postal_address(verified_nin)

        address['type'] = 'official'
        address['verified'] = True

        user_addresses = self.get_addresses()

        for old_address in user_addresses:
            if old_address.get('type') == 'official':
                user_addresses.remove(old_address)
                user_addresses.append(address)
                break
        else:
            user_addresses.append(address)

    def get_mobiles(self):
        '''
        Get the user's mobile phone numbers,
        as a list of dictionaries with the form:
            {
            'mobile': '666666666',
            'verified': True
            }

        :return: list
        '''
        return self._mongo_doc.get('mobile', [])

    def set_mobiles(self, mobiles):
        '''
        Set the user's mobile phone numbers,
        given as a list of dictionaries with the form:
            {
            'mobile': '666666666',
            'verified': True
            }
        This removes any previous list of numbers
        that the user might have had.

        :param mobiles: the mobile numbers to set
        :type  mobiles: list
        '''
        self._mongo_doc['mobile'] = mobiles

    def add_mobile(self, mobile):
        '''
        Add a mobile phone number to the user's list of mobiles,
        given as a dictionary with the form:
            {
            'mobile': '666666666',
            'verified': True
            }

        :param mobile: the mobile number to add
        :type  mobile: dict
        '''
        mobiles = self.get_mobiles()
        mobiles.append(mobile)
        self.set_mobiles(mobiles)

    def add_verified_mobile(self, verified_mobile):
        '''
        Pick one mobile phone number from the user's list
        and set it as verified.
        If it is the only mobile number the user has,
        set it as the user's primary mobile.

        :param verified_mobile: the verified mobile number
        :type  verified_mobile: str
        '''
        mobiles = self._mongo_doc['mobile']

        for mobile in mobiles:
            if mobile['mobile'] == verified_mobile:
                mobile['verified'] = True
                if len(mobiles) == 1:
                    mobile['primary'] = True

    def get_passwords(self):
        '''
        Get the user's passwords
        as a list of dictionaries with the form:
            {
            'id': ObjectId('112345678901234567890123'),
            'salt': '$NDNv1H1$9c810d852430b62a9a7c6159d5d64c41c3831846f81b6799b54e1e8922f11545$32$32$',
            'source' : 'signup', 
            'created_ts' : ISODate('2013-11-28T13:33:44.479Z')
            }

        :return: list
        '''
        # Make a copy since caller might manipulate this dict (like adding user_id_hint,
        # breaking other test cases later on)
        return copy.deepcopy(self._mongo_doc.get('passwords', []))

    def set_passwords(self, passwords):
        '''
        Set the user's passwords
        given as a list of dictionaries with the form:
            {
            'id': ObjectId('112345678901234567890123'),
            'salt': '$NDNv1H1$9c810d852430b62a9a7c6159d5d64c41c3831846f81b6799b54e1e8922f11545$32$32$',
            'source' : 'signup', 
            'created_ts' : ISODate('2013-11-28T13:33:44.479Z')
            }
        This removes any previous list of passwords
        that the user might have had.

        :param passwords: the passwords to set
        :type  passwords: list
        '''
        self._mongo_doc['passwords'] = passwords

    def get_entitlements(self):
        '''
        Get the user's entitlements as a list of 
        names within the MACE URN urn:mace:eduid.se:role namespace,
        for example:
            [
            'urn:mace:eduid.se:role:admin',
            'urn:mace:eduid.se:role:student'
            ]

        :return: list
        '''
        return self._mongo_doc.get('eduPersonEntitlement', [])

    def set_entitlements(self, entitlements):
        '''
        Set the user's entitlements as a list of 
        names within the MACE URN urn:mace:eduid.se:role namespace, like:
            [
            'urn:mace:eduid.se:role:admin',
            'urn:mace:eduid.se:role:student'
            ]
        This removes any previous list of entitlements
        that the user might have had.

        :param entitlements: the entitlements to set
        :type  entitlements: list
        '''
        self._mongo_doc['eduPersonEntitlement'] = entitlements

    def get_eppn(self):
        '''
        Get the user's eduPersonPrincipalName.

        :return: str
        '''
        return self._mongo_doc.get('eduPersonPrincipalName', '')

    def set_terminated(self, terminate=True):
        '''
        Flag the account as terminated.

        :param terminate: whether we are terminating
                          or reactivating the account
        :type  terminate: bool
        '''
        if terminate:
            terminated_ts = datetime.utcnow()
        else:
            terminated_ts = None
        self._mongo_doc['terminated'] = terminated_ts

    def is_terminated(self):
        '''
        Find out if (and when) the account for this user
        has been set as terminated.

        :return: bool or datetime
        '''
        return self._mongo_doc.get('terminated', None)

    def get_letter_proofing_data(self):
        '''
        Get letter proofing data for the user.

        :rtype: [dict]
        '''
        return self._mongo_doc.get('letter_proofing_data', [])

    def set_letter_proofing_data(self, data):
        '''
        Store letter proofing data on the user.

        :param data: Proofing data from the letter id proofing service
        :type  data: [dict]
        '''
        self._mongo_doc['letter_proofing_data'] = data
