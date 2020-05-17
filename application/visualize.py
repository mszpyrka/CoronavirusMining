import geopandas
import matplotlib.pyplot as plt
from iso3166 import countries
import json
import argparse
import pandas as pd
import numpy as np
from matplotlib import pyplot


def plot_map_json(data, title, ax=None):
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

    if ax:
        world.plot('corr', ax=ax, legend="True")
        ax.title.set_text(title)
    else:
        world.plot('corr', legend="True")
        pyplot.title(title)


def plot_map_csv(data, column, ax=None, title=None):
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

    vis_title = column
    if title:
        vis_title = column + '_' + title

    if ax:
        world.plot(column, ax=ax, legend="True")
        ax.title.set_text(vis_title)
    else:
        world.plot(column, legend="True")
        pyplot.title(vis_title)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--country", dest="country_code", default="POL")
    #parser.add_argument("--delta", dest="delta", default=0.1, type=float)
    #parser.add_argument("--correlation", dest="corr", default="trend_correlation")

    args = parser.parse_args()

    country_code = args.country_code
    #delta = args.delta
    #corr = args.corr

    with open('../analysis/correlations-basic.json') as json_file:
        correlations_basic = json.load(json_file)

    with open('../analysis/correlations.json') as json_file:
        correlations = json.load(json_file)

    #fig, (ax1, ax2, ax3, ax4) = pyplot.subplots(nrows=4, sharex=True, sharey=True)
    fig, (ax1, ax2) = pyplot.subplots(nrows=2, sharex=True, sharey=True)
    plot_map_json(correlations_basic[countries.get(country_code).alpha2]['twitter_smooth'], 'corr_twitter', ax1)
    plot_map_json(correlations[countries.get(country_code).alpha2]['twitter_smooth'], 'corr_twitter_followers', ax2)
    plot_map_json(correlations[countries.get(country_code).alpha2]['who_conf_smooth'], 'corr_who_conf')
    plot_map_json(correlations[countries.get(country_code).alpha2]['who_rec_smooth'], 'corr_who_rec')
    plot_map_json(correlations[countries.get(country_code).alpha2]['who_deaths_smooth'], 'corr_who_deaths')

    data = pd.read_csv("../analysis/to_visualize.csv")
    data_basic = pd.read_csv("../analysis/to_visualize-basic.csv")

    fig, (ax1, ax2) = pyplot.subplots(nrows=2, sharex=True, sharey=True)
    plot_map_csv(data_basic, 'corr_twt_conf', ax1)
    plot_map_csv(data, 'corr_twt_conf', ax2, 'followers')

    fig, (ax1, ax2) = pyplot.subplots(nrows=2, sharex=True, sharey=True)
    plot_map_csv(data_basic, 'corr_twt_deaths', ax1)
    plot_map_csv(data, 'corr_twt_deaths', ax2, 'followers')

    fig, (ax1, ax2) = pyplot.subplots(nrows=2, sharex=True, sharey=True)
    plot_map_csv(data_basic, 'corr_twt_rec', ax1)
    plot_map_csv(data, 'corr_twt_rec', ax2, 'followers')

    plt.show()
