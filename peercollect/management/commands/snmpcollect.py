from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from snimpy.manager import Manager as M
from snimpy.manager import load
from snimpy.snmp import SNMPException
from django_peeringdb.models.concrete import NetworkIXLan
from peercollect.models import Peering


class Command(BaseCommand):
    help = "populate peering database from SNMP"

    def add_arguments(self, parser):
        parser.add_argument(
            "-n", "--dry-run", action="store_true", default=False, help="dry run"
        )

    def handle(self, *args, **options):
        # BGP4-MIB is IPv4-only. For IPv6, there are:
        #   * draft-ietf-idr-bgp4-mibv2-15 (IETF, but expired)
        #   * BGP4-V2-MIB-JUNIPER (Juniper)
        #   * BGP4V2-MIB (Foundry/Brocade)
        #   * CISCO-BGP4-MIB (Cisco)
        #   * ARISTA-BGP4V2-MIB (Arista)
        #   * FORCE10-BGP4-V2-MIB (Force10)
        #
        # Juniper was found to be buggy, and needs:
        #   set protocols bgp snmp-options emit-inet-address-length-in-oid
        # See:
        # https://puck.nether.net/pipermail/juniper-nsp/2017-March/034067.html
        # and the resulting PR 1265504 (reported from this codebase!)
        #
        # As of May 2020, there are still issues with parsing, needing
        # additional code to parse (address type, address) tuples. snimpy#90.
        #
        # This effectively means only IPv4 matches, which is probably okay for
        # this use case (and probably this decade).
        load("BGP4-MIB")

        for router, community in settings.SNMP_ROUTERS.items():
            m = M(host=router, community=community, version=2)

            netixlans = []
            notmatched = 0

            try:
                peers = m.bgpPeerRemoteAs
                for ip, asn in peers.iteritems():
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

            print(
                "{}: matched {}, not matched {}".format(
                    router, len(netixlans), notmatched
                )
            )
