# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
import bcrypt


class Avatars(models.Model):
    avatar = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = "Avatars"


class Favorites(models.Model):
    userid = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    titleid = models.ForeignKey(
        "Titles", models.DO_NOTHING, db_column="titleId"
    )  # Field name made lowercase.
    addeddate = models.DateTimeField(
        db_column="addedDate"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Favorites"


class Followers(models.Model):
    followerid = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="followerId", related_name="follower"
    )  # Field name made lowercase.
    followedid = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="followedId", related_name="followed"
    )  # Field name made lowercase.
    addeddate = models.DateTimeField(
        db_column="addedDate"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Followers"


class Genretypes(models.Model):
    genre = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = "GenreTypes"


class Genres(models.Model):
    titleid = models.ForeignKey(
        "Titles", models.DO_NOTHING, db_column="titleId"
    )  # Field name made lowercase.
    genreid = models.ForeignKey(
        Genretypes, models.DO_NOTHING, db_column="genreId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Genres"


class Names(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "Names"


class Participantcategories(models.Model):
    category = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = "ParticipantCategories"


class Participants(models.Model):
    titleid = models.ForeignKey(
        "Titles", models.DO_NOTHING, db_column="titleId"
    )  # Field name made lowercase.
    personid = models.ForeignKey(
        Names, models.DO_NOTHING, db_column="personId"
    )  # Field name made lowercase.
    category = models.ForeignKey(
        Participantcategories, models.DO_NOTHING, db_column="category"
    )

    class Meta:
        managed = False
        db_table = "Participants"


class Pending(models.Model):
    userid = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    titleid = models.ForeignKey(
        "Titles", models.DO_NOTHING, db_column="titleId"
    )  # Field name made lowercase.
    addeddate = models.DateTimeField(
        db_column="addedDate"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Pending"


class Ratings(models.Model):
    posterid = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="posterId"
    )  # Field name made lowercase.
    titleid = models.ForeignKey(
        "Titles", models.DO_NOTHING, db_column="titleId"
    )  # Field name made lowercase.
    rating = models.FloatField()
    addeddate = models.DateTimeField(
        db_column="addedDate"
    )  # Field name made lowercase.
    comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Ratings"


class Titletypes(models.Model):
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = "TitleTypes"


class Titles(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    titletype = models.ForeignKey(
        Titletypes, models.DO_NOTHING, db_column="titleType"
    )  # Field name made lowercase.
    primarytitle = models.CharField(
        db_column="primaryTitle", max_length=255
    )  # Field name made lowercase.
    originaltitle = models.CharField(
        db_column="originalTitle", max_length=255
    )  # Field name made lowercase.
    startyear = models.IntegerField(db_column="startYear")  # Field name made lowercase.
    endyear = models.IntegerField(db_column="endYear")  # Field name made lowercase.
    runtimeminutes = models.IntegerField(
        db_column="runtimeMinutes"
    )  # Field name made lowercase.
    language = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    isoriginaltitle = models.IntegerField(
        db_column="isOriginalTitle"
    )  # Field name made lowercase.
    imdbrating = models.FloatField(db_column="imdbRating")  # Field name made lowercase.
    imdbratingcount = models.IntegerField(
        db_column="imdbRatingCount"
    )  # Field name made lowercase.
    cover = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    translatedtitle = models.CharField(
        db_column="translatedTitle", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Titles"


class Tokens(models.Model):
    userid = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    token = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = "Tokens"


class Users(models.Model):
    username = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    phone = models.CharField(unique=True, max_length=255, blank=True, null=True)
    birthdate = models.DateField(db_column="birthDate")  # Field name made lowercase.
    registerdate = models.DateTimeField(
        db_column="registerDate"
    )  # Field name made lowercase.
    avatarid = models.ForeignKey(
        Avatars, models.DO_NOTHING, db_column="avatarId"
    )  # Field name made lowercase.
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "Users"

    # Set encrypted password
    def set_password(self, raw_password):
        encoded_password = raw_password.encode("utf8")
        self.password = bcrypt.hashpw(encoded_password, bcrypt.gensalt(rounds=14))

    # Check if given password matches set password
    def check_password(self, raw_password):
        # Se obtiene la contraseña almacenada
        selfpw = self.password

        # Si la contraseña almacenada es un byte array guayrdado como string, se recorta
        if isinstance(selfpw, str) and selfpw.startswith("b'") and selfpw.endswith("'"):
            selfpw = selfpw[2:-1].encode("utf-8")

        # Se comprueba que las contraseñas coinciden
        return bcrypt.checkpw(raw_password.encode("utf-8"), selfpw)
