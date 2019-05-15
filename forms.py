from wtforms import Form, StringField, SubmitField, PasswordField, TextAreaField, BooleanField, validators

# Register form
class RegForm(Form):
    username = StringField("Username", [validators.Length(min=1, max=20)])
    password = PasswordField("Password", [validators.Length(min=1, max=20)])
    email = StringField("Email", [validators.Length(min=1, max=20)])
    firstName = StringField("First Name", [validators.Length(min=1, max=20)])
    lastName = StringField("Last Name", [validators.Length(min=1, max=20)])

# Document form
class DocForm(Form):
    title = StringField("Title", [validators.Length(min=1, max=100)])
    content = TextAreaField("Content", [validators.Length(min=1)])
    is_private = BooleanField()