
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# this Model hold my Personal information, Skills etc.
class AboutMe(models.Model):
    bio = models.TextField(_("Bio"), blank=True, null=True)
    profile_img = models.ImageField(_("Profile Image"), upload_to="profile_images/", blank=True, null=True)
    background_img = models.ImageField(_("Background Image"), upload_to="background_images/", blank=True, null=True)
    resume = models.FileField(_("Resume"), upload_to="Resume/", blank=True, null=True)
    
    skills = models.TextField(_("Skills"), blank=True, null=True)

    def __str__(self):
        return self.bio[:18] if self.bio else "No bio provided"

# this Model hold my Competitive programming information,activity etc.
class CP_Log(models.Model):
    title = models.CharField(_("Title"), blank=True, null=True, max_length=50)
    url = models.URLField(_("Url"), blank=True, null=True, max_length=200)
    activity_img = models.ImageField(_("Activity_img"), upload_to="Activity_img/", blank=True, null=True)
    details = models.TextField(_("Details"), blank=True, null=True,max_length = 400)
    
    def __str__(self):
        return self.title if self.title else _("No Title")
    
# This model hold my projects 

class Projects(models.Model):
    title = models.CharField(_("Title"),blank = True,null = True, max_length = 50)
    url = models.URLField(_("Url"), blank=True, null=True, max_length=200)
    project_img = models.ImageField(_("Project_img"), upload_to="Project_img/", blank=True, null=True)
    details = models.TextField(_("Details"), blank=True, null=True,max_length = 600)
    
    def __str__(self):
        return self.title if self.title else _("No Projects.")
    
    
# This model hold my Experince in tech-field

class Experience(models.Model):
    experience_title = models.CharField(_("Experience Title"),blank = True,null = True, max_length = 50)
    experience_img = models.ImageField(_("Experience_img"), upload_to="Experience_img/", blank=True, null=True)
    experience_details = models.TextField(_("Experience_Details"), blank=True, null=True,max_length = 600)
    
    def __str__(self):
        return self.experience_title if self.experience_title else _("No Experience.")
    


# This model hold my All Certifications

class Certifications(models.Model):
    certificate_title = models.CharField(_("Certificate_Title"),blank = True,null = True, max_length = 50)
    certificate_img = models.ImageField(_(" Certificate_img"), upload_to=" Certificate_img/", blank=True, null=True)
    certificate_details = models.TextField(_("Details"), blank=True, null=True,max_length = 600)
    
    def __str__(self):
        return self.certificate_title if self.certificate_title else _("No Certifications.")


# This model hold my All Hobbies  
class Hobbies(models.Model):
    # for Books 
    book_name = models.CharField(_("Book name"), blank=True, null=True, max_length=50)
    book_img = models.ImageField(_("book_img"), upload_to="book_img/", blank=True, null=True)
    writer_name = models.CharField(_("writer name"), blank=True, null=True, max_length=100)

    # for others hobbies
    movie_name = models.CharField(_("Movie Name"), blank=True, null=True, max_length=100)

    def __str__(self):
        if self.book_name:
            return f"Book: {self.book_name.title()}"
        elif self.movie_name:
            return f"Movie: {self.movie_name.title()}"
        return _("No Hobbies")
    
class ConnectMe(models.Model):
    name = models.CharField(_("Name"),blank = True,null = True, max_length = 50)
    email = models.EmailField(_("Email"),blank = True,null = True, max_length = 60)
    comment = models.TextField(_("Comment"), blank=True, null=True,max_length = 600)
    def __str__(self):
        return self.name
    
