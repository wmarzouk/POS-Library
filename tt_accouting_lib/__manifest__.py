# -*- coding: utf-8 -*-
{
    'name': 'TT Accounting Library',
    'version': '1.5',
    'category': 'Accounting',
    'summary': 'Accounting Library',
    'description': """
TechnoTown Accounting Library
=============================
This module enrich ODOO Accounting with the below features:

    1) Adding Debit/Credit Note.
    2) Exporting the P&L , Balance Sheet and Trial Balance Reports as Excel.
    3) Export GL as excel.
    4) Pre payment feature.
    5) Print Payment Receipts and Journal Entries
""",
    'website': 'https://www.technotown.technology/',
    'author' : 'Techno Town',
    'depends': ['base', 'product','mail','account','account_accountant'],
    'data': [ 'data/fin_docs_data.xml',
        'security/account_lib_security.xml',
        'security/ir.model.access.csv',
        'views/financial_documents.xml',
        'views/excel_account_report.xml',
        'views/account_account_inh.xml',
        'views/pre_payment_view.xml',
        'wizard/level_trial_balance.xml',
        'report/journal_entry_receipt.xml',
        'report/payment_receipt_print.xml',
        ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
