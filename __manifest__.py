# -*- coding: utf-8 -*-
{
    'name': "Örgüt Yönetim Uygulaması",

    'summary': """
        Türkiye İşçi Partisi Örgüt Yönetim Uygulaması""",

    'description': """
        Türkiye İşçi Partisi Üye Yönetim Yazılımı
    """,
    'sequence': -100,
    "installable": True,
    "application": True,

    'author': "Türkiye İşçi Partisi",
    'website': "https://tip.org.tr",

    'version': '17.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'base_address_extended', 'portal'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/orgut_region_views.xml',
        'views/orgut_state_views.xml',
        'views/orgut_city_views.xml',
        'views/res_partner_inherit_views.xml',
        'views/orgut_yonetimi_menuitem.xml',
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
