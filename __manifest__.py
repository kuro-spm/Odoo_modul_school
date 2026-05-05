# -*- coding: utf-8 -*-
{
    'name': 'School',
    'version': '3.0',
    'category': 'Education',
    'summary': 'School Management',
    'description': """
          Module prepared by department 'Informàtica i comunicacions'
          of Institute Milà i Fontanals in Igualada (Barcelona-Spain)
          for learning in development and adaptation of modules of Odoo ERP.

          It is part of the learning materials for the module
          'Sistemes de gestió empresarial' in the course
          'CFS Desenvolupament d''aplicacions multiplataforma'.
    """,
    'author': 'Group DAM2 - Course 2025-2026',
    'website': 'http://www.infomila.info',
    'depends': ['base'],
    'data': [
        'views/actions.xml',   # primer accions
        'views/menus.xml',     # després menús
        'views/course_views.xml',
        'views/course_edition_views.xml',
        'views/subject_views.xml',
        'views/teacher_views.xml',
        'views/thematic_views.xml',
        'views/teaching_views.xml',
        'reports/report_school_course.xml',
        'reports/report_school_teacher.xml',
     
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}