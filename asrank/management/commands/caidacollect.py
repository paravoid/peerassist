from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from django.utils.six import iteritems

from django_peeringdb.models.concrete import Network

from asrank.client import fetch_from_caida
from asrank.models import ASRank


class Command(BaseCommand):
    help = "populate AS Rank from CAIDA"

    def handle(self, *args, **options):
        with transaction.atomic():
            # build a asn -> Network instance dict, as a performance optimization
            asn_to_net = Network.objects.only("asn").in_bulk(field_name="asn")

            asn_to_rank = {}
            for asn, rank in fetch_from_caida():
                if asn not in asn_to_net:
                    continue

                asn_to_rank[asn] = ASRank(net=asn_to_net[asn], rank=rank)

            # bulk create, as a performance optimization
            ASRank.objects.all().delete()
            ASRank.objects.bulk_create(asn_to_rank.values())

        print(f"Imported ranks for {len(asn_to_rank)}/{len(asn_to_net)} ASNs")
