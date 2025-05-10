-- SQLite
SELECT id, groupname, the_level, the_type, 
        the_value, the_date, aobs, json_extract(e_extra_info,'$.name')
FROM eattributes
WHERE the_type = 'geoentity:name@wikidata'
        AND groupname = 'geo1'
ORDER BY the_value, the_date
LIMIT 100   ;
