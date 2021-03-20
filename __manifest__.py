# -*- coding: utf-8 -*-
{
    "name" : "InfoSaône - Module Odoo 14 pour Agenda Plastigray",
    "version" : "0.1",
    "author" : "InfoSaône / Tony Galmiche",
    "category" : "InfoSaône",
    "description": """
    InfoSaône - Module Odoo 14 pour Agenda Plastigray
    ===================================================
    InfoSaône - Module Odoo 14 pour Agenda Plastigray
    """,
    "maintainer": "InfoSaône",
    "website": "https://infosaone.com",
    "depends" : [
        "base",
        "calendar",
    ], 
    "init_xml" : [],
    "demo_xml" : [],
    "data" : [
        "security/ir.model.access.csv",
        "security/ir.rule.xml",
        "views/calendar_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "active": False,
    "application": True,
}
