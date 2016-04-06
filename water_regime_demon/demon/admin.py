from django.contrib import admin

from .models import Site, WaterLevel, WaterFlow

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    pass

@admin.register(WaterLevel)
class WaterLevelAdmin(admin.ModelAdmin):
    pass

@admin.register(WaterFlow)
class WaterFlowAdmin(admin.ModelAdmin):
    pass
