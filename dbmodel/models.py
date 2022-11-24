from django.db import models

# Create your models here.


class crowdinfo(models.Model):
    shoot_time = models.DateTimeField(auto_now=True)
    total_count = models.IntegerField()
    in_count = models.IntegerField()
    out_count = models.IntegerField()
    vis_count = models.IntegerField()

    def __str__(self):
        return str(self.shoot_time)


class warning(models.Model):
    warn_type = models.CharField(max_length=100)
    camera_id = models.IntegerField()
    warn_time = models.DateTimeField(auto_now_add=True)
    info = models.CharField(max_length=500, null=True)

    def __str__(self):
        return str(self.warn_time)

