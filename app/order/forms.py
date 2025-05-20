from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class AddToCartForm(FlaskForm):
    """Form for adding an item to the shopping cart."""
    # Remove item_id - we get it directly from request.form now
    # item_id = HiddenField('Item ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', default=1, validators=[
        DataRequired(),
        NumberRange(min=1, message='Quantity must be at least 1.')
    ])
    submit = SubmitField('Add to Cart')
