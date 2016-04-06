from __future__ import unicode_literals

from django.db import models


class Site(models.Model):
    id            = models.AutoField(primary_key=True)
    site_id       = models.CharField(max_length=20, unique=True)
    site_name     = models.CharField(max_length=50)
    river_basins  = models.CharField(max_length=50)
    river_name    = models.CharField(max_length=50)
    province      = models.CharField(max_length=50)
    safety_level  = models.FloatField(null=True)
    warning_level = models.FloatField(null=True)
    crawl_date    = models.IntegerField(null=True)
    deleted       = models.BooleanField(default=True)

    class Meta:
        db_table = "site"
        managed = False

    def __unicode__(self):
        return self.site_name


class WaterLevel(models.Model):
    id           = models.AutoField(primary_key=True)
    sid          = models.ForeignKey(Site, on_delete = models.CASCADE, db_column="sid")
    level        = models.FloatField()
    date         = models.IntegerField(unique=True)

    class Meta:
        db_table = "water_level"
        managed = False

    def __unicode__(self):
        return "[%s] [site_id=%s] [level=%s]" % (self.date, self.sid, self.level)

class WaterFlow(models.Model):
    id           = models.AutoField(primary_key=True)
    sid          = models.ForeignKey(Site, on_delete = models.CASCADE, db_column="sid")
    flow         = models.FloatField()
    date         = models.IntegerField(unique=True)

    class Meta:
        db_table = "water_flow"
        managed = False

    def __unicode__(self):
        return "%s %s flow=%s" % (self.sid, self.date, self.flow)

