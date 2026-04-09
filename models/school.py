# -*- coding: utf-8 -*-
from odoo import models, fields, api, _ , tools
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
    _order = 'name'

    name = fields.Char('Name', size=60, required=True)
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)
    summary = fields.Text('Summary', required=False) #Alternativa: Html.
    
    manager_id = fields.Many2one('school.teacher', 'Manager', required=True) #, domain=[('country_id.code', '=', 'ES')])     #relacio Many to One: MANY CURSOS pot tenir ONE teacher. un teacher pot tenir molts cursos.
    course_subject_ids = fields.One2many('school.course.subject', 'course_id', string='Subjects', readonly=True) 
    thematic_id = fields.Many2one('school.thematic', string='Thematic', required=True)
    course_edition_ids = fields.One2many('school.course.edition', 'course_id', string='Editions')

    #Camps extra per a poder posar-los en les vistes
    manager_phone = fields.Char('Phone', related='manager_id.phone')
    manager_email = fields.Char('eMail', related='manager_id.email')
    manager_citizenship = fields.Many2one('res.country', string='Citizenship', related='manager_id.country_id')     #manager_citizenship = fields.Char('Citizenship', related='manager_id.country_id.name')


    @api.constrains('hours')
    def check_hours(self):
        for crs in self:
            if crs.hours <= 0:
                raise ValidationError(_('Hours must be positive.'))

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.name = self.name.capitalize()
  

class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'Subject Management'
    _order = 'name'

    name = fields.Char('Name', size=60, required=True, translate=True) #S'ha de poder traduir
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)
    teacher_ids = fields.Many2many('school.teacher', 'school_teacher_subject_rel',
                                   'subject_id', 'teacher_id', string='Teachers authorized', readonly=True)
    #course_ids = fields.Many2many('school.course', 'school_course_subject_rel', 'subject_id', 'course_id', readonly=True)
    course_subject_ids = fields.One2many('school.course.subject', 'subject_id', string='Courses', readonly=True)
    
    @api.constrains('hours')
    def check_hours(self):
        for sbj in self:
            if sbj.hours<0:
                raise ValidationError(_('Hours must be positive.'))
            
    @api.onchange('name')
    def _onchange_name(self):
        if self.name!=False:
            # Cal controlar que no sigui buit (quan es dona d'alta o modifica deixant-lo buit
            # ja que no es pot aplicar upper() sobre un "buit" (en realitat "False")
            self.name = self.name.capitalize()
            


class SchoolTeacher(models.Model):
    #El _ al davant indica que és privat.
    _name = 'school.teacher'
    _description = 'Teacher Management'
    _rec_name = 'display_name' #Per defecte és Name, però no tenim aquest camp
    _order = 'last_name,first_name'

    _sql_constraints=[
        ('ck_salari','check(salary>=0)','Salary must be positive (controlled by BD)')
    ]
    #_sql_constraints=[('ck_salari','check(salary>=0)','Salary must be positive (controlled by BD)''')
    # No és habitual incorporar una check a la BD. S'utilitzen les @api.constraints
    # on Odoo controla la restricció abans d'enviar la instrucció insert/update a la BD
    # Aquí s'ha incorporat com exemple

    first_name = fields.Char('First Name', size=30, required=True)
    last_name = fields.Char('Last Name', size=40, required=True)
    birthdate = fields.Date('Birthdate', required=True)
    tin = fields.Char('Tax ID', size=14)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other','Other')],'Gender')
    salary = fields.Integer('Salary')
    email = fields.Char('eMail', size=60, required=True)
    phone = fields.Char('Phone')
    photo = fields.Binary(string="Photo", required=True, attachment=False) #obligar a guardar la foto sencera directament dins de la taula del professor     #max_width=1024, max_height=1024, si és Image
    active = fields.Boolean('Active?', default=True)
    
    
    course_ids = fields.One2many('school.course', 'manager_id', string='Courses', readonly=True)     #Relacio One2Many: ONE TEACHER pot tenir MANY cursos. Un curs pot tenir un teacher. 
    country_id = fields.Many2one('res.country','Citizenship', required=True)
    subject_ids = fields.Many2many(comodel_name='school.subject',relation='school_teacher_subject_rel', column1='teacher_id', column2='subject_id',string='Subjects authorized')
    #Relació inversa: teacher_ids = fields.Many2many(comodel_name='school.teacher', relation='school_teacher_subject_rel', column1='subject_id', column2='teacher_id', string='Teachers authorized', readonly=True)
    #comodel_name= nom de la relació a la que apunta
    #relation = nom de la nova taula que es crea i que conté la relació
    #column1 i column2 han d'estar girades respecte la many2many definida a teacher!!

    #Computed fields:
    n_manager = fields.Integer(string='Num. courses', compute='_compute_n_manager')
    n_subject = fields.Integer(string='Num. subject', compute='_compute_n_subject')
    n_teaching = fields.Integer(string='Num. teaching', compute='_compute_n_teaching')
    age =fields.Integer('Age', compute='_compute_age', store=False)
    #full_name= fields.Char('Full name', compute='_compute_full_name', store=False) #Treiem el full_name perquè farem servir display_name.
    birthday_this_year = fields.Date(string='Birthday', compute='compute_birthday')
    age_celebrated =fields.Integer(string='Age celebrated', compute='_compute_age_celebrated')

    #El _ al davant indica que és privat.
    #Aqui configurem el display name!!!
    @api.depends('first_name', 'last_name')
    def _compute_display_name(self):
        #self és equivalent a this.
        #és el conjunt de registres (recordset) sobre el que es necessita executar el mètode.
        for tchr in self:
            if tchr.first_name and tchr.last_name:
                tchr.display_name = tchr.last_name + ", " + tchr.first_name
            else:
                tchr.display_name = ''

#DEPENDS:             
    @api.depends('birthdate')
    def _compute_age(self):
        avui = date.today()
        for tchr in self:
            if tchr.birthdate: 
                tchr.age = relativedelta(avui, tchr.birthdate).years
            

    @api.depends('birthdate')
    def _compute_birthday(self):
        avui = date.today()
        for tchr in self:
            if tchr.birthdate:
                try:
                    # Intentem crear la data amb l'any actual
                    tchr.birthday_this_year = tchr.birthdate.replace(year=avui.year)
                except ValueError:
                    # Si falla (és 29 de febrer i l'any actual no és de traspàs)
                    # segons el dossier, ho posem al 1 de març 
                    tchr.birthday_this_year = tchr.birthdate.replace(year=avui.year, month=3, day=1)
            else:
                tchr.birthday_this_year = False

    @api.depends('birthdate', 'birthday_this_year')
    def _compute_age_celebrated(self):
        for tchr in self:
            if tchr.birthdate and tchr.birthday_this_year:
                # L'edat que celebra és la diferència d'anys
                tchr.age_celebrated = tchr.birthday_this_year.year - tchr.birthdate.year
            else:
                tchr.age_celebrated = 0

#CONSTRAINS:
    @api.constrains('salary')
    def check_salary(self):
        for tchr in self:
            if tchr.salary<0:
                raise ValidationError(_('Salary must be positive.'))
    
    @api.constrains('email')
    def check_email(self):
        for tchr in self:
            if tchr.email and not is_valid_email(tchr.email):
                raise ValidationError(_("The teacher's email is invalid."))

    @api.constrains('phone')
    def check_phone(self):
        for tchr in self:
            if tchr.phone and not tchr.phone.isdigit():
                raise ValidationError(_("The teacher's phone number can only contain digits."))

#ONCHANGE                
    @api.onchange('tin')
    def _onchange_tin(self):
        if(self.tin):
            self.tin = self.tin.upper()

    def _auto_init(self):
        res = super(SchoolTeacher, self)._auto_init()
        tools.create_unique_index(self._cr, 'school_teacher_unique_tin',
                                  self._table, ['lower(tin)'])
        return res

    @api.depends('course_ids')
    def _compute_n_manager(self):
        #contar cursos dins de course_ids
        for teacher in self:
            teacher.n_manager = len(teacher.course_ids)

#DEPENDS:
    @api.depends('subject_ids')
    def _compute_n_subject(self):
        for teacher in self:
            teacher.n_subject = len(teacher.subject_ids)

    #Hem de fer servir el searchcount perque no tenim els cursos dins del model de teacher
    def _compute_n_teaching(self):
        for tchr in self:
            tchr.n_teaching = self.env['school.teaching'].search_count([('teacher_id', '=', tchr.id)])


class CourseSubject(models.Model):
    _name = 'school.course.subject'
    _description = 'Course Subject Rel Management'
    _order = 'number, course_id'
    _sql_constraints = [
        ('course_subject_unique','unique(course_id, subject_id)', _('The subject in a course must be unique!')),
        ('course_number_unique','unique(course_id, number)', _('The number in a course must be unique!'))
    ]
    #camps pròpis
    number = fields.Integer('Number', required=True)
    
    #La relació intermitja (aquesta) té dues relacions Many2one, mentre que les dues classes a les que apunten tindràn cadascuna una relació One2Many
    course_id = fields.Many2one('school.course', string='Course', required=True, ondelete='cascade')
    subject_id = fields.Many2one('school.subject', string='Subject', required=True, ondelete='restrict')
    
    #Related field per poder-ho afegir a la view:
    subject_hours = fields.Integer('Hours', related='subject_id.hours')

    @api.constrains('number')
    def check_number(self):
        for num in self:
            if(num.number<0):
                raise ValidationError(_('Number must be positive.'))

    @api.depends('number', 'course_id', 'subject_id')
    def _compute_display_name(self):
        for cs in self:
            if cs.number and cs.course_id and cs.subject_id:
                cs.display_name = cs.course_id.name + " - " + str(cs.number) + " - " + cs.subject_id.name
                #python no permet concatenar cadenes amb números, aiixí que necessitem posar str(variable_numerica).
            else:
                cs.display_name=''


class SchoolCourseEdition(models.Model):
    _name='school.course.edition'
    _description='Course Editions Management'
    _order='date_start'
    _sql_constraints = {
        ('unique_course_date_start', 'unique(course_id, date_start)',
         _('It''s not possible 2 course editions with same course and same date start'))
    }

    name = fields.Char('Course edition', required=True)
    date_start = fields.Date('Start Date', required=True)
    date_stop = fields.Date('Finish Date')

    # Com que SchoolCourseEdition té una relació de composició amb curs, si s'elimina el curs, s'han d'eliminar les edicions també.
    course_id = fields.Many2one('school.course', string='Course', required=True, ondelete='cascade')  

    #Camps calculats
    n_teachers = fields.Integer(string='N. Teachers', compute='_compute_n_teachers')

    @api.constrains('date_start', 'date_stop')
    def _check_dates(self):
        for edition in self:
            if edition.date_start and edition.date_stop:
                if edition.date_stop < edition.date_start:
                    raise ValidationError(_("The finish date cannot be earlier than the start date."))

    @api.onchange('name')
    def _onchange_name(self):
        if self.name!=False:
            # Cal controlar que no sigui buit (quan es dona d'alta o modifica deixant-lo buit
            # ja que no es pot aplicar upper() sobre un "buit" (en realitat "False")
            self.name = self.name.title() #ho posa tot en majúscula?

    @api.depends('name', 'course_id')
    def _compute_display_name(self):
        for edition in self:
            if edition.name and edition.course_id:
                edition.display_name = edition.course_id.name + " - " + edition.name
            else:
                edition.display_name = " - "

    #Exercici de matrícula
    def _compute_n_teachers(self):
        for edition in self:
            #Fem un SEARCH (No search_count)
            teachings = self.env['school.teaching'].search([('edition_id', '=', edition.id)])
            teachers = []
            #Fem un recorregut per la llista teachings mirant si el teacher ja esta a teachers
            for t in teachings:
                if t.teacher_id not in teachers:
                    teachers.append(t.teacher_id)
            edition.n_teachers = len(teachers)




class SchoolThematic(models.Model):
    _name = 'school.thematic'
    _description = 'Thematic Management'
    _order = 'name'

    name = fields.Char('Name', size=60, required=True, translate=True)    
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


class Teaching(models.Model):
    _name = 'school.teaching'
    _description = 'Teaching Management'

    teacher_id = fields.Many2one('school.teacher', string="Teacher", required=True)
    edition_id = fields.Many2one('school.course.edition', string="Edition", required=True)
    subject_id = fields.Many2one('school.subject', string="Subject", required=True)

    # Related fields per a utilitzar en les views:
    course_edition_course_id = fields.Many2one('school.course', string="Course", related="edition_id.course_id")
    #subject_teacher_ids = fields.Many2one('school.teacher', string="Course Manager", related="edition_id.course_id.manager_id") # retorna el Professor Responsable del curs.
    subject_teacher_ids = fields.Many2many('school.teacher',related='subject_id.teacher_id', string="Authorized Teachers")  #llista de professors que saben fer l'assignatura
    
