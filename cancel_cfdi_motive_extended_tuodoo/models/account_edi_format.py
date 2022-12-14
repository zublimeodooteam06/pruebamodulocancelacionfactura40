from odoo import api, fields, models, _
from odoo.exceptions import UserError

from zeep import Client
from zeep.transports import Transport
import logging
_logger = logging.getLogger(__name__)



class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_finkok_cancel(self, move, credentials, cfdi):
        print("+++++++_l10n_mx_edi_finkok_cancel+++++++++++++")
        context = dict(self._context)
        context['cancel_reason_code'] = move.l10n_mx_xma_cfdi_cancel_cancel_type_id.default_code if move.l10n_mx_xma_cfdi_cancel_cancel_type_id.default_code else move.payment_id.l10n_mx_xma_cfdi_cancel_cancel_type_id.default_code
        context['cancel_replace_folio'] = move.replace_uuid if move.replace_uuid else move.payment_id.replace_uuid

        return self.with_context(context)._l10n_mx_edi_finkok_cancel_service(
            move.l10n_mx_edi_cfdi_uuid, move.company_id, credentials)

    def _l10n_mx_edi_finkok_cancel_service(self, uuid, company, credentials):
        ''' Cancel the CFDI document with PAC: finkok. Does not depend on a recordset
        '''
        print("+++++++_l10n_mx_edi_finkok_cancel_service+++++++++++++",self._context.get('cancel_reason_code'))
        certificates = company.l10n_mx_edi_certificate_ids
        certificate = certificates.sudo().get_valid_certificate()
        cer_pem = certificate.get_pem_cer(certificate.content)
        key_pem = certificate.get_pem_key(certificate.key, certificate.password)
        if company.l10n_mx_edi_pac_test_env:
            return {
                    'errors': [_("No es posible cancelar en modo pruebas. Solo funciona en módo productivo.")],
                }
        else:
            try:
                transport = Transport(timeout=20)
                client = Client(credentials['cancel_url'], transport=transport)
                uuid_type = client.get_type('ns1:UUID')()
                uuid_type.UUID = uuid
                uuid_type.FolioSustitucion = self._context.get('cancel_replace_folio') or ""
                if not self._context.get('cancel_reason_code'):
                    raise UserError("reason not defined")
                uuid_type.Motivo = self._context.get('cancel_reason_code')
                docs_list = client.get_type('ns1:UUIDS')(uuid_type)
                _logger.info("VALORESSSSSSSSSSSS  uuid_type <%s>", docs_list,credentials['username'],credentials['password'])
                response = client.service.cancel(
                    docs_list,
                    credentials['username'],
                    credentials['password'],
                    company.vat,
                    cer_pem,
                    key_pem,
                )
            except Exception as e:
                return {
                    'errors': [_("The Finkok service failed to cancel with the following error: %s", str(e))],
                }

        if not getattr(response, 'Folios', None):
            code = getattr(response, 'CodEstatus', None)
            msg = _("Cancelling got an error") if code else _('A delay of 2 hours has to be respected before to cancel')
        else:
            code = getattr(response.Folios.Folio[0], 'EstatusUUID', None)
            cancelled = code in ('201', '202')  # cancelled or previously cancelled
            # no show code and response message if cancel was success
            code = '' if cancelled else code
            msg = '' if cancelled else _("Cancelling got an error")

        errors = []
        if code:
            errors.append(_("Code : %s") % code)
        if msg:
            errors.append(_("Message : %s") % msg)
        if errors:
            return {'errors': errors}

        return {'success': True}
