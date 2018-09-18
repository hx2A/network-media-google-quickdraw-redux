import decimal
import string


def remove_decimals(val):
    """convert all Decimal objects to ints

    boto3's dynamodb queries return json-like objects with all numbers as
    instances of decimal.Decimal. This recursively converts them to ints
    faster than a json serialization class could.
    """
    if isinstance(val, decimal.Decimal):
        return int(val)
    elif isinstance(val, dict):
        return {k: remove_decimals(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [remove_decimals(v) for v in val]
    else:
        return val


def validate_p_id(p_id):
    """validate a p_id to make sure there is no malicious code

    make sure the p_id value contains a limited set of characters that cannot
    be code.
    """
    return (str(p_id) and
            not set(str(p_id)).
            difference(string.ascii_lowercase).
            difference('|_'))


def validate_s_id(s_id):
    """validate a s_id to make sure there is no malicious code

    make sure the s_id value contains a limited set of characters that cannot
    be code.
    """
    return str(s_id) and not set(str(s_id)).difference(string.digits)
