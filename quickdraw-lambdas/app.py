from chalice import Chalice, CORSConfig, CognitoUserPoolAuthorizer
import boto3

from chalicelib import util


app = Chalice(app_name='quickdraw-lambdas')

cors_config = CORSConfig(
    allow_origin='https://quickdraw.ixora.io',
)

authorizer = CognitoUserPoolAuthorizer(
    'GoogleQuickdraw',
    header='Authorization',
    provider_arns=[('arn:aws:cognito-idp:us-east-1:386512717651:'
                    'userpool/us-east-1_7OESlcisr')])


dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
)

table = dynamodb.Table('GoogleQuickdraw')


@app.route('/drawings/{country}/{category}/{recognized}', cors=cors_config)
def get_drawings(country, category, recognized):
    """return all of the drawings for a country and category

    the country and category codes join together to form a compound partition
    key. the database is designed to return all of the sketches in a single
    partition, making this process more efficient. some filtering can be done
    for recognized or unrecognized drawings.
    """
    p_id = '|'.join([country, category])

    if not util.validate_p_id(p_id):
        return {'response': 'invalid input'}

    query_args = {}
    expression_values = {}

    query_args['KeyConditionExpression'] = 'p_id = :p_id'
    query_args['FilterExpression'] = ('attribute_not_exists(f) '
                                      'and attribute_not_exists(i)')
    expression_values[':p_id'] = p_id

    if recognized != 'all':
        query_args['FilterExpression'] += " and r = :r"
        expression_values[':r'] = recognized == 'yes'

    query_args['ExpressionAttributeValues'] = expression_values

    try:
        response = table.query(**query_args)
        response = util.remove_decimals(response['Items'])

        return {'response': 'success', 'data': response}
    except Exception as e:
        return {'response': 'error'}


def _admin_query(min_s_id, index_name, flag_char):
    "generic function for executing the admin queries"
    if not util.validate_s_id(min_s_id):
        return {'response': 'invalid input'}

    try:
        response = table.query(
            IndexName=index_name,
            KeyConditionExpression=f'{flag_char} = :val1 and s_id > :s_id',
            ExpressionAttributeValues={
                ':val1': 1,
                ':s_id': int(min_s_id)
            },
            Limit=50
        )

        response = util.remove_decimals(response['Items'])

        return {'response': 'success', 'data': response}
    except Exception as e:
        return {'response': 'error'}


@app.route('/flagged/{min_s_id}',
           cors=cors_config, authorizer=authorizer)
def get_flagged_drawings(min_s_id):
    "get flagged drawings for admin screen"
    return _admin_query(min_s_id, 'GoogleQuickdrawFlagged', 'f')


@app.route('/inappropriate/{min_s_id}',
           cors=cors_config, authorizer=authorizer)
def get_inappropriate_drawings(min_s_id):
    "get inappropriate drawings for admin screen"
    return _admin_query(min_s_id, 'GoogleQuickdrawInappropriate', 'i')


def _update_flags(params, update_expression, include_values=True):
    "generic function for updating a sketches' flags"
    p_id = params.get('p_id')
    s_id = params.get('s_id')

    if not util.validate_p_id(p_id) or not util.validate_s_id(s_id):
        return {'response': 'invalid input'}

    update_args = {}
    update_args['Key'] = {
        'p_id': p_id,
        's_id': s_id
    }
    update_args['UpdateExpression'] = update_expression
    if include_values:
        update_args['ExpressionAttributeValues'] = {
            ':val1': 1
        }

    try:
        table.update_item(**update_args)
        return {'response': 'success'}
    except Exception as e:
        return {'response': 'error'}


@app.route('/flag', methods=['POST', 'PUT'], cors=cors_config)
def flag_drawing():
    "flag a sketch as unacceptable"
    params = app.current_request.json_body
    return _update_flags(params, 'SET f = :val1')


@app.route('/unflag', methods=['POST', 'PUT'],
           cors=cors_config, authorizer=authorizer)
def unflag_drawing():
    "remove a flag to mark a sketch as acceptable"
    params = app.current_request.json_body
    return _update_flags(params, 'REMOVE f', include_values=False)


@app.route('/censor', methods=['POST', 'PUT'],
           cors=cors_config, authorizer=authorizer)
def mark_inappropriate():
    "mark a sketch as inappropriate"
    params = app.current_request.json_body
    return _update_flags(params, 'SET i = :val1 REMOVE f')


@app.route('/authenticated', methods=['GET'],
           cors=cors_config, authorizer=authorizer)
def authenticated():
    "used on admin page to test if user is authenticated"
    return {'response': True}
