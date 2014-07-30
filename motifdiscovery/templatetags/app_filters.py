from django import template
import numpy as np

register = template.Library()

@register.filter(name='isEven')
def isEven(value):
    if np.mod(value, 2) == 0:
        return True
    else:
        return False

@register.filter(name='roundOff')
def roundOff(value):
    return np.round(value, decimals=1)

@register.filter(name='lookup')
def lookup(d, key):
    return d[key]

@register.filter(name='getId')
def getId(d):
    return d.id

@register.filter(name='getStr')
def getStr(d):
    return d.start_time

@register.filter(name='getEnd')
def getEnd(d):
    return d.end_time
