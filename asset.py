#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['Asset']
__metaclass__ = PoolMeta


class Asset:
    __name__ = 'asset'
    owner = fields.Many2One('party.party', 'Owner')
    address = fields.Many2One('party.address', 'Address',
        domain=[
            ('party', '=', Eval('owner')),
            ],
        depends=['owner'])
    contact = fields.Many2One('party.party', 'Contact')
    owner_reference = fields.Char('Owner Reference')

    @fields.depends('owner')
    def on_change_owner(self):
        self.address = None
        if self.owner:
            self.address = self.owner.address_get()
