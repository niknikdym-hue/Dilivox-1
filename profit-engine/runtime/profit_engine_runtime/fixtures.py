from __future__ import annotations


FIXTURE_CAPTURED_AT = "2026-08-27T12:00:00+00:00"

DIRECT = {
    "campaigns": {"result": {"Campaigns": [
        {"Id": "fixture-campaign-a", "Name": "Fixture campaign", "State": "ON", "Status": "ACCEPTED"}
    ]}},
    "report_status": 200,
    "report_tsv": "Date\tCampaignId\tImpressions\tClicks\tCost\n2026-08-26\tfixture-campaign-a\t100\t7\t12.340000\n",
    "report_attempts": 1,
    "money_basis": {"currency": "RUB", "include_vat": True, "include_discount": True, "money_in_micros": False}
}

METRICA = {
    "query": {"metrics": ["ym:s:visits", "ym:s:yanPartnerPrice", "ym:s:yanRequests", "ym:s:yanRenders", "ym:s:yanShows"]},
    "data": [{"dimensions": [{"name": "2026-08-26"}], "metrics": [31, "18.250000", 80, 70, 61]}],
    "currency": "RUB", "sampled": False, "sample_size": 31, "sample_space": 31,
    "data_lag": 0, "contains_sensitive_data": False
}

YAN = {
    "tree": {"fields": [
        {"name": "shows", "semantic": "delivery"},
        {"name": "hits_render", "semantic": "delivery"},
        {"name": "hits", "semantic": "delivery"},
        {"name": "fixture_revenue", "semantic": "revenue"}
    ]},
    "selected_revenue_field": "fixture_revenue",
    "report": {"data": {"points": [
        {"date": "2026-08-26", "shows": 61, "hits_render": 70, "hits": 80, "fixture_revenue": "18.250000"}
    ]}},
    "currency": "RUB", "timezone": "Europe/Moscow", "vat_basis": "fixture-explicit"
}
