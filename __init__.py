# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import asset


def register():
    Pool.register(
        asset.AssetOwner,
        asset.Asset,
        module='asset_owner', type_='model')
