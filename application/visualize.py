import geopandas
import matplotlib.pyplot as plt
from iso3166 import countries
import json
import argparse
import pandas as pd
import numpy as np
from matplotlib import pyplot


def plot_map_json(data, title, ax=None, legend=True):
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
        world.plot('corr', ax=ax, legend=legend)
        ax.title.set_text(title)
    else:
        world.plot('corr', legend="True")
        pyplot.title(title)


def plot_map_csv(data, column, ax=None, title=None):
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world[column] = [np.nan] * len(world.index)

    for key, row in data.iterrows():
        alpha_3 = countries.get(key).alpha3
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


def process_series(data):
    strings = data.split('\n')
    x = []
    y = []
    for i in strings[:-1]:
        tmp = i.split()
        x.append(tmp[0])
        y.append(float(tmp[1]))

    res = pd.Series(y, index=x)
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--country", dest="country_code", default="POL")
    #parser.add_argument("--delta", dest="delta", default=0.1, type=float)
    #parser.add_argument("--correlation", dest="corr", default="trend_correlation")

    args = parser.parse_args()

    country_code = args.country_code
    #delta = args.delta
    #corr = args.corr

    with open('correlations-basic.json') as json_file:
        correlations_basic = json.load(json_file)

    with open('correlations.json') as json_file:
        correlations = json.load(json_file)

    #1
    fig1, a = pyplot.subplots(nrows=4, ncols=2)
    plot_map_json(correlations_basic[countries.get(country_code).alpha2]['twitter_smooth'], 'corr_twitter', a[0][1])
    #plot_map_json(correlations[countries.get(country_code).alpha2]['twitter_smooth'], 'corr_twitter_followers')
    plot_map_json(correlations[countries.get(country_code).alpha2]['who_conf_smooth'], 'corr_who_conf', a[1][1])
    plot_map_json(correlations[countries.get(country_code).alpha2]['who_rec_smooth'], 'corr_who_rec', a[2][1])
    plot_map_json(correlations[countries.get(country_code).alpha2]['who_deaths_smooth'], 'corr_who_deaths', a[3][1])

    data = pd.read_csv("to_visualize.csv", index_col=0)
    data_basic = pd.read_csv("to_visualize-basic.csv", index_col=0)

    series_list = ['twitter_raw', 'who_conf_smooth', 'who_rec_smooth', 'who_deaths_smooth']
    code = countries.get(country_code).alpha2
    country_summary = data_basic.loc[code]
    country_summary_foll = data.loc[code]

    for i, series in enumerate(series_list):
        a[i][0].plot(process_series(country_summary[series]))
        a[i][0].set_title(series)
        a[i][0].tick_params(axis='x', labelrotation=60)

    for i in range(3):
        a[i][0].set_xticklabels([])
        a[i][1].set_xticklabels([])

    fig1.suptitle('twitter_raw, who_conf, who_rec, who_death for %s' % code, fontsize=16)


    #2
    fig2, a = pyplot.subplots(nrows=2, ncols=2)
    plot_map_json(correlations_basic[countries.get(country_code).alpha2]['twitter_smooth'], 'corr_twitter', a[0][1])
    plot_map_json(correlations[countries.get(country_code).alpha2]['twitter_smooth'], 'corr_twitter_followers', a[1][1])
    #fig.tight_layout(pad=0)

    a[0][0].plot(process_series(country_summary['twitter_raw']))
    a[0][0].set_title('twitter_raw_basic')
    a[0][0].tick_params(axis='x', labelrotation=60)
    a[0][0].set_xticklabels([])

    a[1][0].plot(process_series(country_summary_foll['twitter_raw']))
    a[1][0].set_title('twitter_raw_followers')
    a[1][0].tick_params(axis='x', labelrotation=60)

    fig2.suptitle('twitter_raw_basic, twitter_raw_followers for %s' % code, fontsize=16)
    #print(country_summary['twitter_raw'])
    #plt.plot(process_series(country_summary['twitter_raw']))

    #3
    fig3, a = pyplot.subplots(nrows=3, ncols=2)
    plot_map_csv(data_basic, 'corr_twt_conf', a[0][0])
    plot_map_csv(data, 'corr_twt_conf', a[0][1], 'followers')

    plot_map_csv(data_basic, 'corr_twt_deaths', a[1][0])
    plot_map_csv(data, 'corr_twt_deaths', a[1][1], 'followers')

    plot_map_csv(data_basic, 'corr_twt_rec', a[2][0])
    plot_map_csv(data, 'corr_twt_rec', a[2][1], 'followers')

    fig3.suptitle('basic and followers corr_twt_conf, corr_twt_deaths, corr_twt_rec', fontsize=16)
    plt.show()
    #fig1.savefig('output/fig1.png')
    #fig2.savefig('output/fig2.png')
    #fig3.savefig('output/fig3.png')
