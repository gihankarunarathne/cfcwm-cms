INSERT INTO curw.station (`id`, `stationId`, `name`, `latitude`, `longitude`, `resolution`)
VALUES
  (100020, 'curw_iBATTARA2', 'IBATTARA2', 6.89, 79.860002, 0),
  (100021, 'curw_iBATTARA3', 'IBATTARA3', 6.89, 79.860003, 0),
  (100022, 'curw_iBATTARA4', 'IBATTARA4', 6.89, 79.860004, 0),
  (100023, 'curw_isurupaya', 'Isurupaya', 6.89, 79.92, 0),
  (100024, 'curw_borella', 'Borella', 6.93, 79.86, 0),
  (100025, 'curw_kompannaveediya', 'Kompannaveediya', 6.92, 79.85, 0),
  (100026, 'curw_angurukaramulla', 'Angurukaramulla', 7.21, 79.86, 0),
  (100027, 'curw_hirimbure', 'Hirimbure', 6.054, 80.221, 0),
  (100028, 'curw_yatiwawala', 'Yatiwawala', 7.329, 80.613, 0);

# Database Migration
UPDATE curw.station SET id=100020, stationId='curw_iBATTARA2', name='IBATTARA2', latitude=6.89, longitude=79.862, resolution=0 WHERE id=20;
UPDATE curw.station SET id=100021, stationId='curw_iBATTARA3', name='IBATTARA3', latitude=6.89, longitude=79.863, resolution=0 WHERE id=21;
UPDATE curw.station SET id=100022, stationId='curw_iBATTARA4', name='IBATTARA4', latitude=6.89, longitude=79.864, resolution=0 WHERE id=22;
UPDATE curw.station SET id=100023, stationId='curw_isurupaya', name='Isurupaya', latitude=6.89, longitude=79.92, resolution=0 WHERE id=23;
UPDATE curw.station SET id=100024, stationId='curw_borella', name='Borella', latitude=6.93, longitude=79.86, resolution=0 WHERE id=24;
UPDATE curw.station SET id=100025, stationId='curw_kompannaveediya', name='Kompannaveediya', latitude=6.92, longitude=79.85, resolution=0 WHERE id=25;
UPDATE curw.station SET id=100026, stationId='curw_angurukaramulla', name='Angurukaramulla', latitude=7.21, longitude=79.86, resolution=0 WHERE id=26;
UPDATE curw.station SET id=100027, stationId='curw_hirimbure', name='Hirimbure', latitude=6.054, longitude=80.221, resolution=0 WHERE id=27;
UPDATE curw.station SET id=100028, stationId='curw_yatiwawala', name='Yatiwawala', latitude=7.329, longitude=80.613, resolution=0 WHERE id=28;