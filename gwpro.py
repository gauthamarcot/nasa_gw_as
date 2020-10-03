from astropy.coordinates import EarthLocation
from astropy.time import Time
from ligo.skymap.coordinates import DetectorFrame
from ligo.skymap.io import read_sky_map
import ligo.skymap.plot
from matplotlib import pyplot as plt

# Download GW150914 localization
url = 'https://dcc.ligo.org/public/0122/P1500227/012/bayestar_gstlal_C01.fits.gz'
m, meta = ligo.skymap.io.read_sky_map(url)

# Plot sky map on an orthographic projection
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(
    111, projection='astro globe', center='130d -70d')
ax.imshow_hpx(m, cmap='cylon')

# Hide the original ('RA', 'Dec') ticks
for coord in ax.coords:
    coord.set_ticks_visible(False)
    coord.set_ticklabel_visible(False)

# Construct Hanford-Livingston detector frame at the time of the event
frame = DetectorFrame(site_1=EarthLocation.of_site('H1'),
                      site_2=EarthLocation.of_site('L1'),
                      obstime=Time(meta['gps_time'], format='gps'))

# Draw grid for detector frame
ax.get_coords_overlay(frame).grid()
