
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



class AccountPayment(models.Model):
    _inherit = 'account.payment'


    def action_cancel(self):
        '''Mark the edi.document related to this move to be canceled.
        '''
        res = super().action_cancel()

        self.l10n_mx_xma_cfdi_cancel_to_cancel = True

        return res

    l10n_mx_xma_cfdi_cancel_to_cancel = fields.Boolean(
        string='Documento a cancelar',
        copy=False,
        default=False,
    )
    l10n_mx_xma_cfdi_cancel_cancel_type_id = fields.Many2one(
        'edi.mx.cancel.motive',
        string='Motivo de cancelación',
        copy=False,
        domain=[('is_to_payment','=',True)]
    )

    replace_uuid = fields.Char(string="Reemplazar Folio Fiscal", copy=False)

    code_motive = fields.Char(
        string='Code',
        related="l10n_mx_xma_cfdi_cancel_cancel_type_id.default_code",
        store=True,
        copy=False,

    )


    # def _l10n_mx_edi_finkok_cancel(self, pac_info):
    #     '''CANCEL for Finkok.
    #     '''
    #     url = pac_info['url']
    #     username = pac_info['username']
    #     password = pac_info['password']
    #     for inv in self:
    #         uuid = inv.l10n_mx_edi_cfdi_uuid
    #         certificate_ids = inv.company_id.l10n_mx_edi_certificate_ids
    #         certificate_id = certificate_ids.sudo().get_valid_certificate()
    #         company_id = self.company_id
    #         cer_pem = certificate_id.get_pem_cer(certificate_id.content)
    #         key_pem = certificate_id.get_pem_key(
    #             certificate_id.key, certificate_id.password)
    #         cancelled = False
    #         code = False
    #         try:
    #             transport = Transport(timeout=20)
    #             client = Client(url, transport=transport)
    #             uuid_replace = inv.l10n_mx_edi_cancel_invoice_id.l10n_mx_edi_cfdi_uuid
    #             factory = client.type_factory('apps.services.soap.core.views')
    #             uuid_type = factory.UUID()
    #             uuid_type.UUID = uuid
    #             uuid_type.Motivo = inv.l10n_mx_xma_cfdi_cancel_cancel_type_id.default_code
    #             if inv.replace_uuid:
    #                 uuid_type.FolioSustitucion = inv.replace_uuid
    #             print("+++++++_l10n_mx_edi_finkok_cancel_service+++++++++++++",inv.l10n_mx_xma_cfdi_cancel_cancel_type_id.default_code)
    #             invoices_list = factory.UUIDArray(uuid_type)
    #             response = client.service.cancel(invoices_list, username, password, company_id.vat, cer_pem, key_pem)
    #         except Exception as e:
    #             inv.l10n_mx_edi_log_error(str(e))
    #             continue
    #         if not (hasattr(response, 'Folios') and response.Folios):
    #             msg = _('A delay of 2 hours has to be respected before to cancel')
    #         else:
    #             code = getattr(response.Folios.Folio[0], 'EstatusUUID', None)
    #             cancelled = code in ('201', '202')  # cancelled or previously cancelled
    #             # no show code and response message if cancel was success
    #             code = '' if cancelled else code
    #             msg = '' if cancelled else _("Cancelling got an error")
    #         inv._l10n_mx_edi_post_cancel_process(cancelled, code, msg)