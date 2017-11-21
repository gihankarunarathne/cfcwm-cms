import copy
import logging
import os
import tempfile
from collections import OrderedDict
from datetime import datetime

import geopandas as gpd
from curw.rainfall.wrf.extraction.spatial_utils import get_voronoi_polygons
from curwmysqladapter import Data, Station

from cms_utils.UtilValidation import timeseries_availability
from observation.resource import ResourceManager
from observation.obs_virtual.ObsVirtualUtils import is_unique_points


def get_basin_shape(shape_file):
    shape_attribute = ['OBJECTID', 1]
    # tt = gpd.read_file(shape_file)['geometry'].area

    shape_df = gpd.GeoDataFrame.from_file(shape_file)
    shape_polygon_idx = shape_df.index[shape_df[shape_attribute[0]] == shape_attribute[1]][0]
    return shape_df['geometry'][shape_polygon_idx]


def create_kub_timeseries(adapter, stations, duration, opts):
    print("""
    *********************************************************
    *   Create KUB Data                                     *
    *********************************************************
    """)
    # Duration args destruction
    start_date_time = duration.get('start_date_time', None)
    end_date_time = duration.get('end_date_time', None)
    # Opts args destruction
    force_insert = opts.get('force_insert', False)

    variables = ['Precipitation']
    units = ['mm']
    metaData = {
        'station': 'Hanwella',
        'variable': 'Precipitation',
        'unit': 'mm',
        'type': 'Observed',
        'source': 'WeatherStation',
        'name': 'WUnderground',
    }

    for i in range(0, len(variables)):
        print('variable:', variables[i], ' unit:', units[i])
        meta = copy.deepcopy(metaData)
        meta['variable'] = variables[i]
        meta['unit'] = units[i]

        points = {}
        points_timeseries = {}

        # Get KUB basin shape file for checking weather station reside within it
        shp = ResourceManager.get_resource_path('shp/kelani-upper-basin/kelani-upper-basin.shp')
        shape_polygon = get_basin_shape(shp)

        for station in stations:
            print('\n**************** STATION **************')
            print('station:', station['name'])
            #  Check whether station exists
            is_station_exists = adapter.get_station({'name': station['name']})
            if is_station_exists is None:
                logging.warning('Station %s does not exists. Continue with others.', station['name'])
                continue

            # Check whether station reside within the basin
            # NOTE: No need to check weather inside the basin
            # if not Point(is_station_exists['longitude'], is_station_exists['latitude']).within(shape_polygon):
            #     logging.warning('Station %s does not contains inside KUB. Continue with others', station['name'])
            #     continue

            meta['station'] = station['name']
            if 'run_name' in station:
                meta['name'] = station['run_name']

            # -- Get Processed Timeseries for this station
            event_id = adapter.get_event_id(meta)
            if event_id is None:
                logging.warning('Event Id for %s does not exists. Continue with others', station['name'])
                continue
            logging.debug('%s : eventId is %s. Search with %s', station['name'], event_id, meta)

            opts = {
                'from': start_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'to': end_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'mode': Data.processed_data,
            }
            station_timeseries = adapter.retrieve_timeseries([event_id], opts)
            if len(station_timeseries) and len(station_timeseries[0]['timeseries']) > 0:
                station_timeseries = station_timeseries[0]['timeseries']
            else:
                print('INFO: Timeseries does not have any data on :', end_date_time.strftime("%Y-%m-%d"),
                      opts, station_timeseries)
                continue

            # -- Check whether timeseries worth to count in
            is_available = False
            if variables[i] in station['variables']:
                station_variable_index = station['variables'].index(variables[i])
                min_values = station['min_values']
                max_values = station['max_values']
                validationObj = {
                    'max_value': max_values[station_variable_index],
                    'min_value': min_values[station_variable_index],
                }
                is_available = timeseries_availability(station_timeseries, validationObj)

            # -- If a valid timeseries, store for further use
            if is_available:
                points[station['name']] = [is_station_exists['longitude'], is_station_exists['latitude']]
                points_timeseries[station['name']] = station_timeseries
        # -- END Getting data from stations

        if len(points) < 1:
            logging.warning("No station data found for given period of time. Abort...")
            print("No station data found for given period of time. Abort...")
            continue
        else:
            if is_unique_points(points):
                logging.info('Available stations %s', points)
                print('Available stations:', points)
            else:
                logging.warning("Available points should be unique. Abort...")
                print("Available points should be unique. Abort...")
                continue
        # -- Create thiessen polygon
        out = tempfile.mkdtemp(prefix='voronoi_')
        result = get_voronoi_polygons(points, shp, ['OBJECTID', 1], output_shape_file=os.path.join(out, 'out.shp'))
        print(result)
        thiessen_dict = {}
        total_area = 0.0
        for row in result.iterrows():
            if row[1][0] is not '__total_area__':
                thiessen_dict[row[1][0]] = row[1][3]
            elif row[1][0] is '__total_area__':
                total_area = row[1][3]

        if total_area is 0.0:
            logging.warning('Total Area can not be 0.0')
            return
        upper_thiessen_values = OrderedDict()
        for t_station_name in thiessen_dict.keys():
            thiessen_factor = thiessen_dict[t_station_name] / total_area
            for tt in points_timeseries.get(t_station_name, []):
                key = tt[0].timestamp()
                if key not in upper_thiessen_values:
                    upper_thiessen_values[key] = 0
                    upper_thiessen_values[key] += float(tt[1]) * thiessen_factor

        # Iterate through each timestamp
        kub_timeseries = []
        for avg in upper_thiessen_values:
            d = datetime.fromtimestamp(avg)
            kub_timeseries.append([d.strftime('%Y-%m-%d %H:%M:%S'), "%.3f" % upper_thiessen_values[avg]])

        # -- Create Station for KLB Obs
        is_kub_station = adapter.get_station({'name': 'KUB Obs'})
        if is_kub_station is None:
            kub_station = \
                (Station.CUrW, 'curw_kub_obs', 'KUB Obs', 7.111666667, 80.14983333, 0, "Kelani Upper Basin Observation")
            adapter.create_station(kub_station)

        # -- Store KLB Timeseries
        metaKUB = copy.deepcopy(metaData)
        metaKUB['station'] = 'KUB Obs'
        metaKUB['variable'] = variables[i]
        metaKUB['unit'] = units[i]
        metaKUB['name'] = 'KUB Obs Mean'
        klb_event_id = adapter.get_event_id(metaKUB)
        if klb_event_id is None:
            klb_event_id = adapter.create_event_id(metaKUB)
            print('HASH SHA256 created: ', klb_event_id)
        else:
            print('HASH SHA256 exists: ', klb_event_id)
            opts = {
                'from': start_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'to': end_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'mode': Data.processed_data,
            }
            existingTimeseries = adapter.retrieve_timeseries(metaKUB, opts)
            if len(existingTimeseries) and len(existingTimeseries[0]['timeseries']) > 0 and not force_insert:
                print('\n')
                continue

        rowCount = \
            adapter.insert_timeseries(klb_event_id, kub_timeseries, upsert=force_insert, mode=Data.processed_data)
        print('%s rows inserted.\n' % rowCount)


def create_klb_timeseries(adapter, stations, duration, opts):
    print("""
    *********************************************************
    *   Create KLB Data                                     *
    *********************************************************
    """)
    # Duration args destruction
    start_date_time = duration.get('start_date_time', None)
    end_date_time = duration.get('end_date_time', None)
    # Opts args destruction
    force_insert = opts.get('force_insert', False)

    variables = ['Precipitation']
    units = ['mm']
    metaData = {
        'station': 'Colombo',
        'variable': 'Precipitation',
        'unit': 'mm',
        'type': 'Observed',
        'source': 'WeatherStation',
        'name': 'WUnderground',
    }

    for i in range(0, len(variables)):
        print('variable:', variables[i], ' unit:', units[i])
        meta = copy.deepcopy(metaData)
        meta['variable'] = variables[i]
        meta['unit'] = units[i]

        points = {}
        points_timeseries = {}

        # Get KUB basin shape file for checking weather station reside within it
        shp = ResourceManager.get_resource_path('shp/klb-wgs84/klb-wgs84.shp')
        shape_polygon = get_basin_shape(shp)

        for station in stations:
            print('\n**************** STATION **************')
            print('station:', station['name'])
            #  Check whether station exists
            is_station_exists = adapter.get_station({'name': station['name']})
            if is_station_exists is None:
                logging.warning('Station %s does not exists. Continue with others', station['name'])
                continue

            # Check whether station reside within the basin
            # NOTE: No need to check weather inside the basin
            # if not Point(is_station_exists['longitude'], is_station_exists['latitude']).within(shape_polygon):
            #     logging.warning('Station %s does not contains inside KLB. Continue with others', station['name'])
            #     continue

            meta['station'] = station['name']
            if 'run_name' in station:
                meta['name'] = station['run_name']

            # -- Get Processed Timeseries for this station
            event_id = adapter.get_event_id(meta)
            if event_id is None:
                logging.warning('Event Id for %s does not exists. Continue with others', station['name'])
                continue
            print('%s : eventId is %s. Search with %s' % (station['name'], event_id, meta))

            opts = {
                'from': start_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'to': end_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'mode': Data.processed_data,
            }
            station_timeseries = adapter.retrieve_timeseries([event_id], opts)
            if len(station_timeseries) and len(station_timeseries[0]['timeseries']) > 0:
                station_timeseries = station_timeseries[0]['timeseries']
            else:
                print('INFO: Timeseries does not have any data on :', end_date_time.strftime("%Y-%m-%d"),
                      station_timeseries)
                continue

            # -- Check whether timeseries worth to count in
            is_available = False
            if variables[i] in station['variables']:
                station_variable_index = station['variables'].index(variables[i])
                min_values = station['min_values']
                max_values = station['max_values']
                validationObj = {
                    'max_value': max_values[station_variable_index],
                    'min_value': min_values[station_variable_index],
                }
                is_available = timeseries_availability(station_timeseries, validationObj)

            # -- If a valid timeseries, store for further use
            if is_available:
                points[station['name']] = [is_station_exists['longitude'], is_station_exists['latitude']]
                points_timeseries[station['name']] = station_timeseries
        # -- END Getting data from stations

        if len(points) < 1:
            logging.warning("No station data found for given period of time. Abort...")
            continue
        else:
            if is_unique_points(points):
                logging.info('Available stations %s', points)
                print('Available stations:', points)
            else:
                logging.warning("Available points should be unique. Abort...")
                print("Available points should be unique. Abort...")
                continue
        # -- Create thiessen polygon
        logging.debug("Create thiessen polygon using points: %s", points)
        out = tempfile.mkdtemp(prefix='voronoi_')
        result = get_voronoi_polygons(points, shp, ['OBJECTID', 1], output_shape_file=os.path.join(out, 'out.shp'))
        print(result)
        thiessen_dict = {}
        total_area = 0.0
        for row in result.iterrows():
            if row[1][0] is not '__total_area__':
                thiessen_dict[row[1][0]] = row[1][3]
            elif row[1][0] is '__total_area__':
                total_area = row[1][3]

        if total_area is 0.0:
            logging.warning('Total Area can not be 0.0')
            return
        lower_thiessen_values = OrderedDict()
        for t_station_name in thiessen_dict.keys():
            thiessen_factor = thiessen_dict[t_station_name] / total_area
            for tt in points_timeseries.get(t_station_name, []):
                key = tt[0].timestamp()
                # If key doesn't contain in the dictionary, create new key
                if key not in lower_thiessen_values:
                    lower_thiessen_values[key] = 0
                # Added to thiessen value at that timestamp
                lower_thiessen_values[key] += float(tt[1]) * thiessen_factor

        # Iterate through each timestamp
        klb_timeseries = []
        for avg in lower_thiessen_values:
            d = datetime.fromtimestamp(avg)
            klb_timeseries.append([d.strftime('%Y-%m-%d %H:%M:%S'), "%.3f" % lower_thiessen_values[avg]])

        # -- Create Station for KLB Obs
        is_klb_station = adapter.get_station({'name': 'KLB Obs'})
        if is_klb_station is None:
            klb_station = \
                (Station.CUrW, 'curw_klb_obs', 'KLB Obs', 7.111666667, 80.14983333, 0, "Kelani Lower Basin Observation")
            adapter.create_station(klb_station)

        # -- Store KLB Timeseries
        metaKLB = copy.deepcopy(metaData)
        metaKLB['station'] = 'KLB Obs'
        metaKLB['variable'] = variables[i]
        metaKLB['unit'] = units[i]
        metaKLB['name'] = 'KLB Obs Mean'
        klb_event_id = adapter.get_event_id(metaKLB)
        if klb_event_id is None:
            klb_event_id = adapter.create_event_id(metaKLB)
            print('HASH SHA256 created: ', klb_event_id)
        else:
            print('HASH SHA256 exists: ', klb_event_id)
            opts = {
                'from': start_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'to': end_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'mode': Data.processed_data,
            }
            existingTimeseries = adapter.retrieve_timeseries(metaKLB, opts)
            if len(existingTimeseries) and len(existingTimeseries[0]['timeseries']) > 0 and not force_insert:
                print('\n')
                continue

        rowCount = \
            adapter.insert_timeseries(klb_event_id, klb_timeseries, upsert=force_insert, mode=Data.processed_data)
        print('%s rows inserted.\n' % rowCount)
