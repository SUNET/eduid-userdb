# -*- coding: utf-8 -*-

from unittest import TestCase

from eduid_userdb.element import DuplicateElementViolation
from eduid_userdb.profile import Profile, ProfileList

__author__ = 'lundberg'


OPAQUE_DATA = {'a_string': 'I am a string', 'an_int': 3, 'a_list': ['eins', 2, 'drei'], 'a_map': {'some': 'data'}}


class ProfileTest(TestCase):
    def test_create_profile(self):
        profile = Profile(
            owner='test owner', schema='test schema', profile_data=OPAQUE_DATA, created_by='test created_by',
        )
        self.assertEqual(profile.owner, 'test owner')
        self.assertEqual(profile.schema, 'test schema')
        self.assertEqual(profile.created_by, 'test created_by')
        self.assertIsNotNone(profile.created_ts)
        for key, value in OPAQUE_DATA.items():
            self.assertIn(key, profile.profile_data)
            self.assertEqual(value, profile.profile_data[key])

    def test_profile_list(self):
        profile = Profile(
            owner='test owner 1', schema='test schema', profile_data=OPAQUE_DATA, created_by='test created_by',
        )
        profile2 = Profile(
            owner='test owner 2', created_by='test created_by', schema='test schema', profile_data=OPAQUE_DATA,
        )

        profile_list = ProfileList([profile, profile2])
        self.assertIsNotNone(profile_list)
        self.assertEqual(profile_list.count, 2)
        self.assertIsNotNone(profile_list.find('test owner 1'))
        self.assertIsNotNone(profile_list.find('test owner 2'))

    def test_empty_profile_list(self):
        profile_list = ProfileList([])
        self.assertIsNotNone(profile_list)
        self.assertEqual(profile_list.count, 0)

    def test_profile_list_owner_conflict(self):
        profile = Profile(
            owner='test owner 1', schema='test schema', profile_data=OPAQUE_DATA, created_by='test created_by',
        )
        profile_dict = profile.to_dict()
        profile2 = Profile.from_dict(profile_dict)

        with self.assertRaises(DuplicateElementViolation):
            ProfileList([profile, profile2])
