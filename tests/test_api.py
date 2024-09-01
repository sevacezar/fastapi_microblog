"""Module with the API-tests."""

import os

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User, followers
from tweets.models import Tweet
from images.models import Media
from likes.models import likes


class TestTweets:
    """Class with unit-tests of operations with tweets."""

    async def test_create_tweet_no_image_success(
            self,
            client: AsyncClient,
            db: AsyncSession,
            test_user_1: User,
    ):
        """Function for testing POST-request of creation new tweet without images."""
        # Tweet sending
        tweet_json: dict = {'tweet_data': 'New tweet'}
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Check API
        assert response.status_code == 200
        content = response.json()
        assert content.get('result')
        assert content.get('tweet_id') == 1

        # Check DB
        tweet = await db.execute(select(Tweet).filter(Tweet.id == 1))
        tweet = tweet.scalars().one_or_none()
        assert tweet
        assert tweet.content == 'New tweet'

    async def test_create_tweet_no_image_api_key_empty(
            self,
            client: AsyncClient,
            db: AsyncSession,
    ):
        """Function for testing POST-request of creation new tweet
        without images with error of empty api-key."""
        # Tweet sending
        tweet_json: dict = {'tweet_data': 'New tweet1'}
        response = await client.post('/api/tweets', json=tweet_json)

        # Check API
        assert response.status_code == 404
        content = response.json()
        assert content.get('result') == False
        assert content.get('error_type') == 'UserNotFoundError'
        assert content.get('error_message') == 'Passed api-key is empty'

    async def test_create_tweet_no_image_api_key_invalid(
            self,
            client: AsyncClient,
            db: AsyncSession,
    ):
        """Function for testing POST-request of creation new tweet
        without images with error of invalid api-key."""
        # Tweet sending
        tweet_json: dict = {'tweet_data': 'New tweet1'}
        headers: dict = {'api-key': 'wrong'}
        response = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Check API
        assert response.status_code == 404
        content = response.json()
        assert content.get('result') == False
        assert content.get('error_type') == 'UserNotFoundError'
        assert content.get('error_message') == 'User with the passed api-key is not exist'

    async def test_get_tweets_success(
            self,
            client: AsyncClient,
            db: AsyncSession,
            test_user_1: User,
    ):
        """Function for testing GET-request of receiving tweets."""
        # Tweet sending
        tweet_json: dict = {'tweet_data': 'New tweet'}
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Tweet getting
        response = await client.get('/api/tweets', headers=headers)

        # Check API
        assert response.status_code == 200
        content = response.json()
        assert content.get('result')
        tweets = content.get('tweets')
        assert tweets
        assert tweets[-1].get('id') == 1
        assert tweets[-1].get('content') == 'New tweet'
        assert not tweets[-1].get('attachemtnts')
        author = tweets[-1].get('author')
        assert author
        assert author.get('id') == test_user_1.id
        assert author.get('name') == test_user_1.name
        assert tweets[-1].get('likes') == []

    async def test_create_tweet_no_image_validation_error(
            self,
            client: AsyncClient,
            test_user_1: User,
    ):
        """Function for testing POST-request of creation new tweet without images."""
        # Tweet sending
        tweet_json: dict = {'tweet_info': 'Some text'}
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Check API
        assert response.status_code == 422
        content = response.json()
        assert content.get('result') == False
        assert content.get('error_type') == 'ValidationError'

    async def test_delete_tweet_success(
            self,
            client: AsyncClient,
            db: AsyncSession,
            test_user_1: User,
    ):
        """Function for testing DELETE-request of deleting tweet by user-creator."""
        # Tweet sending
        tweet_json: dict = {'tweet_data': 'New tweet from new user'}
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Tweet deleting
        tweet_id = response.json().get('tweet_id')
        response = await client.delete(f'/api/tweets/{tweet_id}', headers=headers)

        # Check API
        assert response.status_code == 200
        content = response.json()
        assert content.get('result')

        # Check DB
        tweet = await db.execute(select(Tweet).filter(Tweet.id == tweet_id))
        tweet = tweet.scalars().one_or_none()
        assert not tweet

    async def test_delete_tweet_other_user_error(
            self,
            client: AsyncClient,
            db: AsyncSession,
            test_user_1: User,
            test_user_2: User,
    ):
        """Function for testing DELETE-request of deleting tweet by user-non-creator."""
        # Tweet sending
        tweet_json: dict = {'tweet_data': 'New tweet'}
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Tweet deleting
        tweet_id = response.json().get('tweet_id')
        headers_other_user = {'api-key': test_user_2.api_key}
        response = await client.delete(f'/api/tweets/{tweet_id}', headers=headers_other_user)

        # Check API
        assert response.status_code == 403
        content = response.json()
        assert content.get('result') == False
        assert content.get('error_type') == 'NonUserTweetError'
        assert content.get('error_message') == 'Deleting a tweet that does not belong to the user'

    async def test_delete_tweet_invalid_id_error(
            self,
            client: AsyncClient,
            db: AsyncSession,
            test_user_1: User,
    ):
        """Function for testing DELETE-request of deleting tweet with unexisting id."""
        # Tweet sending
        tweet_json: dict = {'tweet_data': 'New tweet'}
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Tweet deleting
        tweet_id = 100
        response = await client.delete(f'/api/tweets/{tweet_id}', headers=headers)

        # Check API
        assert response.status_code == 404
        content = response.json()
        assert content.get('result') == False
        assert content.get('error_type') == 'TweetNotFoundError'
        assert content.get('error_message') == 'Tweet with the passed id is not exist'


class TestMedia:
    """Class with unit-tests of operations with media."""

    async def test_upload_image_success(
            self,
            client: AsyncClient,
            db: AsyncSession,
            test_user_1: User,
    ):
        """Function for testing POST-request of uploading image."""
        # File sending
        file_data: dict = {'file': ('norm_image.jpeg', b'Test file image')}
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post('/api/medias', headers=headers, files=file_data) # to save file start <$ pytest> from test directory
        
        # Check API
        assert response.status_code == 200
        content = response.json()
        assert content.get('result')
        assert content.get('media_id') == 1

        # Check DB
        image = await db.execute(select(Media).filter(Media.id == 1))
        image = image.scalars().one_or_none()
        assert image
        assert image.name == str(image.id) + '.jpeg'
        os.remove(os.path.join('..', 'static', 'images', '1.jpeg'))

    async def test_upload_image_size_error(
            self,
            client: AsyncClient,
            test_user_1: User,
    ):
        """Function for testing POST-request of uploading image
        with error of too large size of file."""
        # File sending
        file_data: dict = {'file': ('large_image.jpeg', b'1' * 6 * 1024 * 1024)}
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post('/api/medias', headers=headers, files=file_data) # to save file start <$ pytest> from test directory

        # Check API
        assert response.status_code == 413
        content = response.json()
        assert content.get('result') == False
        assert content.get('error_type') == 'FileSizeError'
        assert content.get('error_message') == 'Size of the file is larger than 5 MB'

    async def test_upload_image_type_error(
            self,
            client: AsyncClient,
            test_user_1: User,
    ):
        """Function for testing POST-request of uploading image
        with error of invalid file type."""
        # File sending
        file_data: dict = {'file': ('text_image.txt', b'Test file')}
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post('/api/medias', headers=headers, files=file_data) # to save file start <$ pytest> from test directory

        # Check API
        assert response.status_code == 400
        content = response.json()
        assert content.get('result') == False
        assert content.get('error_type') == 'FileTypeError'
        assert content.get('error_message') == 'Not allowed file extension. Alowed extensions: jpg, jpeg, png, tiff, heic'
    
    async def test_create_tweet_with_image_success(
            self,
            client: AsyncClient,
            db: AsyncSession,
            test_user_1: User,
    ):
        """Function for testing POST-reqfileuest of creation new tweet with images."""
        # File sending
        file_data: dict = {'file': ('norm_image.jpeg', b'Test file image')}
        headers: dict = {'api-key': test_user_1.api_key}
        response_file = await client.post('/api/medias', headers=headers, files=file_data) # to save file start <$ pytest> from test directory
        media_id = response_file.json().get('media_id')

        # Tweet sending
        tweet_json: dict = {'tweet_data': 'Very new tweet', 'tweet_media_ids': [media_id]}
        headers: dict = {'api-key': test_user_1.api_key}
        response_tweet = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Check API
        assert response_file.status_code == 200
        assert media_id
        assert response_tweet.status_code == 200
        content = response_tweet.json()
        assert content.get('result')
        assert content.get('tweet_id') == 1

        # Check DB
        tweet = await db.execute(select(Tweet).filter(Tweet.id == 1))
        tweet = tweet.scalars().one_or_none()
        assert tweet
        assert tweet.content == 'Very new tweet'
        image = await db.execute(select(Media).filter(Media.id == 1))
        image = image.scalars().one_or_none()
        assert image
        assert image.tweet_id == 1
        os.remove(os.path.join('..', 'static', 'images', '1.jpeg'))


class TestLikes:
    """Class with unit-tests of operations with likes."""

    async def test_like_tweet_success(
            self,
            client: AsyncClient,
            db: AsyncSession,
            test_user_1: User,
            test_user_2: User,
    ):
        """Function for testing POST-request of creation new like successfully."""
        # Tweet sending
        tweet_json: dict = {'tweet_data': 'New tweet'}
        headers: dict = {'api-key': test_user_1.api_key}
        response_tweet = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Like posting
        headers_other_user: dict = {'api-key': test_user_2.api_key}
        tweet_id = response_tweet.json().get('tweet_id')
        response_like = await client.post(f'/api/tweets/{tweet_id}/likes', headers=headers_other_user)

        # Check API
        assert response_like.status_code == 200
        content = response_like.json()
        assert content.get('result')

        # Check DB
        likes_query = await db.execute(select(likes))
        likes_objs = likes_query.all()
        assert likes_objs
        assert likes_objs[0] == (1, 2)

    async def test_like_tweet_repeat_error(
            self,
            client: AsyncClient,
            test_user_1: User,
            test_user_2: User):
        """Function for testing POST-request of creation new like with repeat error."""
        # Tweet sending
        tweet_json: dict = {'tweet_data': 'New tweet'}
        headers: dict = {'api-key': test_user_1.api_key}
        response_tweet = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Like posting
        headers_other_user: dict = {'api-key': test_user_2.api_key}
        tweet_id = response_tweet.json().get('tweet_id')
        response_like = await client.post(f'/api/tweets/{tweet_id}/likes', headers=headers_other_user)

        # Repeat like posting
        headers_other_user: dict = {'api-key': test_user_2.api_key}
        tweet_id = response_tweet.json().get('tweet_id')
        response_like_repeat = await client.post(f'/api/tweets/{tweet_id}/likes', headers=headers_other_user)

        # Check API
        assert response_like_repeat.status_code == 400
        content = response_like_repeat.json()
        assert content.get('result') == False
        assert content.get('error_type') == 'RelationshipError'
        assert content.get('error_message') == 'The user has already liked this tweet'

    async def test_unlike_tweet_success(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_user_1: User,
        test_user_2: User,
    ):
        """Function for testing POST-request of deleting like successfully."""
        # Tweet sending
        tweet_json: dict = {'tweet_data': 'New tweet'}
        headers: dict = {'api-key': test_user_1.api_key}
        response_tweet = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Like posting
        headers_other_user: dict = {'api-key': test_user_2.api_key}
        tweet_id = response_tweet.json().get('tweet_id')
        response_like = await client.post(f'/api/tweets/{tweet_id}/likes', headers=headers_other_user)

        # Like deleting
        response_unlike = await client.delete(f'/api/tweets/{tweet_id}/likes', headers=headers_other_user)

        # Check API
        assert response_unlike.status_code == 200
        content = response_like.json()
        assert content.get('result')

        # Check DB
        likes_query = await db.execute(select(likes))
        likes_objs = likes_query.all()
        assert not likes_objs

    async def test_unlike_tweet_repeat_error(
            self,
            client: AsyncClient,
            test_user_1: User,
            test_user_2: User,
    ):
        """Function for testing POST-request of deleting like with repeat error."""
        # Tweet sending
        tweet_json: dict = {'tweet_data': 'New tweet'}
        headers: dict = {'api-key': test_user_1.api_key}
        response_tweet = await client.post('/api/tweets', json=tweet_json, headers=headers)

        # Like posting
        headers_other_user: dict = {'api-key': test_user_2.api_key}
        tweet_id = response_tweet.json().get('tweet_id')
        response_like = await client.post(f'/api/tweets/{tweet_id}/likes', headers=headers_other_user)

        # Like deleting
        response_unlike = await client.delete(f'/api/tweets/{tweet_id}/likes', headers=headers_other_user)

        # Like deleting repeat
        response_unlike_repeat = await client.delete(f'/api/tweets/{tweet_id}/likes', headers=headers_other_user)

        # Check API
        assert response_unlike_repeat.status_code == 400
        content = response_unlike_repeat.json()
        assert content.get('result') == False
        assert content.get('error_type') == 'RelationshipError'
        assert content.get('error_message') == 'There is no like on the tweet'


class TestUsers:
    """Class with unit-tests of operations with users."""

    async def test_follow_user_success(
            self,
            client: AsyncClient,
            db: AsyncSession,
            test_user_1: User,
            test_user_2: User,
    ):
        """Function for testing POST-request of following some user."""
        # Following
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post(f'/api/users/{test_user_2.id}/follow',
                                     headers=headers)

        # Check API
        assert response.status_code == 200
        content = response.json()
        assert content.get('result')

        # Check DB
        follow_relationship = await db.execute(select(followers))
        follow_relationship = follow_relationship.first()
        assert follow_relationship
        follower_id, followed_id = follow_relationship
        assert follower_id == 1
        assert followed_id == 2

    async def test_follow_user_repeat_error(
            self,
            client: AsyncClient,
            test_user_1: User,
            test_user_2: User,
    ):
        """Function for testing POST-request of following some user with repeat error."""
        # Following
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post(
            f'/api/users/{test_user_2.id}/follow',
            headers=headers,
        )

        # Repeat following
        response_repeat = await client.post(
            f'/api/users/{test_user_2.id}/follow',
            headers=headers,
        )

        # Check API
        assert response_repeat.status_code == 400
        content = response_repeat.json()
        assert content.get('result') == False
        assert content.get('error_type') == 'RelationshipError'
        assert content.get('error_message') == 'You are already follow this user'

    async def test_unfollow_user_success(
            self,
            client: AsyncClient,
            db: AsyncSession,
            test_user_1: User,
            test_user_2: User,
    ):
        """Function for testing DELETE-request of unfollowing some user."""
            # Following
        headers: dict = {'api-key': test_user_1.api_key}
        response_following = await client.post(
            f'/api/users/{test_user_2.id}/follow',
            headers=headers,
        )

        # Unfollowing
        response_unfollowing = await client.delete(
            f'/api/users/{test_user_2.id}/follow',
            headers=headers,
        )

        # Check API
        assert response_unfollowing.status_code == 200
        content = response_unfollowing.json()
        assert content.get('result')

        # Check DB
        follow_relationship = await db.execute(select(followers))
        follow_relationship = follow_relationship.all()
        assert not follow_relationship

    async def test_unfollow_user_repeat_error(
            self,
            client: AsyncClient,
            test_user_1: User,
            test_user_2: User,
    ):
        """Function for testing DELETE-request of unfollowing some user with repeat error."""
        # Following
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.post(
            f'/api/users/{test_user_2.id}/follow',
            headers=headers,
        )

        # Unfollowing
        response_unfollowing = await client.delete(
            f'/api/users/{test_user_2.id}/follow',
            headers=headers,
        )

        # Repeat following
        response_unfollowing_repeat = await client.delete(
            f'/api/users/{test_user_2.id}/follow',
            headers=headers,
        )

        # Check API
        assert response_unfollowing_repeat.status_code == 400
        content = response_unfollowing_repeat.json()
        assert content.get('result') == False
        assert content.get('error_type') == 'RelationshipError'
        assert content.get('error_message') == 'You are not already follow this user'

    async def test_get_my_user_info_success(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_user_1: User,
    ):
        """Function for testing GET-request of following some user."""
        # Getting info
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.get(f'/api/users/me', headers=headers)

        # Check API
        assert response.status_code == 200
        content = response.json()
        assert content.get('result')
        user_info = content.get('user')
        assert user_info
        assert user_info.get('id') == test_user_1.id
        assert user_info.get('name') == test_user_1.name
        assert user_info.get('followers') == []
        assert user_info.get('following') == []

    async def test_get_other_user_info_success(
            self,
            client: AsyncClient, 
            test_user_1: User,
            test_user_2: User,
    ):
        """Function for testing GET-request of following some user."""
        # Getting info
        headers: dict = {'api-key': test_user_1.api_key}
        response = await client.get(f'/api/users/{test_user_2.id}', headers=headers)

        # Check API
        assert response.status_code == 200
        content = response.json()
        assert content.get('result')
        user_info = content.get('user')
        assert user_info
        assert user_info.get('id') == test_user_2.id
        assert user_info.get('name') == test_user_2.name
        assert user_info.get('followers') == []
        assert user_info.get('following') == []
