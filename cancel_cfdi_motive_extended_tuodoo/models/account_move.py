
import base64
from itertools import groupby
import re
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
import requests
from pytz import timezone

from lxml import etree
from lxml.objectify import fromstring
from zeep import Client
from zeep.transports import Transport

from odoo import _, api, fields, models, tools
from odoo.tools.xml_utils import _check_with_xsd
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools import float_round
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_repr

import logging
_logger = logging.getLogger(__name__)



class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_mx_xma_cfdi_cancel_to_cancel = fields.Boolean(
        string='Documento a cancelar',
        copy=False,
        default=False,
    )
    l10n_mx_xma_cfdi_cancel_cancel_type_id = fields.Many2one(
        'edi.mx.cancel.motive',
        string='Motivo de cancelación',
        copy=False,
    )

    replace_uuid = fields.Char(string="Reemplazar Folio Fiscal", copy=False)

    code_motive = fields.Char(
        string='Code',
        related="l10n_mx_xma_cfdi_cancel_cancel_type_id.default_code",
        store=True,
        copy=False,

    )

    def button_cancel_posted_moves(self):
        '''Mark the edi.document related to this move to be canceled.
        '''
        res = super().button_cancel_posted_moves()

        self.l10n_mx_xma_cfdi_cancel_to_cancel = True

        return res