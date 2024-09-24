from django.db import models

# Create your models here.

class AbstractModel(models.Model):
    creation = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class WeatherData(AbstractModel):
    state = models.CharField(max_length=50)
    station = models.CharField(max_length=50)
    year = models.CharField(max_length=4)
    date = models.DateField()
    max_temp = models.FloatField()
    min_temp = models.FloatField()
    precipitation = models.FloatField()

    class Meta:
        db_table = "weather_data"
        constraints = [models.UniqueConstraint(fields=['state', 'station', 'date'], name='datewise station weather constraint')]

class WeatherStatistics(AbstractModel):
    state = models.CharField(max_length=50)
    station = models.CharField(max_length=50)
    year = models.CharField(max_length=4)
    avg_max_temp = models.FloatField()
    avg_min_temp = models.FloatField()
    total_precipitation = models.FloatField()

    class Meta:
        db_table = "weather_stats"
        constraints = [models.UniqueConstraint(fields=['state', 'station', 'year'], name='yearwise stationwise statewise weather constraint')]
