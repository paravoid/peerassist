from django.db import models

from django_peeringdb.models.concrete import Network


class ASRank(models.Model):
    net = models.OneToOneField(
        Network, verbose_name="Network", primary_key=True, on_delete=models.CASCADE
    )
    rank = models.PositiveIntegerField("CAIDA Rank")

    def __repr__(self):
        return f"<ASRank: {self.net}={self.rank}>"
