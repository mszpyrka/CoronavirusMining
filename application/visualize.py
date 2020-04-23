import geopandas
import matplotlib.pyplot as plt
from descartes import PolygonPatch
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        country = sys.argv[1]

    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    ax = world.boundary.plot()

    try:
        nami = world[world.name == country]
        namigm = nami.__geo_interface__['features']  # geopandas's geo_interface
        namig0 = {'type': namigm[0]['geometry']['type'], 'coordinates': namigm[0]['geometry']['coordinates']}
        ax.add_patch(PolygonPatch(namig0, fc='red', ec="black", alpha=0.85, zorder=2))

        plt.show()
    except Exception:
        print("You entered wrong country :(")
