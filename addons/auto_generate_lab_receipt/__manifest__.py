{
    'name': 'Auto Generate Lab Receipt',
    'version': '16.0.1.0',
    'summary': 'Generate PDF receipts for lab reports',
    'category': 'Healthcare',
    'author': 'Yogita-ODOO',
    'depends': ['base', 'web'],
    'data': [
        'views/lab_report_views.xml',
        'views/lab_info_views.xml',
        'report/lab_report_template.xml',
        'report/lab_report_action.xml',
        'report/report_assets.xml',
    ],
    'images': ['static/description/lab_report.gif'],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}