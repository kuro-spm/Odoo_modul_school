# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
from ..utils.utils import is_valid_email

# Per importar funció is_valid_email que es troba en fitxer utils.py a la carpeta de nivell superior:
#from ..utils import is_valid_email

# Per importar funció is_valid_email que es troba en fitxer utils.py a mateixa carpeta:
#from .utils import is_valid_email

# Per importar funció is_valid_email que es troba en fitxer utils.py a la carpeta de 2 nivells per damunt:
# from ...utils import is_valid_email

# Per importar funció is_valid_email que es troba en fitxer utils.py en una subcarpeta xxx:
# from .xxx.utils import is_valid_email



class SchoolCourse(models.Model):
    _name = 'school.course'
    _description = 'Course Management'

    name = fields.Char('Name', size=60, required=True)
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)
    summary = fields.Text('Summary', required=False) #Alternativa: Html.
    
    #relacio Many to One: MANY CURSOS pot tenir ONE teacher. un teacher pot tenir molts cursos.
    manager_id = fields.Many2one('school.teacher', 'Manager', required=True) #No seria required si fos 0..1
    #camps relacionats amb teacher:
    manager_phone = fields.Char('Phone', related='manager_id.phone')
    manager_email = fields.Char('eMail', related='manager_id.email')
    manager_citizenship = fields.Char('Citizenship', related='manager_id.country_id.name')
    #manager_citizenship = fields.Many2One('res.country','Citizenship', related='manager_id.country_id')

    #subject_ids = fields.Many2many(comodel_name='school.subject', relation='school_course_subject_rel', column1='course_id', column2='subject_id', string='Subjects', readonly=True)
    course_subject_ids = fields.One2many('school.course.subject', 'course_id', string='Subjects')
    thematic_id = fields.Many2one('school.thematic', string='Thematic', required=True)
    course_call_ids = fields.One2many('school.course.call', 'course_id', string='Calls')

    @api.constrains('hours')
    def check_hours(self):
        for crs in self:
            if crs.hours<0:
                raise ValidationError(_('Hours must be positive.'))


class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'Subject Management'

    name = fields.Char('Name', size=60, required=True, translate=True) #S'ha de poder traduir
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)
    teacher_ids = fields.Many2many('school.teacher', 'school_teacher_subject_rel',
                                   'subject_id', 'teacher_id', string='Teachers authorized', readonly=True)
    #course_ids = fields.Many2many('school.course', 'school_course_subject_rel', 'subject_id', 'course_id', readonly=True)
    course_subject_ids = fields.One2many('school.course.subject', 'subject_id', string='Courses')
    
    @api.constrains('hours')
    def check_hours(self):
        for sbj in self:
            if sbj.hours<0:
                raise ValidationError(_('Hours must be positive.'))
            
class CourseSubject(models.Model):
    _name = 'school.course.subject'
    _description = 'Course Subject Rel Management'
    _order = 'course_id,number'

    _order = 'number'
    number = fields.Integer('Number', required=True)
    #La relació intermitja (aquesta) té dues relacions Many2one, mentre que les dues classes a les que apunten tindràn cadascuna una relació One2Many
    course_id = fields.Many2one('school.course', string='Course', required=True, ondelete='cascade')
    subject_id = fields.Many2one('school.subject', string='Subject', required=True)

    @api.constrains('number')
    def check_number(self):
        for num in self:
            if(num.number<0):
                raise ValidationError(_('Number must be positive.'))

    # hauríem de controlar que en un curs no hi hagi dues assignatures amb el mateix number ni assignatures repetides.



class SchoolTeacher(models.Model):
    #El _ al davant indica que és privat.
    _name = 'school.teacher'
    _description = 'Teacher Management'
    _rec_name = 'display_name' #Per defecte és Name, però no tenim aquest camp
    _order = 'first_name, last_name'

    first_name = fields.Char('First Name', size=30, required=True)
    last_name = fields.Char('Last Name', size=40, required=True)
    birthdate = fields.Date('Birthdate', required=True)
    tin = fields.Char('Tax ID', size=14)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other','Other')],'Gender')
    salary = fields.Integer('Salary')
    email = fields.Char('eMail', size=60, required=True)
    phone = fields.Char('Phone')
    active = fields.Boolean('Active?', default=True)
    photo = fields.Binary(string="Photo", max_width=1024, max_height=1024, required=True, attachment="False") #obligar a guardar la foto sencera directament dins de la taula del professor
    #Relacio One2Many: ONE TEACHER pot tenir MANY cursos. Un curs pot tenir un teacher. 
    course_ids = fields.One2many('school.course', 'manager_id', string='Courses', readonly=True)    #_rec_name= "first_name"
    subject_ids = fields.Many2many(comodel_name='school.subject',relation='school_teacher_subject_rel', column1='teacher_id', column2='subject_id',string='Subjects authorized')
    ####teacher_ids = fields.Many2many('school.teacher', 'school_teacher_subject_rel','subject_id', 'teacher_id', string='Teachers authorized', readonly=True)

    #comodel_name= nom de la relació a la que apunta
    #relation = nom de la nova taula que es crea i que conté la relació
    #column1 i column2 han d'estar girades respecte la many2many definida a teacher!!
    country_id = fields.Many2one('res.country','Citizenship', required=True)
    #Camps calculats:
    #full_name= fields.Char('Full name', compute='_compute_full_name', store=False)
    #Treiem el full_name perquè farem servir display_name.
    age =fields.Integer('Age', compute='_compute_age', store=False)

    #El _ al davant indica que és privat.
    @api.depends('first_name', 'last_name')
    def _compute_display_name(self):
        #self és equivalent a this.
        #és el conjunt de registres (recordset) sobre el que es necessita executar el mètode.
        for tchr in self:
            if tchr.first_name and tchr.last_name:
                tchr.display_name = tchr.last_name + ", " + tchr.first_name
            else:
                tchr.display_name = ''
            
    @api.depends('birthdate')
    def _compute_age(self):
        avui = date.today()
        for tchr in self:
            if tchr.birthdate: 
                tchr.age = relativedelta(avui, tchr.birthdate).years
            else:
                tchr.age = 0

    @api.constrains('salary')
    def check_salary(self):
        for tchr in self:
            if tchr.salary<0:
                raise ValidationError(_('Salary must be positive.'))

    @api.constrains('phone')
    def check_phone(self):
        for tchr in self:
            if tchr.phone and not tchr.phone.isdigit():
                raise ValidationError(_("The teacher's phone number can only contain digits."))
    
    @api.constrains('email')
    def check_email(self):
        for tchr in self:
            if tchr.email and not is_valid_email(tchr.email):
                raise ValidationError(_("The teacher's email is invalid."))
            



class SchoolThematic(models.Model):
    _name = 'school.thematic'
    _description = 'Thematic Management'

    name = fields.Char('Name', required=True)
    course_ids = fields.One2many('school.course', 'thematic_id', string='Courses')
    # Relació recursiva:
    parent_id = fields.Many2one('school.thematic', string='Parent Thematic')
    child_ids = fields.One2many('school.thematic', 'parent_id', string='Child Thematics')

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        # _check_recursion() es una función nativa de Odoo. 
        # Devuelve False si detecta un bucle infinito (Ej: A es padre de B, y B es padre de A)
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create infinite recursive topics.'))

class CourseCall(models.Model):
    _name='school.course.call'
    _description ='Course Call Management'

    name=fields.Char('Course call', required=True)
    date_start = fields.Date('Start Date', required=True)
    date_finish = fields.Date('Finish Date')
    #Com que CourseCall té una relació de composició amb curs, si s'elimina el curs, s'han d'eliminar les convocatories també.
    course_id = fields.Many2one('school.course', string='Called Course', required=True, ondelete='cascade')  
    @api.constrains('date_start', 'date_finish')
    def _check_dates(self):
        for call in self: #necessita un singleton
            if call.date_start and call.date_finish:
                if call.date_finish < call.date_start:
                    raise ValidationError(_("The finish date cannot be earlier than the start date."))







    
