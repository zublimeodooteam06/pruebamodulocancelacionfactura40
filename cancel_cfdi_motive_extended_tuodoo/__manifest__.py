# -*- coding: utf-8 -*-
{
    'name': "Motivos para Cancelar CFDI",

    'summary': """Agrega las opciones 03 y 04 dentro de un catalago en Contabilidad / Ajustes / Motivos de cancelación para su uso dentro de la solicitud de cancelación.""",

    'description': """Agrega las opciones 03 y 04 dentro de un catalago en Contabilidad / Ajustes / Motivos de cancelación para su uso dentro de la solicitud de cancelación.
    """,

    'author': "TuOdoo",
    'website': "http://www.tuodoo.com",
    'category': 'Account',
    'version': '14.0.0.1',
    'depends': ['account','l10n_mx_edi'],
    'data': [
        'security/edi_mx_cancel_motive.xml',
        'data/data.xml',
        'views/edi_mx_cancel_motive.xml',
        'views/account_move.xml',
        'views/account_payment.xml',
    ],
}
