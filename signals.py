from django.dispatch import Signal
context_signal = Signal(providing_args=['request', 'context'])

