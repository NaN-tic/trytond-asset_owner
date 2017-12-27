# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.asset_owner.tests.test_asset_owner import suite
except ImportError:
    from .test_asset_owner import suite

__all__ = ['suite']
