======================
Party Replace Scenario
======================

Imports::

    >>> import datetime
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> today = datetime.date(2015, 1, 1)

Install asset_owner::

    >>> config = activate_modules('asset_owner')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create a party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Customer')
    >>> party.save()
    >>> party2 = Party(name='Customer')
    >>> party2.save()

Create asset::

    >>> Asset = Model.get('asset')
    >>> Owner = Model.get('asset.owner')
    >>> asset = Asset()
    >>> asset.name = 'Asset'
    >>> asset.save()
    >>> owner = Owner()
    >>> owner.asset = asset
    >>> owner.owner = party
    >>> owner.contact = party
    >>> owner.save()

Try replace active party::

    >>> replace = Wizard('party.replace', models=[party])
    >>> replace.form.source = party
    >>> replace.form.destination = party2
    >>> replace.execute('replace')

Check fields have been replaced::

    >>> owner.reload()
    >>> owner.owner == party2
    True
    >>> owner.contact == party2
    True
