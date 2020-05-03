import geopandas
import matplotlib.pyplot as plt
from descartes import PolygonPatch
import sys
from iso3166 import countries
import json
import argparse


def plot_country(country_code, primary=False):
    try:
        # France, Norway hardcoded
        if country_code == 'FRA':
            nami = world[world.name == 'France']
        elif country_code == 'NOR':
            nami = world[world.name == 'Norway']
        else:
            nami = world[world.iso_a3 == country_code]

        namigm = nami.__geo_interface__['features']  # geopandas's geo_interface
        namig0 = {'type': namigm[0]['geometry']['type'], 'coordinates': namigm[0]['geometry']['coordinates']}
        color = 'red' if primary else 'orange'
        ax.add_patch(PolygonPatch(namig0, fc=color, ec="black", alpha=0.85, zorder=2))

    except Exception:
        print("Country not supported: %s" % country_code)
        print(countries.get(country_code))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--country", dest="country_code", default="POL")
    parser.add_argument("--delta", dest="delta", default=0.1, type=float)
    parser.add_argument("--correlation", dest="corr", default="trend_correlation")

    args = parser.parse_args()

    country_code = args.country_code
    delta = args.delta
    corr = args.corr

    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    ax = world.boundary.plot()

    plot_country(country_code, True)

    with open('../analysis/correlations.json') as json_file:
        correlations = json.load(json_file)
    try:
        base_correlation = correlations[countries.get(country_code).alpha2][corr]

        for key_code in correlations:
            if abs(correlations[key_code][corr] - base_correlation) <= delta and key_code != countries.get(country_code).alpha2:
                plot_country(countries.get(key_code).alpha3)

        plt.show()
    except KeyError:
        print("Entered country code is invalid: %s" % country_code)
