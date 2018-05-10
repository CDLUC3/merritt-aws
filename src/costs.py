from collections import OrderedDict

import numpy as np
import pandas as pd


def __read_costs(tsv_path: str = 'data/Merritt Costs 2018-05-08.txt'):
    __tsv_raw = pd.read_csv(tsv_path, sep='\t', na_filter=False, index_col=False)
    __usage_type_raw = __tsv_raw['usage_type']
    __description_raw = __tsv_raw['item_description']

    zone = __usage_type_raw.str.extract('^(US[A-Z][0-9])', expand=False)
    aws_service = __usage_type_raw.str.extract('-([A-Za-z]+)', expand=False)
    usage_type = __usage_type_raw.str.extract('-[A-Za-z]+[-:](.+)', expand=False).fillna('')

    server = __tsv_raw['name'].str.extract('^(uc3-[a-z0-9-]+)', expand=False).fillna('')
    env = server.str.extract('uc3-[a-z0-9]+-([a-z]+)', expand=False).fillna('')
    service = server.str.extract('-(?:mrt)?([a-z]+)', expand=False).fillna('')
    device = __tsv_raw['name'].str.extract('(swap|(?:/dev/[a-z]+))', expand=False).fillna('')

    unit_cost = __description_raw.str.extract('\\$([0-9.]+)', expand=False).astype(float)
    unit = __description_raw.str.lower().str.extract(
        '(gb-month|instance hour|gb.*transfer|million i/o requests|load[^(]*hour)', expand=False).fillna('')
    cost = __tsv_raw['unblended_cost']
    quantity = cost / unit_cost

    df = pd.DataFrame(
        data=OrderedDict([
            ("env", env),
            ("service", service),
            ("server", server),
            ("device", device),
            ("zone", zone),
            ("aws_service", aws_service),
            ("usage_type", usage_type),
            ("unit_cost", unit_cost),
            ("unit", unit),
            ("quantity", quantity),
            ("cost", cost),
        ])
    )

    return df.sort_values(by=['env', 'service', 'server', 'device'])


costs = __read_costs()
environments = np.unique(costs['env'])
services = np.unique(costs['service'])
costs_by_environment = {env: costs.loc[costs['env'] == env] for env in environments}
costs_by_service = {service: costs.loc[costs['service'] == service] for service in services}

costs_by_env_and_service = {}
for env in environments:
    env_costs = costs_by_environment[env]
    env_costs_by_service = {}
    for service in services:
        env_costs_by_service[service] = env_costs.loc[env_costs['service'] == service]
    costs_by_env_and_service[env] = env_costs_by_service
