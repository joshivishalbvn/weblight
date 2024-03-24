
import random
from functools import reduce
from django.db.models import Q

def create_otp():
    otp = random.randint(100000, 999999)
    return otp

DEFAULT_FILTER_PARAMS_LIST=[
        'email',
        'first_name',
        'last_name',
        'phone_number',
]


def get_lead_filter_params( params):
    filters = Q()
    for key, _value in params.items():
        if key in DEFAULT_FILTER_PARAMS_LIST:
            val = params.getlist(key)
            if key == "first_name":
                filters &= reduce(lambda x, y: x | y, [Q(first_name__icontains=word) for word in val])

            if key == "last_name":
                filters &= reduce(lambda x, y: x | y, [Q(last_name__icontains=word) for word in val])

            if key == "email":
                filters &= reduce(lambda x, y: x | y, [Q(email__iexact=word) for word in val])

            if key == "phone_number":
                filters &= reduce(lambda x, y: x | y, [Q(phone_number__iexact=word) for word in val])

    print('\033[91m'+'filters: ' + '\033[92m', filters)
    return filters