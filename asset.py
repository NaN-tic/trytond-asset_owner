# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import ModelView, ModelSQL, fields
from trytond.modules.asset.asset import AssetAssigmentMixin

__all__ = ['Asset', 'AssetOwner']
__metaclass__ = PoolMeta


class AssetOwner(ModelSQL, ModelView, AssetAssigmentMixin):
    'Asset Owner'

    __name__ = 'asset.owner'

    owner = fields.Many2One('party.party', 'Owner')
    contact = fields.Many2One('party.party', 'Contact')
    asset = fields.Many2One('asset', 'Asset')
    owner_reference = fields.Char('Owner Reference')


class Asset:

    __name__ = 'asset'
    owners = fields.One2Many('asset.owner', 'asset', 'Owners')
