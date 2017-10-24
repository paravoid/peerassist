from __future__ import unicode_literals
from django.template import loader
from django_peeringdb.models import NetworkIXLan, IXLan, InternetExchange
from peercollect.models import Peering
from prettytable import PrettyTable
from peermatch.utils import find_peering_poc

# FIXME
from django.core.management.base import CommandError


def peering_matrix(us, them):
    table = PrettyTable([
        'IXP',
        'ASN L',
        us.name,
        'ASN R',
        them.name,
        'Established',
    ])

    common_ixl = IXLan.objects.all()
    common_ixl = common_ixl.filter(netixlan_set__net=us)
    common_ixl = common_ixl.filter(netixlan_set__net=them)
    common_ixl = common_ixl.distinct().order_by('ix__name')

    if len(common_ixl) == 0:
        raise CommandError('No common IXLans found')

    rows = 0

    for ixl in common_ixl:
        nixl_us = NetworkIXLan.objects.filter(ixlan=ixl, net=us)
        nixl_them = NetworkIXLan.objects.filter(ixlan=ixl, net=them)

        for i in nixl_us:
            for k in nixl_them:
                try:
                    Peering.objects.get(netixlan=k)
                    already_peered = 'yes'
                except Peering.DoesNotExist:
                    already_peered = 'no'

                if i.ipaddr4 is not None and k.ipaddr4 is not None:
                    table.add_row([
                        ixl.ix.name,
                        i.asn, i.ipaddr4,
                        k.asn, k.ipaddr4,
                        already_peered,
                    ])
                    rows += 1
                if i.ipaddr6 is not None and k.ipaddr6 is not None:
                    table.add_row([
                        ixl.ix.name,
                        i.asn, i.ipaddr6,
                        k.asn, k.ipaddr6,
                        already_peered,
                    ])
                    rows += 1

    if rows == 0:
        return None
    else:
        return table


def email(us, them):
    common_ixp = InternetExchange.objects.all()
    common_ixp = common_ixp.filter(ixlan_set__netixlan_set__net=us)
    common_ixp = common_ixp.filter(ixlan_set__netixlan_set__net=them)
    common_ixp = common_ixp.distinct().order_by('name')

    if len(common_ixp) == 0:
        raise CommandError('No common IXPs found')

    peerings = Peering.objects.filter(netixlan__net=them)

    existing_ixp = common_ixp.filter(
            ixlan_set__netixlan_set__peering__in=peerings)
    new_ixp = common_ixp.exclude(
            ixlan_set__netixlan_set__peering__in=peerings)

    if len(new_ixp) == 0:
        raise CommandError('No new IXPs found')

    recipients = find_peering_poc(them)
    if len(recipients) == 0:
        raise CommandError('No appropriate PoCs found')

    template = loader.get_template('peermatch/email.txt')
    context = {
        'peer': them,
        'recipients': ', '.join(recipients),
        'new_ixp': new_ixp,
        'existing_ixp': existing_ixp,
        'matrix': peering_matrix(us, them),
    }

    return template.render(context).lstrip().rstrip()
