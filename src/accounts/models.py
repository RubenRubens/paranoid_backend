from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    bio = models.TextField(default='')
    profile_picture = models.ImageField(upload_to='uploads/', null=True)


class FollowerPetition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    possible_follower = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following_petition'
    )
    petition_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'possible_follower')


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'follower')

    def followers(user: User):
        queryset = Follow.objects.filter(user=user).values_list('follower', flat=True)
        return User.objects.filter(pk__in=queryset)

    def following(user: User):
        queryset = Follow.objects.filter(follower=user).values_list('user', flat=True)
        return User.objects.filter(pk__in=queryset)

    def __str__(self):
        return f'User: {self.user} - Follower: {self.follower}'

