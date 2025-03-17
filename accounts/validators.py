from django.core.exceptions import ValidationError

def validate_phone(value):
    if len(str(value)) != 10:
        raise ValidationError("Phone number must be exactly 10 digits.")
    if not str(value).isdigit():
        raise ValidationError("Phone number must contain only digits.")

def validate_pincode(value):
    if len(str(value)) !=6:
        raise ValidationError("Pincode must be exactly 6 digits")
    if not str(value).isdigit():
        raise ValidationError("Pincode must contain only digits")