# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import date, datetime
from sql import Null, Literal
from sql.conditionals import Coalesce

from trytond import backend
from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.transaction import Transaction

from trytond.modules.asset.asset import AssetAssignmentMixin

__all__ = ['Asset', 'AssetOwner']


class AssetOwner(AssetAssignmentMixin):
    'Asset Owner'
    __name__ = 'asset.owner'
    asset = fields.Many2One('asset', 'Asset', required=True, ondelete='CASCADE')
    owner = fields.Many2One('party.party', 'Owner',
        required=True)
    contact = fields.Many2One('party.party', 'Contact')
    owner_reference = fields.Char('Owner Reference')

    @classmethod
    def __register__(cls, module_name):
        pool = Pool()
        Asset = pool.get('asset')
        TableHandler = backend.get('TableHandler')
        cursor = Transaction().connection.cursor()

        table = cls.__table__()
        asset_table = Asset.__table__()

        handler = TableHandler(Asset, module_name)
        migrate_data = not handler.table_exist(cls._table)
        owner_exist = handler.column_exist('owner')

        super(AssetOwner, cls).__register__(module_name)

        # Migration: owner from asset table
        if migrate_data and owner_exist:
            cursor.execute(*table.insert([
                    table.asset,
                    table.owner,
                    table.contact,
                    table.owner_reference,
                    table.from_date],
                    asset_table.select(
                        asset_table.id,
                        asset_table.owner,
                        asset_table.contact,
                        asset_table.owner_reference,
                        Literal(date.min),
                        where=asset_table.owner != Null)))


class Asset:
    __name__ = 'asset'
    __metaclass__ = PoolMeta
    owners = fields.One2Many('asset.owner', 'asset', 'Owners')
    current_owner = fields.Function(fields.Many2One('party.party',
            'Current Owner'),
        'get_current_owner', searcher='search_current_owner')
    current_owner_contact = fields.Function(fields.Many2One('party.party',
            'Current Owner Contact'),
        'get_current_owner')

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

    @classmethod
    def search_current_owner(cls, name, clause):
        pool = Pool()
        Date = pool.get('ir.date')
        AssetOwner = pool.get('asset.owner')
        Party = pool.get('party.party')
        transaction = Transaction()
        table = AssetOwner.__table__()
        party = Party.__table__()
        condition = party.id == table.owner
        tables = {
            None: (table, None),
            'owner': {
                None: (party, condition),
                }
            }
        date = transaction.context.get('_datetime', Date.today())
        if isinstance(date, datetime):
            date = date.date()
        new_clause = tuple(('owner',)) + tuple(clause[1:])
        expression = AssetOwner.owner.convert_domain(new_clause, tables,
            AssetOwner)
        query = party.join(table, condition=condition).select(
            table.asset, where=(
                (Literal(date) >= Coalesce(table.from_date, date.min))
                & (Literal(date) <= Coalesce(table.through_date, date.max))
                & expression))
        return [('id', 'in', query)]
