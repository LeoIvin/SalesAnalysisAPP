        Profile.objects.create(user=instance, first_name='', last_name='')

# Signal receiver function,  save the Profile whenever the User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()