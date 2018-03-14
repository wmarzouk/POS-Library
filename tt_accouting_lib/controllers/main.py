
import base64

from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import binary_content
from odoo.http import request, STATIC_CACHE, content_disposition


class account_report_controller(http.Controller):


    @http.route('/account_report_excel/print', type='http', auth='public', website=True)
    # def print_execel(self, filename,model_name,model_curr_id):
    def print_execel(self, **kwargs):
        model_name = kwargs['model_name']
        model_curr_id = kwargs['model_curr_id']
        filename = kwargs['filename']
        mod_obj = request.env[model_name].with_context(request.env.context).search([('id','=',int(model_curr_id))])
        if 'act_mod_name' in kwargs:
            file_content = mod_obj.create_excel_data(act_mod_name=kwargs['act_mod_name'],act_ids=kwargs['act_ids'])
        else:
            file_content = mod_obj.create_excel_data()
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return request.make_response(file_content,
                                     headers=[('Content-Type', mimetype),
                                     ('Content-Disposition', content_disposition(filename))
                                      ,('Content-Length', len(file_content))
                                      , ('follow_redirects','False')
                                     ])



