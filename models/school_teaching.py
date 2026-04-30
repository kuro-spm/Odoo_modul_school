# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError

class SchoolTeaching(models.Model):
    _name = 'school.teaching'
    _description = 'Teaching Management'

    teacher_id = fields.Many2one('school.teacher', string="Teacher", required=True)
    edition_id = fields.Many2one('school.course.edition', string="Edition", required=True)
    subject_id = fields.Many2one('school.subject', string="Subject", required=True)

    # Related fields per a utilitzar en les views:
    course_edition_course_id = fields.Many2one('school.course', string="Course", related="edition_id.course_id")
    subject_teacher_ids = fields.Many2many('school.teacher',related='subject_id.teacher_ids', string="Authorized Teachers")  #llista de professors que saben fer l'assignatura
    


