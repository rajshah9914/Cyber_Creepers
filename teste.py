import geocoder
g = geocoder.ip('me')
print(g.latlng)
lat=g.latlng[0]
longi=g.latlng[1]