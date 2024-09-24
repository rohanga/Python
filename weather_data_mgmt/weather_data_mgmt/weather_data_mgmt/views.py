import logging

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Avg, Sum, Q

from infrastructure.models import WeatherData, WeatherStatistics

logger = logging.getLogger(__name__)

class WeatherStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherStatistics
        fields = '__all__'

class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = '__all__'


class WeatherStatsAPIView(ViewSet):
    @swagger_auto_schema(
            manual_parameters=[
            openapi.Parameter(
                'station_id', openapi.IN_QUERY, description="Filter by station id",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'year', openapi.IN_QUERY, description="Filter by year",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'state', openapi.IN_QUERY, description="Filter by state",
                type=openapi.TYPE_STRING
            )
        ]
    )
    @action(methods=['GET'], detail=False, url_path=r"stats")
    def get_stats(self, request):
        try:
            station = request.query_params.get('station', None)
            year = request.query_params.get('year', None)
            state = request.query_params.get('state', None)

            filters = Q()
            if station:
                filters &= Q(station=station)
            if year:
                filters &= Q(year=year)
            if state:
                filters &= Q(state=state)

            # Build the query based on the provided parameters
            weather_stats = (
                WeatherStatistics.objects
                .filter(filters)
            )
            serializer = WeatherStatisticsSerializer(weather_stats, many=True)
            return Response({'data': serializer.data, 'count': len(weather_stats)}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)


    @swagger_auto_schema()
    @action(methods=['post'], detail=False, url_path=r"calculatestats")
    def calculate_stats(self, request):
        try:
            # Build the query based on the provided parameters
            weather_stats = (
                    WeatherData.objects
                    .values('year', 'station', 'state')
                    .annotate(
                        average_max_temp=Avg('max_temp'),
                        average_min_temp=Avg('min_temp'),
                        total_precipitation=Sum('precipitation')
                    )  # This limits the overall result set, adjust as necessary
                )

            models_to_insert = []
            for stat in weather_stats:
                weather_stat_record = {
                    'year': stat['year'],
                    'state': stat['state'],
                    'station': stat['station'],
                    'avg_max_temp': "{:.2f}".format(stat['average_max_temp']),
                    'avg_min_temp': "{:.2f}".format(stat['average_min_temp']),
                    'total_precipitation': "{:.2f}".format(stat['total_precipitation'])
                    }
                models_to_insert.append(WeatherStatistics(**weather_stat_record))
            inserted_models = WeatherStatistics.objects.bulk_create(models_to_insert,ignore_conflicts=True)
            serializer = WeatherStatisticsSerializer(inserted_models, many=True)
            return Response({'data': serializer.data, 'count': len(inserted_models)}, status=status.HTTP_200_OK)
        except Exception as err:
            logger.error('Exception occured', err)

    @swagger_auto_schema(
            manual_parameters=[
            openapi.Parameter(
                'start', openapi.IN_QUERY, description="Start",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'end', openapi.IN_QUERY, description="End",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'station_id', openapi.IN_QUERY, description="Station id",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'state', openapi.IN_QUERY, description="state",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'date', openapi.IN_QUERY, description="yyyy-mm-dd",
                type=openapi.TYPE_STRING
            ),

        ]
    )
    @action(methods=['GET'], detail=False, url_path=r"weatherdata")
    def get_weather_data(self, request):
        try:
            start = int(request.query_params.get('start', 1)) - 1  # Convert to 0-based index
            end = int(request.query_params.get('end', 1))

            station_id = request.query_params.get('station_id')  # Convert to 0-based index
            date = request.query_params.get('date')
            state = request.query_params.get('state')

            filters = {}
            if station_id:
                filters['station'] = station_id
            if date:
                filters['date'] = date
            if state:
                filters['state'] = state

            # Fetch filtered records and apply slicing based on start and end
            weather_data = WeatherData.objects.filter(**filters)[start:end]

            # Serialize the result
            serializer = WeatherDataSerializer(weather_data, many=True)
            return Response({'data': serializer.data, 'count': len(weather_data)}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
