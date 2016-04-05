from __future__ import print_function
from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django_peeringdb.models import Network

from peermatch.textviews import email


class Command(BaseCommand):
    help = "peer with an ASN"

    def add_arguments(self, parser):
        parser.add_argument('asn', type=int)

    def handle(self, *args, **options):
        us = Network.objects.get(asn=settings.OUR_ASN)

        try:
            them = Network.objects.get(asn=options['asn'])
        except Network.DoesNotExist:
            raise CommandError('Peer network does not exist')

        if us == them:
            raise CommandError('Do you really want to peer with yourself?')

        print(email(us, them))
