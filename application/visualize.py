import geopandas
import matplotlib.pyplot as plt
from iso3166 import countries
import json
import argparse
import pandas as pd
import numpy as np
from matplotlib import pyplot


def plot_map_json(data, title):
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world['corr'] = [np.nan] * len(world.index)

    for key in data:
        alpha_3 = countries.get(key).alpha3
        world.loc[world.iso_a3 == alpha_3, 'corr'] = data[key]

        # Some countries code not supported in geopandas
        if alpha_3 == 'FRA':
            world.loc[world.name == 'France', 'corr'] = data[key]
        elif alpha_3 == 'NOR':
            world.loc[world.name == 'Norway', 'corr'] = data[key]

    world.plot('corr', legend="True")
    pyplot.title(title)


def plot_map_csv(data, column, ax=None):
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world[column] = [np.nan] * len(world.index)

    for _, row in data.iterrows():
        alpha_3 = countries.get(row['alpha_2']).alpha3
        world.loc[world.iso_a3 == alpha_3, column] = row[column]

        #Some countries code not supported in geopandas
        if alpha_3 == 'FRA':
            world.loc[world.name == 'France', column] = row[column]
        elif alpha_3 == 'NOR':
            world.loc[world.name == 'Norway', column] = row[column]

    if (ax):
        world.plot(column, ax=ax, legend="True")
        ax.title.set_text(column)
    else:
        world.plot(column, legend="True")
        pyplot.title(column)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--country", dest="country_code", default="POL")
    #parser.add_argument("--delta", dest="delta", default=0.1, type=float)
    #parser.add_argument("--correlation", dest="corr", default="trend_correlation")

    args = parser.parse_args()

    country_code = args.country_code
    #delta = args.delta
    #corr = args.corr

    with open('../analysis/correlations.json') as json_file:
        correlations = json.load(json_file)

    #fig, (ax1, ax2, ax3, ax4) = pyplot.subplots(nrows=4, sharex=True, sharey=True)
    plot_map_json(correlations[countries.get(country_code).alpha2]['twitter_smooth'], 'corr_twitter')
    plot_map_json(correlations[countries.get(country_code).alpha2]['who_conf_smooth'], 'corr_who_conf')
    plot_map_json(correlations[countries.get(country_code).alpha2]['who_rec_smooth'], 'corr_who_rec')
    plot_map_json(correlations[countries.get(country_code).alpha2]['who_deaths_smooth'], 'corr_who_deaths')

    data = pd.read_csv("../analysis/to_visualize.csv")

    plot_map_csv(data, 'corr_twt_conf', '')

    fig, (ax1, ax2, ax3) = pyplot.subplots(nrows=3, sharex=True, sharey=True)
    plot_map_csv(data, 'corr_twt_conf', ax1)
    plot_map_csv(data, 'corr_twt_deaths', ax2)
    plot_map_csv(data, 'corr_twt_rec', ax3)

    plt.show()
