from django.conf import settings
from django.shortcuts import render
from django.db.models import F

import django_tables2 as tables
import django_filters as filters
from django_filters.views import FilterView

from django_peeringdb.models import Network, IXLan, InternetExchange
from itertools import groupby


class NetworkSummaryTable(tables.Table):
    class Meta:
        model = Network
        fields = (
            "asn",
            "name",
            "info_traffic",
            "info_scope",
            "policy_general",
        )


class NetworkFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="contains")
    present_in = filters.ModelMultipleChoiceFilter(
        label="Present in",
        field_name="netixlan_set__ixlan__ix",
        queryset=InternetExchange.objects.filter(
            ixlan_set__netixlan_set__net__asn=settings.OUR_ASN
        ).order_by("name"),
    )

    class Meta:
        model = Network
        fields = (
            "asn",
            "name",
            "info_traffic",
            "info_scope",
            "policy_general",
        )


class FilteredNetworkList(tables.SingleTableMixin, FilterView):
    model = Network
    ordering = ["asn"]
    table_class = NetworkSummaryTable
    filterset_class = NetworkFilter
    template_name = "prospects.html"


def home(request):
    us = Network.objects.get(asn=settings.OUR_ASN)

    our_lans = IXLan.objects.filter(netixlan_set__net=us)

    our_ix = InternetExchange.objects.filter(ixlan_set__in=our_lans)
    our_ix = our_ix.order_by("name")

    common_nets = Network.objects.all()
    common_nets = common_nets.filter(netixlan_set__ixlan__in=our_lans)
    common_nets = common_nets.annotate(ix=F("netixlan_set__ixlan__ix"))
    common_nets = common_nets.annotate(
        peering=F("netixlan_set__peering__netixlan__ixlan__ix")
    )
    common_nets = common_nets.distinct()
    common_nets = common_nets.order_by("policy_general", "asn")

    values = common_nets.values(
        "name", "asn", "policy_general", "info_traffic", "ix", "peering",
    )

    nets = []
    for k, g in groupby(values, key=lambda n: n["asn"]):
        groups = list(g)

        # be DRY and copy all the keys from values
        net = groups[0]

        # override ix/peering with a list of all of their values
        for combined in ("ix", "peering"):
            net[combined] = [i[combined] for i in groups if i[combined] is not None]

        # if we already have peerings established on all the potential IXPs
        # with this peer, skip it; should this be made configuratble?
        if set(net["ix"]) == set(net["peering"]):
            continue

        # if we have no peerings at all with this peer, skip it
        # (this belongs in a separate view, most probably)
        # FIXME
        # if len(net['peering']) == 0:
        #    continue

        nets.append(net)

    context = {
        "us": us,
        "ixps": our_ix,
        "nets": nets,
    }

    return render(request, "home.html", context)
