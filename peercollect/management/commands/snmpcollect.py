from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from django.utils.six import iteritems
from snimpy.manager import Manager as M
from snimpy.manager import load
from snimpy.snmp import SNMPException
from django_peeringdb.models.concrete import NetworkIXLan
from peercollect.models import Peering


class Command(BaseCommand):
    help = "populate peering database from SNMP"

    def add_arguments(self, parser):
        parser.add_argument('-n', '--dry-run',
                action='store_true',
                default=False,
                help='dry run')

    def handle(self, *args, **options):
        # only BGP4-MIB for now, there were snimpy troubles with Juniper's BGP
        # v2 MIB:
        # http://puck.nether.net/pipermail/juniper-nsp/2017-March/034067.html
        #
        # This effectively means only IPv4 matches, which is probably okay for
        # this use case (and probably this decade).
        load("BGP4-MIB")

        for router, community in iteritems(settings.SNMP_ROUTERS):
            m = M(host=router, community=community, version=2)

            netixlans = []
            notmatched = 0

            try:
                peers = m.bgpPeerRemoteAs
                for ip, asn in iteritems(peers):
                    try:
                        netixlan = NetworkIXLan.objects.get(ipaddr4=ip, asn=asn)
                        netixlans.append(netixlan)
                    except NetworkIXLan.DoesNotExist:
                        notmatched += 1
            except SNMPException as e:
                raise CommandError(e)

            with transaction.atomic():
                # flush all peerings for this router
                Peering.objects.filter(router=router).delete()

                # ...and recreate them
                for netixlan in netixlans:
                    p = Peering(netixlan=netixlan, router=router)
                    p.save()

            print("{}: matched {}, not matched {}".format(
                router, len(netixlans), notmatched))
