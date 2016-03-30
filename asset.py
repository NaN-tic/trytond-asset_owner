# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta, Pool
from trytond.model import ModelView, ModelSQL, fields
from trytond.modules.asset.asset import AssetAssigmentMixin

__all__ = ['Asset', 'AssetOwner']
__metaclass__ = PoolMeta


class AssetOwner(AssetAssigmentMixin):
    'Asset Owner'

    __name__ = 'asset.owner'

    owner = fields.Many2One('party.party', 'Owner')
    contact = fields.Many2One('party.party', 'Contact')
    asset = fields.Many2One('asset', 'Asset')
    owner_reference = fields.Char('Owner Reference')


class Asset:

    __name__ = 'asset'
    owners = fields.One2Many('asset.owner', 'asset', 'Owners')
    current_owner = fields.Function(fields.Many2One('party.party',
        'Current Owner'), 'get_current_owner')
    current_owner_contact = fields.Function(fields.Many2One('party.party',
        'Current Owner Contact'), 'get_current_owner')

    @classmethod
    def get_current_owner(cls, assets, names):
        pool = Pool()
        AssetOwner = pool.get('asset.owner')
        assigments = cls.get_current_values(assets, AssetOwner)
        result = {}
        for name in names:
            result[name] = dict((i.id, None) for i in assets)

        print "***************************************************"
        print assigments
        for asset, assigment_id in assigments.iteritems():
            print "asset", asset, assigment_id
            if not assigment_id:
                continue
            assigment = AssetOwner(assigment_id)
            result['current_owner'][asset] = assigment.owner.id
            result['current_owner_contact'][asset] = assigment.contact and \
                assigment.contact.id
        return result
