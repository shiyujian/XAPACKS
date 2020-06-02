from django.urls import path
from . import views
urlpatterns = [
    # path('home/', views.home, name = 'home'),
    # path('uploadelevationPointfile/', views.uploadelevationPointfile, name = 'uploadelevationPointfile'),
    # path('elevationPoint/', views.elevationPoint, name = 'elevationPoint'),
    # path('elevationPointfile/', views.elevationPointfile, name = 'elevationPointfile'),
    # path('useOSCommand/', views.useOSCommand, name = 'useOSCommand'),
    # path('uploadData/', views.uploadData, name = 'uploadData'),
    # path('pointShapefile/', views.pointShapefile, name = 'pointShapefile'),
    path('earthVolume/', views.earthVolume, name = 'earthVolume'),
]