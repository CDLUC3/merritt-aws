from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython import display as ipd
from IPython.display import display


def __read_costs(tsv_path: str = 'data/Merritt Costs 2018-05-08.txt'):
    __tsv_raw = pd.read_csv(tsv_path, sep='\t', na_filter=False, index_col=False)
    __usage_type_raw = __tsv_raw['usage_type']
    __description_raw = __tsv_raw['item_description']

    zone = __usage_type_raw.str.extract('^(US[A-Z][0-9])', expand=False)
    aws_service = __usage_type_raw.str.extract('-([A-Za-z]+)', expand=False)
    usage_type = __usage_type_raw.str.extract('-[A-Za-z]+[-:](.+)', expand=False).fillna('Other')

    server = __tsv_raw['name'].str.extract('^(uc3-[a-z0-9-]+)', expand=False).fillna('')
    env = server.str.extract('uc3-[a-z0-9]+-([a-z]+)', expand=False).fillna('')
    service = server.str.extract('-(?:mrt)?([a-z]+)', expand=False).fillna('other')
    device = __tsv_raw['name'].str.extract('(swap|(?:/dev/[a-z]+))', expand=False).fillna('')

    unit_cost = __description_raw.str.extract('\\$([0-9.]+)', expand=False).astype(float)
    unit = __description_raw.str.lower().str.extract(
        '(gb-month|instance hour|gb.*transfer|million i/o requests|load[^(]*hour)', expand=False).fillna('')
    cost = __tsv_raw['unblended_cost']
    quantity = cost / unit_cost

    df = pd.DataFrame(
        data=OrderedDict([
            ("service", service),
            ("env", env),
            ("server", server),
            ("aws_service", aws_service),
            ("device", device),
            ("usage_type", usage_type),
            ("cost", cost),
            ("quantity", quantity),
            ("unit", unit),
            ("unit_cost", unit_cost),
            ("zone", zone),
        ])
    )

    index_cols = ['service', 'env', 'server', 'device', 'aws_service', 'usage_type']
    return df.sort_values(by=index_cols)  # .set_index(index_cols)


costs = __read_costs()

services = np.unique(costs['service'])
envs = np.unique(costs['env'])
aws_services = np.unique(costs['aws_service'])


def display_md(md_str: str):
    display(ipd.Markdown(md_str))


def display_summary(service):
    display_md('### Service: %s' % service)

    s_costs = costs_for_service(service)
    s_total_cost = total_cost(s_costs)
    display_md('###### Total cost: $%s' % s_total_cost)

    plot_costs_by_usage(s_costs)
    plt.show()

    for env in envs:
        se_costs = costs_for_service_and_env(service, env)
        if se_costs.empty:
            continue
        se_total_cost = total_cost(se_costs)
        if not service == '':
            display_md('#### %s %s' % (service, env))
            display_md('###### Total cost for %s %s: $%s' % (service, env, se_total_cost))
        for server in servers_for(service, env):
            ses_costs = costs_for_server(server)
            ses_total_cost = total_cost(ses_costs)
            if not server == '':
                display_md('##### %s' % server)
                display_md('###### Total cost for %s: $%s' % (server, ses_total_cost))
            ses_summary = summary_table_for(ses_costs)
            display(ses_summary)
    display_md('---')


def plot_costs_by_usage(df: pd.DataFrame):
    usage_costs = df.groupby(['usage_type'])['cost'].sum().to_frame()
    usage_costs.sort_values('cost', inplace=True)
    usage_costs.rename(index=str, columns={'usage_type': 'Usage Type', 'cost': 'Cost ($)'})
    plot = usage_costs.plot.barh(
        logy=False,
        width=1.0,
        facecolor='#1295d8',
        edgecolor='#005581',
        figsize=(7.5, 7.5)
    )
    return plot


def plot_costs_by_service(df: pd.DataFrame):
    service_costs = df.groupby(['service'])['cost'].sum().to_frame()
    service_costs.sort_values('cost', inplace=True)
    service_costs.rename(index=str, columns={'service': 'Service', 'cost': 'Cost ($)'})
    plot = service_costs.plot.barh(
        logy=False,
        width=1.0,
        facecolor='#1295d8',
        edgecolor='#005581',
        figsize=(7.5, 7.5)
    )
    return plot


def summary_table_for(df: pd.DataFrame):
    sum = pd.DataFrame(data={'aws_service': df['aws_service']})
    sum['device'] = df['device']
    sum['usage_type'] = df['usage_type']
    sum['cost'] = df['cost'].map(lambda x: "$%s" % np.round(x, 2))
    sum['basis'] = df.apply(
        (lambda row: "%s %s at $%s ea." % (np.round(row['quantity'], 2), row['unit'], np.round(row['unit_cost'], 2))),
        axis=1
    )
    return sum.reindex()  # TODO: fix this


def total_cost(df: pd.DataFrame):
    return np.round(df['cost'].sum(), 2)


def costs_for_service(service):
    return costs.loc[costs['service'] == service]


def costs_for_service_and_env(service, env):
    s_costs = costs_for_service(service)
    return s_costs.loc[s_costs['env'] == env]


def servers_for(service, env):
    se_costs = costs_for_service_and_env(service, env)
    return np.unique(se_costs['server'])


def costs_for_server(server):
    return costs[costs['server'] == server]


def costs_for_server_and_aws_service(server, aws_service):
    s_costs = costs_for_server(server)
    return s_costs.loc[s_costs['aws_service'] == aws_service]

# TODO: roll up costs by sevice/server/env/device/usage_type and display
# TODO:   1. the whole list in a pretty way
# TODO:   2. summary charts for each


# for service in services:
#     s_costs = costs_for_service(service)
#     s_total_cost = total_cost(s_costs)
#     for env in envs:
#         se_costs = costs_for_service_and_env(service, env)
#         se_total_cost = total_cost(se_costs)
#         for server in servers_for(service, env):
#             ses_costs = costs_for_server(server)
#             ses_total_cost = total_cost(ses_costs)
#             display(ses_costs)
