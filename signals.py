from django.dispatch import Signal

#expect no return value
context_signal = Signal(providing_args=['request', 'context'])

#callback *could* return a new http response object
post_signal = Signal(providing_args=['request', 'form', 'extra'])

def last_response(responses, allow_none=False):
    """ get the last existing response value from responses of a signal """
    try:
        if allow_none:
            return responses[-1][1]
        else:
            return [response for response in responses if response[1] is not None][-1][1]
    except:
        return None
