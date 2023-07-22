# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##################################################################################

{
    'name': 'General Ledger Report with Advance Filter(Enterprise Edition)',
    'version': '13.0.0.1',
    'category': 'Accounting',
    'summary': 'Apps for apply account and account type fiter on General Ledger Report by account type General Ledger Report with Account Type Filter General Ledger Report with Account Filter Enterprise General Ledger Report filter with account type',
    'description': """
    
    Detailed General Ledger
    This apps helps to apply account and account type fiter on General Ledger Report
    General Ledger Report filter by Accounts
	General Ledger filter in odoo
	General Ledger filter for 
    Account Filter on General Ledger Reports
    Accounting Filter on General Ledger Reports
    Filter By Account on General Ledger Report
    Account Filter on Accounting Report

    General Ledger Report with Account Type Filter
	General Ledger Report with analytic account
	General Ledger filter with analytic account
	General Ledger Report filter by Account Type
    Account Type Filter on General Ledger Reports
    Accounting Type Filter on General Ledger Reports
    Filter By Account Type on General Ledger Report
    Account Type Filter on Accounting Report
    general Ledger report filter with Account
    General Ledger report filter with account type
    enterprise accounting report filter

    General Ledger Report filter by Balance
    Balace Filter on General Ledger Reports
    With Balance Filter on General Ledger Reports
    Without Balance Filter on General Ledger Reports
    Filter By Balance on General Ledger Report
    Balance without Filter on Accounting Report
    general Ledger report filter with balance amount
    General Ledger report filter without balance amount
    enterprise general ledger report filter
    View general ledger report with Display Name
    Display Name on general Ledger Report
    Display name visible on general ledger report
""",
    'author': 'BrowseInfo',
    'price': 49,
    'currency': "EUR",
    'website': 'https://www.browseinfo.in',
    'depends': ['account', 'account_accountant', 'account_reports'],
    'data': [

        'data/account_financial_report_data.xml',
        'views/general_ledger_filter.xml',
        'views/custom_account_report.xml',
    ],
    'qweb': [
         'static/src/xml/custom_account_report.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url':'https://youtu.be/ZVH7DUkT8-M',
    "images":['static/description/Banner.png'],
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
