import unittest

from django.test import TestCase

from grd.models import User


class UserManagerTest(TestCase):
    def test_create_user(self):
        user_email = 'foo@localhost'
        user = User.objects.create_user(user_email)
        self.assertTrue(User.objects.filter(email=user_email).exists())
        self.assertEqual(user.email, user_email)
    
    def test_create_user_invalid_no_email(self):
        self.assertRaises(TypeError, User.objects.create_user)
        self.assertRaises(ValueError, User.objects.create_user, None)
    
    def test_create_superuser(self):
        user_email = 'super@localhost'
        user_pass = 'secret'
        user = User.objects.create_superuser(user_email, user_pass)
        self.assertTrue(User.objects.filter(email=user_email).exists())
        self.assertEqual(user.email, user_email)
        self.assertTrue(user.check_password, user_pass)


class UserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_email = 'foo@localhost'
        cls.user = User.objects.create_user(cls.user_email)
    
    def test_get_full_name(self):
        self.assertEqual(self.user_email, self.user.get_full_name())
    
    def test_get_short_name(self):
        self.assertEqual(self.user_email, self.user.get_short_name())
