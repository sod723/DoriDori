
# # Create your models here.
# class User(AbstractBaseUser):
#
#     # user_id = models.CharField(max_length=24, unique=True)
#     # user_name = models.CharField(max_length=24)
#     # user_email = models.EmailField(max_length=128, unique=True)
#     # user_phone = models.CharField(max_length=13)
#
#     # #is_passenger = models.BooleanField(default=True)
#     #
#     # USERNAME_FIELD = 'user_email'
#     #
#     #
#     # class Meta:
#     #     db_table = "User"
#
#     profile_image = models.TextField()  # 프로필 이미지
#     nickname = models.CharField(max_length=24, unique=True)
#     name = models.CharField(max_length=24, null=False)
#     email = models.EmailField(unique=True, null=False)
#     phonenum = models.CharField(max_length=24, null=False)
#
#     TYPE =(
#         ('passenger', 'passenger'),
#         ('driver', 'driver'),
#     )
#
#     type = models.CharField(max_length=100, null=True, choices=TYPE)
#     USERNAME_FIELD = 'nickname'
#
#
#     class Metaㅋ
#         db_table = "User"