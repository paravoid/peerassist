from django.db import models

from django_peeringdb.models.concrete import NetworkIXLan


class Peering(models.Model):
    netixlan = models.OneToOneField(
        NetworkIXLan, db_index=True, on_delete=models.CASCADE
    )
    router = models.CharField(max_length=255, db_index=True)

    def __repr__(self):
        peer_name = self.netixlan.net.name
        ixp_name = self.netixlan.ixlan.ix.name
        return f"Peering with {peer_name} at {ixp_name}"
