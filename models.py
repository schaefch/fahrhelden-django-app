from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


# from
# https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Die Email-Adresse is notwendig.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Root benötigt is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Root benötigt is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class BaseUser(AbstractUser):
    objects = UserManager()
    username = None
    first_name = models.CharField(max_length=128, verbose_name="Vorname")
    last_name = models.CharField(max_length=128, verbose_name="Nachname")
    email = models.EmailField(unique=True, verbose_name="Email-Adresse")
    is_confirmed = models.BooleanField(
        default=False, verbose_name="Identität bestätigt"
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class Bringer(BaseUser):
    street = models.CharField(max_length=128, verbose_name="Straße")
    house_nr = models.CharField(max_length=128, verbose_name="Hausnummer")
    zip_code = models.CharField(max_length=128, verbose_name="Postleitzahl")
    location = models.CharField(max_length=128, verbose_name="Ort")
    phone_number = models.CharField(
        max_length=128, verbose_name="Telefonnummer"
    )
    last_activity = models.DateTimeField(
        default=timezone.now, verbose_name="Letzte Verbindung"
    )
    birth_date = models.DateField(
        default=timezone.now, verbose_name="Geburtsdatum"
    )

    def __str__(self):
        deactivated_string = "[DEAKTIVIERT] " if not self.is_active else ""
        unconfirmed_string = "[UNBESTÄTIGT] " if not self.is_confirmed else ""
        return f"{deactivated_string}{unconfirmed_string} \
                {self.first_name} {self.last_name} \
                aus {self.location}"

    class Meta:
        verbose_name = "Fahrer"
        verbose_name_plural = "Fahrer"


class StaffUser(BaseUser):
    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff"


class RootUser(StaffUser):
    class Meta:
        verbose_name = "Root-User"


JOB_STATUS_CHOICES = (
    ("WAITING", "Wartet"),
    ("PENDING", "Lieferung läuft"),
    ("DONE", "Lieferung beendet"),
)


class JobStatus(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 128
        kwargs["choices"] = JOB_STATUS_CHOICES
        kwargs["default"] = "WAITING"
        super().__init__(*args, **kwargs)

    @staticmethod
    def toChoice(key):
        return dict(JOB_STATUS_CHOICES)[key]


class Amount(models.IntegerField):
    CHOICES = (
        (1, "Wenig"),
        (2, "Mittel"),
        (3, "Viel"),
    )

    def __init__(self, *args, **kwargs):
        kwargs["choices"] = self.CHOICES
        kwargs["default"] = 1
        super().__init__(*args, **kwargs)


class Job(models.Model):
    first_name = models.CharField(max_length=128, verbose_name="Vorname")
    last_name = models.CharField(max_length=128, verbose_name="Nachname")
    street = models.CharField(max_length=128, verbose_name="Straße")
    house_nr = models.CharField(max_length=128, verbose_name="Hausnummer")
    zip_code = models.CharField(max_length=128, verbose_name="Postleitzahl")
    location = models.CharField(max_length=128, verbose_name="Ort")
    phone_number = models.CharField(
        max_length=128, verbose_name="Telefonnummer"
    )
    buy_list = models.TextField(default="", verbose_name="Einkaufsliste")
    amount = Amount(verbose_name="Menge")
    placed_at = models.DateTimeField(
        default=timezone.now, verbose_name="Wartet seit"
    )
    driver = models.ForeignKey(
        Bringer,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Fahrer",
    )
    status = JobStatus(verbose_name="Lieferstatus")
    drivers_comment = models.CharField(
        blank=True, default="", max_length=128, verbose_name="Kommentar Fahrer"
    )

    def __str__(self):
        placed_at = self.placed_at.strftime("%d.%m.%Y um %H:%M:%S")
        driver_string = (
            "" if self.driver is None else f", Fahrer: {self.driver}"
        )

        return f"[{JobStatus.toChoice(self.status)}] #{self.id} \
             - {self.first_name} {self.last_name} aus {self.location}, \
             platziert am {placed_at}{driver_string}"

    class Meta:
        verbose_name = "Auftrag"
        verbose_name_plural = "Aufträge"
