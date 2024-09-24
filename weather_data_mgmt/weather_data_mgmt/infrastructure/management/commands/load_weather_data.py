import time
import os
from pathlib import Path
from datetime import datetime
import logging
import pandas as pd

from django.db import IntegrityError
from django.core.management.base import BaseCommand

from infrastructure.models import WeatherData
from infrastructure.constants import STATE_ID_MAP
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates weather table data from a fixture folder `wx_data` using txt files'

    def add_arguments(self, parser):
        parser.add_argument('--folderpath', required=True, type=str, help='Path to the wx_data folder')

    def handle(self, *args, **kwargs):
        folderpath = kwargs['folderpath']

        # Ensure the folder path exists
        if not os.path.isdir(folderpath):
            raise ValueError(f"The specified path '{folderpath}' is not a valid directory.")

        # Get all .txt files in the folder
        txt_files = list(Path(folderpath).glob('*.txt'))
        print(txt_files)
        start_time = time.time()
        for file in txt_files:
            try:
                # Extract codename from filename (first 7 characters)
                codename = file.stem[:7]

                print(f"Processing file: {file.name}")
                print(f"Codename: {codename}")
                state = STATE_ID_MAP[codename]
                station = file.stem[7:]
                df = pd.read_csv(f'{folderpath}/{file.name}', delimiter="\t", header=None)
                df.columns = ["date", "max_temp", "min_temp", "precp"]
                size = len(df)

                records_to_insert = []
                models_to_insert = []
                for idx in range(size):
                    row = df.iloc[idx]


                    if not WeatherData.objects.filter(
                            state=state,
                            station=station,
                            date=datetime.strptime(str(row['date']), "%Y%m%d").date()
                        ).exists():
                            records_to_insert.append(row)
                    weather_record = {
                            'state': state,
                            'station': station,
                            'year': str(row['date'])[:4],
                            'max_temp': row['max_temp'] / 10 if row['max_temp'] != '-9999' else None,
                            'min_temp': row['min_temp'] / 10 if row['min_temp'] != '-9999' else None,
                            'precipitation': row['precp'] / 10 if row['precp'] != '-9999' else None,
                            'date': datetime.strptime(str(row['date']), "%Y%m%d").date()
                        }
                    models_to_insert.append(WeatherData(**weather_record))

                inserted_models = WeatherData.objects.bulk_create(models_to_insert,ignore_conflicts=True)
                inserted_count = len(records_to_insert)
                ignored_count = len(inserted_models) - inserted_count
                print(f'inserted_count {inserted_count}')
                print(f'ignored_count {ignored_count}')
                print(f'Completed entry for {state}')
                print(f'######################################## {state}')


            except IOError as e:
                print(f"Error processing file {file.name}: {e}")
            except IntegrityError as e:
                logger.error('IntegrityError==>',e)
            except FileNotFoundError:
                logger.error('File not found. Please provide a valid CSV file path')
            except Exception as e:
                logger.exception('Something went wrong, check exception')
        end_time = time.time()  # End timer
        time_taken = end_time - start_time
        print(f"Time taken: {time_taken:.2f} seconds")
