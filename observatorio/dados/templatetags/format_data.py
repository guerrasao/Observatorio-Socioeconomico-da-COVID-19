from django import template
from decimal import Decimal
register = template.Library()

@register.filter
def no_zero(value, unidade):
    if value != '-':
        if unidade == "DECI":
            value = float(value)
        elif unidade == "PORC":
            value = float(value)
        elif unidade == "REAL" or unidade == "DOLA" or unidade == "EURO":
            value = Decimal("{:.2f}".format(value))
    return value

@register.filter
def insert_unit(value, unidade):
    if value != '-':
        if unidade == "PORC":
            value = str(value+"%")
        elif unidade == "REAL":
            value = str("R$"+value)
        elif unidade == "DOLA":
            value = str("$"+value)
        elif unidade == "EURO":
            value = str("€"+value)
    return value