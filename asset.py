# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import date
from sql import Null

from trytond import backend
from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.transaction import Transaction

from trytond.modules.asset.asset import AssetAssignmentMixin

__all__ = ['Asset', 'AssetOwner']
__metaclass__ = PoolMeta


class AssetOwner(AssetAssignmentMixin):
    'Asset Owner'
    __name__ = 'asset.owner'
    asset = fields.Many2One('asset', 'Asset')
    owner = fields.Many2One('party.party', 'Owner', required=True)
    contact = fields.Many2One('party.party', 'Contact')
    owner_reference = fields.Char('Owner Reference')


class Asset:
    __name__ = 'asset'
    owners = fields.One2Many('asset.owner', 'asset', 'Owners')
    current_owner = fields.Function(fields.Many2One('party.party',
        'Current Owner'), 'get_current_owner')
    current_owner_contact = fields.Function(fields.Many2One('party.party',
        'Current Owner Contact'), 'get_current_owner')

    @classmethod
    def __register__(cls, module_name):
        pool = Pool()
        AssetOwner = pool.get('asset.owner')
        TableHandler = backend.get('TableHandler')

        table = cls.__table__()
        asset_owner_table = AssetOwner.__table__()

        cursor = Transaction().cursor
        handler = TableHandler(cursor, cls, module_name)
        owner_exist = handler.column_exist('owner')
        contact_exist = handler.column_exist('contact')
        owner_reference_exist = handler.column_exist('owner_reference')

        super(Asset, cls).__register__(module_name)

        handler = TableHandler(cursor, cls, module_name)
        # Migration: owner Many2One replaced by One2Many
        if owner_exist:
            assert contact_exist and owner_reference_exist
            cursor.execute(*table.select(
                    table.id,
                    table.owner,
                    table.contact,
                    table.owner_reference,
                    where=table.owner != Null))
            for asset_id, owner_id, contact_id, owner_reference \
                    in cursor.fetchall():
                asset_owner_table.insert([
                        asset_owner_table.asset,
                        asset_owner_table.owner,
                        asset_owner_table.contact,
                        asset_owner_table.owner_reference,
                        asset_owner_table.from_date],
                    [[
                            asset_id,
                            owner_id,
                            contact_id if contact_id else Null,
                            owner_reference if owner_reference else Null,
                            date.min]])
            handler.drop_column('owner')
            handler.drop_column('contact')
            handler.drop_column('owner_reference')

    @classmethod
    def get_current_owner(cls, assets, names):
        pool = Pool()
        AssetOwner = pool.get('asset.owner')
        assigments = cls.get_current_values(assets, AssetOwner)
        result = {}
        for name in names:
            result[name] = dict((i.id, None) for i in assets)

        for asset, assigment_id in assigments.iteritems():
            if not assigment_id:
                continue
            assigment = AssetOwner(assigment_id)
            if 'current_owner' in names:
                result['current_owner'][asset] = (assigment.owner.id
                    if assigment.owner else None)
            if 'current_owner_contact' in names:
                result['current_owner_contact'][asset] = (assigment.contact.id
                    if assigment.contact else None)
        return result
