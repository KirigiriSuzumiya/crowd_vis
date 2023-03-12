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


class crowdinfo_concordance(models.Model):
    time = models.CharField(max_length=50, default='null')
    avg_count = models.IntegerField()
    max_count = models.IntegerField()
    min_count = models.IntegerField()

    @classmethod
    def get_data(cls):
        return cls.objects.all()
# 上面张表不需要直接写入数据,是我将crowdinfo表里的数据按时间段进行整合后写入,并删除crowdinfo该时间段里的数据,优化crowdinfo数据库节省空间
