from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)
# Create your models here.
class UserManager(BaseUserManager):
    
    #creates user with given email and password
    def create_user(self, email, first_name, last_name, gender, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            gender=gender,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    #creates staffuser with given email and password
    def create_staffuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
            first_name= "admin", 
            last_name="none",  
            gender="none"
        )
        user.staff = True
        user.save(using=self._db)
        return user

    
    #creates superuser with given email and password
    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
            first_name= "admin", 
            last_name=None,  
            gender=None
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user
    


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name    =   'email address',
        max_length      =   255,
        unique=True
    )
    active  =   models.BooleanField(default = True)  #false when user deletes his account
    staff   =   models.BooleanField(default = False) #an admin user; non super-user
    admin   =   models.BooleanField(default = False) #a superuser
    
    # extended
    first_name = models.CharField(
        max_length = 100, 
        blank = True, 
        null = True
    )
    last_name = models.CharField(
        max_length = 100, 
        blank = True, 
        null = True
    )
    GENDERs = (
		("Male", "Male"),
		("Female", "Female"),
		("Other", "Other")
	)
    gender = models.CharField(
        choices=GENDERs,
        max_length=20,
        default="Male",
        null = True
    )

    USERNAME_FIELD = 'email' #makes email the default username fielf
    REQUIRED_FIELDS = [] #email & password are required by default.

    objects = UserManager() #setting up user manager

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)
    

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active


class pics(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
 


class contact(models.Model):
    name = models.CharField(max_length = 100, blank = True, null = True)
    email = models.EmailField()
    comment = models.TextField()
    def __str__(self):
        return self.email

class history(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    time = models.DateTimeField()
    pic = models.CharField(max_length = 200, blank = True, null = True)
    STATUS_CHOICES  = (
        ('Vegetation Localization','Vegetation Localization'),
        ('Object Detection','Object Detection'),
        ('Land Use','Land Use'),
        ('Parameter','Parameter'),
    )
    selection = models.CharField(choices=STATUS_CHOICES,max_length=50, default="Crop Identification")
    def __str__(self):
        return str(self.user_id)


class newsalert(models.Model):
    email = models.EmailField()
    def __str__(self):
        return self.email