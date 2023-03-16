from django.db import models


# Create your models here.


class crowdinfo(models.Model):
    shoot_time = models.DateTimeField(auto_now=True, db_index=True)
    total_count = models.IntegerField()
    in_count = models.IntegerField()
    out_count = models.IntegerField()
    vis_count = models.IntegerField()

    def __str__(self):
        return str(self.shoot_time)

    @classmethod
    def get_data(cls):
        return cls.objects.all()


class warning(models.Model):
    warn_time = models.DateTimeField(auto_now=True)
    warn_type = models.CharField(max_length=50, null=True)
    warn_area = models.CharField(max_length=50, null=True)
    warn_description = models.CharField(max_length=50, null=True)
    camera_id = models.IntegerField(default=0, null=True)
    info = models.CharField(max_length=50, null=True)

    def __str__(self):
        return str(self.warn_time)

    @classmethod
    def get_data(cls):
        return cls.objects.all()


class soft_delete(models.Model):
    shoot_time = models.CharField(max_length=50, default='1970-01-01 00:00:00')
    total_count = models.IntegerField()
    in_count = models.IntegerField()
    out_count = models.IntegerField()
    vis_count = models.IntegerField()
    label = models.CharField(max_length=20, default='is deleted')

    @classmethod
    def get_data(cls):
        return cls.objects.all()


class tracking_object_table(models.Model):
    track_id = models.IntegerField()
    inshoot_time = models.DateTimeField(db_index=True, null=True)
    outshoot_time = models.DateTimeField(null=True)
    person_info = models.CharField(max_length=100, null=True)

    @classmethod
    def get_data(cls):
        return cls.objects.all()
