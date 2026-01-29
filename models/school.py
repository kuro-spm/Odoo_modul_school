# -*- coding: utf-8 -*-
from odoo import models,fields

class SchoolCourse(models.Model):
    _name = 'school.course'
    _description = 'Course Management'

    name = fields.Char('Name', size=60, required=True)
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)
    manager_id = fields.Many2one('school.teacher', 'Manager') #No és required perquè és 0..1


class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'Subject Management'
    _rec_name = 'first_name'

    name = fields.Char('Name', size=60, required=True)
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)


class SchoolTeacher(models.Model):
    _name = 'school.teacher'
    _description = 'Teacher Management'

    first_name = fields.Char('First Name', size=30, required=True)
    last_name = fields.Char('Last Name', size=40, required=True)
    birthdate = fields.Date('Birthdate', required=True)
    tin = fields.Char('Tax ID', size=14)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],'Gender')
    salary = fields.Integer('Salary')
    email = fields.Char('eMail', size=60, required=True)
    phone = fields.Char('Phone')
    course_ids = fields.One2many('school.course', 'manager_id', string='Courses')    #_rec_name= "first_name"


    
