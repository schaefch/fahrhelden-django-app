from .models import Job, Bringer, StaffUser, BaseUser
from django.contrib.admin import AdminSite
from django.contrib import admin


class StaffAdminSite(AdminSite):
    site_header = "Fahrhelden - Hotline Portal"
    site_title = "Fahrhelden - Hotline Portal"
    index_title = "Fahrhelden - Hotline Portal"


class BringerStaffAdmin(admin.ModelAdmin):
    fields = (
        "is_active",
        "is_confirmed",
        "email",
        "first_name",
        "last_name",
        "street",
        "house_nr",
        "zip_code",
        "location",
        "phone_number",
        "birth_date",
        "date_joined",
    )
    ordering = [
        "is_confirmed",
        "-date_joined",
    ]

    readonly_fields = (
        "email",
        "date_joined",
    )

    search_fields = [
        "email",
    ]


class JobStaffAdmin(admin.ModelAdmin):
    fields = (
        "first_name",
        "last_name",
        "street",
        "house_nr",
        "zip_code",
        "location",
        "phone_number",
        "buy_list",
        "amount",
        "status",
        "driver",
    )
    ordering = [
        "-status",
        "-placed_at",
    ]


staff_admin_site = StaffAdminSite(name="staff_admin")
staff_admin_site.register(Job, JobStaffAdmin)
staff_admin_site.register(Bringer, BringerStaffAdmin)


class RootAdminSite(AdminSite):
    site_header = "Fahrhelden - Admin Portal"
    site_title = "Fahrhelden - Admin Portal"
    index_title = "Fahrhelden - Admin Portal"


root_admin_site = RootAdminSite(name="root_admin")
root_admin_site.register(Job)
root_admin_site.register(BaseUser)
root_admin_site.register(Bringer)
root_admin_site.register(StaffUser)
