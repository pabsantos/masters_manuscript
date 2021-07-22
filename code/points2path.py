import pandas as pd

coord = pd.read_csv('output/validtime_speeding.csv', dtype = {'id': str, 'time_acum': int, 'lat': float, 'long': float})

coord2 = coord[['id', 'long', 'lat', 'time_acum', 'date', 'time', 'spd_kmh', 'limite_vel', 'rel_spd']]

coord2['WKT'] = None

for i in range(1, len(coord2)):
    if (coord2['time_acum'][i] - coord2['time_acum'][i-1]) == 1:
        coord2['WKT'][i] = 'LINESTRING (' + str(coord2['long'][i]) + ' ' + str(coord2['lat'][i]) + ',' + str(coord2['long'][i-1]) + ' ' + str(coord2['lat'][i-1]) + ')' 
        coord2['rel_spd'][i] = (coord2['rel_spd'][i] + coord2['rel_spd'][i-1])/2
    else:
        coord2['WKT'][i] = 0
    print(str(i) + '/' + str(coord2.shape[0]))
    
linhas = coord2.query('WKT != 0')

print(linhas.head())

linhas.to_csv('output/validtime_speeding_line.csv', sep = ';', columns = ['WKT', 'id', 'long', 'lat', 'time_acum', 'date', 'time', 'spd_kmh', 'limite_vel', 'rel_spd'])