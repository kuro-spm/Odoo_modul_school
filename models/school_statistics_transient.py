# -*- coding: utf-8 -*-
from odoo import models, fields, drop_view_if_exists, _
from odoo.exceptions import ValidationError


#Les classes d'aquest tipus només tindràn privilegis de lectura!
#També està bé posar delete="0" i create="0" a les vistes.
#_auto=False  fa que no es crei la taula a la base de dades!
class SchoolStatistics(models.Model):
    _name = 'school.statistics'
    _description = 'SchoolStatistics management'
    _auto=False  #_auto=False  fa que no es crei la taula a la base de dades!
    _order='year desc, qty_editions desc, course_name'

    course_name = fields.Char('Course', size=60)
    year = fields.Integer('Year')
    qty_editions = fields.Integer(string='# Editions')

    #select sce.course_id, sc.name, date_part('year', sce.date_start), count(*)
    #from school_course_edition sce
    #join school_course sc on sc.id = scd.course_id
    #group by date_part('year', sce.date_start)

    #Recordatori: \d nom_de_la_taula per fer un desc.

    def init(self):
        cr = self._cr
        drop_view_if_exists(cr, 'school_year_course_qty_editions')
        #estem obligats a posar un id a la select en primera posició!!!
        #també es obligatori fer servir alies amb els noms dels camps de la classe!

    
