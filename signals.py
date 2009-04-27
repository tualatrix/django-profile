from django.dispatch import Signal

#expect no return value
context_signal = Signal(providing_args=['request', 'context'])

#callback *could* return a new http response object
post_signal = Signal(providing_args=['request', 'form', 'extra'])

def last_response(responses):
    """ get the last response value from responses of a signal """
    try:
        return responses[-1][1]
    except:
        return None
