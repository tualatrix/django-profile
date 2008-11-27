from django.template import Library, Node
from userprofile.forms import RegistrationForm
from django.template.loader import render_to_string
     
register = Library()
     
class RegistationFormNode(Node):
    def render(self, context):
        form = RegistrationForm()
        template = "userprofile/account/includes/registration_form.html"
        data = { 'form': form, }
        return render_to_string(template, data)
    
def registration_form(parser, token):
    return RegistationFormNode()
registration_form = register.tag(registration_form)

