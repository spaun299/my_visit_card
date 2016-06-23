## This is a simple python script that allow you to  download gz file from url,  and then unzip this file to your destination

#### Example:
>__python run.py -schedule="n" -url="http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz" -destination="/path/to/folder/file/name"__
or just
__python run.py__
If you don't pass any parameters to script, default parameters will be:
schedule="y"
url="http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz"
destination="geo_lite.mmdb"
