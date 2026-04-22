from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError

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


