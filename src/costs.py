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
            ("cost", cost),
            ("quantity", quantity),
            ("unit", unit),
            ("unit_cost", unit_cost),
            ("aws_service", aws_service),
            ("usage_type", usage_type),
            ("zone", zone),
        ])
    )

    index_cols = ['service', 'env', 'server', 'device']
    return df.sort_values(by=index_cols).set_index(index_cols)


costs = __read_costs()

# supertotal = 0
# for service in services:
#     display(Markdown("---\n# Service: %s" % service))
#     svc_total = 0
#     for env in environments:
#         env_svc_costs = costs_by_env_and_service[env][service]
#         if not env_svc_costs.empty:
#             display(Markdown("## Environment: %s" % env))
#             display(env_svc_costs)
#             total = env_svc_costs['cost'].sum()
#             display(Markdown("### Total: $%s" % np.round(total, 2)))
#             svc_total = svc_total + total
#     display(Markdown("## Total: $%s" % np.round(svc_total, 2)))
#     supertotal = supertotal + svc_total
#
# display(Markdown("# Total: $%s" % np.round(supertotal, 2)))

# class Costs:
#
#
#
#     def __init__(self, costs: pd.DataFrame):
#         self.costs = costs
#         self.environments = np.unique(costs['env'])
#         self.services = np.unique(costs['service'])
#
#         costs_by_env_and_service = {}
#         for env in self.environments:
#             env_costs_by_service = {}
#             for service in self.services:
#                 env_costs_by_service[service] = costs.loc[
#                     costs['env'] == env
#                     & costs['service'] == service
#                 ]
#             costs_by_env_and_service[env] = env_costs_by_service
#
#         self.costs_by_env_and_service = costs_by_env_and_service
