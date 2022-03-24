from typing import Tuple
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status

from ..models import Account, Follow, FollowerPetition


class AccountTest(TestCase):

    def setUp(self):

        # Data
        self.mario_data = {
            'username': 'mario',
            'password': 'secret_001',
            'first_name': 'Mario',
            'last_name': 'A.'
        }

        self.daniel_data = {
            'username': 'daniel',
            'password': 'secret_001',
            'first_name': 'Daniel',
            'last_name': 'B.'
        }

        # Registration
        users, accounts = registration(self.daniel_data, self.mario_data)
        self.assertEquals(users, 2)
        self.assertEquals(accounts, 2)

        # Login
        tokens = login(self.daniel_data, self.mario_data)
        self.assertEquals(tokens, 2)

        # Set up test clients (Mario and Daniel)
        self.mario_client, self.mario  = generateTestClient(self.mario_data['username'])
        self.daniel_client, self.daniel  = generateTestClient(self.daniel_data['username'])


    def test_account_delation(self):
        '''
        Deletes Mario's account
        '''
        self.mario_client.delete(f'/account/user/{self.mario.id}/')
        self.assertEqual(User.objects.filter(username=self.mario.username).count(), 0)
        self.assertEqual(Account.objects.filter(user__username=self.mario.username).count(), 0)

    def test_account_delation_forbidden(self):
        '''
        A user deletes someone else account.
        '''
        response = self.mario_client.delete(f'/account/user/{self.daniel.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.filter(username=self.daniel_data['username']).count(), 1)

    def test_petitions(self):
        # TODO: Send several petitions
        for _ in range(1):
            self.daniel_client.post(
                '/account/send_follower_petition/',
                {'user': self.mario.id}
            )

        # There must be only one petition
        petitions = FollowerPetition.objects.all().count()
        self.assertEquals(petitions, 1)

        # Get the list of petitions
        request = self.mario_client.post('/account/follower_petition_list/')
        self.assertEqual(len(request.data), 1)

        # Accept the petition
        self.mario_client.post(
            '/account/accept_follower_petition/',
            {'possible_follower': self.daniel.id}
        )

        # There must be 0 follower petitions and 1 follower
        follower_petitions = FollowerPetition.objects.all().count()
        self.assertEqual(follower_petitions, 0)
        followers = Follow.objects.all().count()
        self.assertEqual(followers, 1)


    def test_accept_follower_petition(self):
        # Daniel sends a following petition to mario
        client_daniel = APIClient()
        token_daniel = Token.objects.get(user__username='daniel')
        client_daniel.credentials(HTTP_AUTHORIZATION='Token ' + token_daniel.key)
        client_daniel.post(
            '/account/send_follower_petition/',
            {'user': User.objects.get(username='mario').id}
        )

        # Mario accepts Daniel's petition
        client_mario = APIClient()
        token_mario = Token.objects.get(user__username='mario')
        client_mario.credentials(HTTP_AUTHORIZATION='Token ' + token_mario.key)
        client_mario.post(
            '/account/accept_follower_petition/',
            {'possible_follower': User.objects.get(username='daniel').id}
        )

        # There must be 0 follower petitions and 1 follower
        follower_petition_number = FollowerPetition.objects.all().count()
        self.assertEqual(follower_petition_number, 0)
        follow_number = Follow.objects.all().count()
        self.assertEqual(follow_number, 1)

    def test_follower_petition_list(self):
        # Daniel sends a following petition to Mario
        client_daniel = APIClient()
        token_daniel = Token.objects.get(user__username='daniel')
        client_daniel.credentials(HTTP_AUTHORIZATION='Token ' + token_daniel.key)
        client_daniel.post(
            '/account/send_follower_petition/',
            {'user': User.objects.get(username='mario').id}
        )

        # Mario get the list of petitions
        client_mario = APIClient()
        token_mario = Token.objects.get(user__username='mario')
        client_mario.credentials(HTTP_AUTHORIZATION='Token ' + token_mario.key)
        response = client_mario.get('/account/follower_petition_list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


def registration(*users_data) -> Tuple[int, int]:
    '''
    Creates new users and returns the number of users and accounts in the DB
    '''
    client = APIClient()
    for user_data in users_data:
        client.post('/account/registration/', user_data, format='json')

    users_number = User.objects.all().count()
    accounts_number = Account.objects.all().count()
    return users_number, accounts_number

def login(*users_data) -> int:
    '''
    Login users and returns the number of tokens in the DB
    '''
    client = APIClient()
    for user_data in users_data:
        client.post(
            '/account/login/',
            {'username': user_data['username'], 'password': user_data['password']}
        )

    token_number = Token.objects.all().count()
    return token_number

def generateTestClient(username: str) -> Tuple[APIClient, User]:
    '''
    Generates an authenticated APIClient ready to perform HTTP requests.
    Returns the generated client as well as the user
    '''
    token = Token.objects.get(user__username=username)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    user = User.objects.get(username=username)
    return client, user