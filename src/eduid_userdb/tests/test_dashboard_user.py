import copy
from unittest import TestCase

from eduid_userdb.credentials import CredentialList
from eduid_userdb.dashboard import DashboardLegacyUser as User
from eduid_userdb.dashboard.user import DashboardUser
from eduid_userdb.exceptions import UserMissingData
from eduid_userdb.fixtures.users import mocked_user_standard, new_user_example


class TestUser(TestCase):
    def test_verify_mail_and_set_as_primary(self):
        user = User(mocked_user_standard.to_dict())

        # Save the original information so that
        # we can restore it after this test.
        old_mail_aliases = user.get_mail_aliases()
        old_mail = user.get_mail()

        # Remove the existing aliases and add one unverified
        user.set_mail_aliases([])
        user.set_mail_aliases([{'email': 'testmail@example.com', 'verified': False,}])

        # Verify the only existing mail alias and since it
        # is the only existing mail address, set it as primary.
        user.add_verified_email('testmail@example.com')

        self.assertEqual(user.get_mail_aliases(), [{'verified': True, 'email': 'testmail@example.com'}])
        self.assertEqual(user.get_mail(), 'testmail@example.com')

        # Restore the old mail settings for other tests
        user.set_mail_aliases(old_mail_aliases)
        user.set_mail(old_mail)


class TestPdataUser(TestCase):
    def test_proper_user(self):
        userdata = new_user_example.to_dict()
        user = DashboardUser.from_dict(data=userdata)
        self.assertEqual(user.user_id, userdata['_id'])
        self.assertEqual(user.eppn, userdata['eduPersonPrincipalName'])

    def test_proper_new_user(self):
        userdata = new_user_example.to_dict()
        userid = userdata.pop('_id')
        eppn = userdata.pop('eduPersonPrincipalName')
        passwords = CredentialList(userdata['passwords'])
        user = DashboardUser.construct_user(_id=userid, eppn=eppn, passwords=passwords)
        self.assertEqual(user.user_id, userid)
        self.assertEqual(user.eppn, eppn)

    def test_missing_id(self):
        userdata = new_user_example.to_dict()
        userid = userdata.pop('_id')
        eppn = userdata.pop('eduPersonPrincipalName')
        passwords = CredentialList(userdata['passwords'])
        user = DashboardUser.construct_user(eppn=eppn, passwords=passwords)
        self.assertNotEqual(user.user_id, userid)

    def test_missing_eppn(self):
        userdata = new_user_example.to_dict()
        userid = userdata.pop('_id')
        userdata.pop('eduPersonPrincipalName')
        with self.assertRaises(UserMissingData):
            DashboardUser.construct_user(_id=userid, **userdata)
