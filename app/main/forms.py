from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, MultipleFileField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Length


class ListingForm(FlaskForm):
    category = SelectField(u'Category', choices=[('none', 'Select Your Listing Category...'), ('Phones', 'Phones'), ('Laptops & Computers', 'Laptops & Computers'),
    ('Appliances', 'Appliances'), ('Video Games', 'Video Games'), ('Books', 'Books'), ('Other', 'Other')])
    list_title = TextAreaField('Listing Title', validators=[Length(min=0, max=140), DataRequired()])
    description = TextAreaField('Your Listing Description', validators=[DataRequired()])
    item_name = StringField('Item Name or Model', validators=[DataRequired()])
    currency = SelectField(u'Currency', choices=[('none', 'Select Currency...'), ('Ksh.', 'Ksh'), ('USD.', 'USD')])
    item_price = IntegerField('Item Price', validators=[DataRequired()])
    inputFile= MultipleFileField('Upload Image(s)', render_kw={'multiple': True}, validators=[DataRequired()] )
    submit = SubmitField('List')

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')