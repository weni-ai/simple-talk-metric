#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''\
Define function to retrieve values from extension local HTTP server cache.

This module provides and configure a function `get_parameter` that fetches parameters
stored in AWS SSM(System Manager) or Secrets Manager based on the provided
key and type. The function uses an HTTP GET request to a extension how cache the request
to either the SSM Parameters API or Secrets Manager API, depending on whether the
parameter is configured as 'config' or 'secret'. The response from these APIs is
then processed and returned as a string.

The module also includes environment variable handling for AWS Lambda configurations
related to this functionality, ensuring seamless integration within AWS environments.

All environment can be get from external os environment.
'''

import json
import os
from urllib.parse import quote_plus, urlencode

import urllib3

### Load in Lambda environment variables

# Specifies the port used for local communication with AWS Lambda extension(default is 2773).
PARAMETERS_SECRETS_EXTENSION_HTTP_PORT=os.environ.get(
	'PARAMETERS_SECRETS_EXTENSION_HTTP_PORT',
	2773
)
# Defines the prefix for parameter keys in SSM or Secrets Manager(default is empty).
PARAMETER_KEY_PREFIX=os.environ.get(
	'PARAMETER_KEY_PREFIX',
	''
)
# Indicates whether to fetch parameters as 'config' or 'secret'(default is 'config').
PARAMETER_DEFAULT_TYPE=os.environ.get(
	'PARAMETER_DEFAULT_TYPE',
	'config'
)

aws_session_token=os.environ['AWS_SESSION_TOKEN']
http=urllib3.PoolManager()

def get_parameter(
	parameter_key : str,
	parameter_type : str=PARAMETER_DEFAULT_TYPE,
	parameter_decrypt : bool=True,
):
	'''\
	Retrieve parameter from the AWS SSM or Secrets Manager based on the specified key and type.

	This function sends an HTTP GET request to either the SSM Parameters API
	or Secrets Manager API to fetch the parameter value. The endpoint depends
	on whether `parameter_type` is set to 'config' or 'secret'. This function
	use `AWS-Parameters-and-Secrets-Lambda-Extension`.

	:param parameter_key: Key of parameter to be retrieved from AWS.
		This key will be prefixed by `PARAMETER_KEY_PREFIX`.
	:param parameter_type: Specifies if parameter is a SSM('config') or a secret('secret'),
		defaults to PARAMETER_DEFAULT_TYPE.
	:param parameter_decrypt: Specifies if parameter will be decrypt by kms, defaults to `True`
	:raises NotImplementedError: If `parameter_type` is not recognized or not implemented
		('config' or 'secret').
	:return: The value of the retrieved parameter as a string. The return is decoded.
	'''
	url=f'http://localhost:{PARAMETERS_SECRETS_EXTENSION_HTTP_PORT}'
	query_params={}
	if parameter_type=='config':
		query_params['withDecryption']=parameter_decrypt
		query_params['name']=f'{PARAMETER_KEY_PREFIX}{parameter_key}'
		url+=f'/systemsmanager/parameters/get/?{urlencode(query_params, quote_via=quote_plus)}'
	elif parameter_type=='secret':
		query_params['secretId']=f'{PARAMETER_KEY_PREFIX}{parameter_key}'
		url+=f'/secretsmanager/get?{urlencode(query_params, quote_via=quote_plus)}'
	else:
		raise NotImplementedError(f'parameter_type={parameter_type} is not implemented')

	response=http.request(
		'GET',
		url,
		headers={
			'X-Aws-Parameters-Secrets-Token': os.environ.get('AWS_SESSION_TOKEN')
		}
	)

	response=json.loads(response.data)
	if parameter_type=='config':
		response=response['Parameter']['Value']
	elif parameter_type=='secret':
		response=response['SecretString']
		response=json.loads(response)
	else:
		raise NotImplementedError(f'parameter_type={parameter_type} is not implemented')
	return response

# vim: nu ts=4 fdm=indent noet ft=python:
