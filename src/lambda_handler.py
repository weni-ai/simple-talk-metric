#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''\
AWS Lambda handler example application.
'''

import sys
import typing

from aws_lambda_typing.context import Context  # pylint: disable=import-error
from aws_lambda_typing.events import S3Event  # pylint: disable=import-error

from get_parameter import get_parameter


def lambda_handler(
		event: S3Event, # pylint: disable=unused-argument
		context: Context # pylint: disable=unused-argument
) -> typing.Dict[str, typing.Any]:
	'''\
	Implement example function to test the AWS Lambda handler.

	This function exist only for tests presupposes, some code here is
	used only as examples.
	'''
	### Load Parameter Store values from extension
	parameter_value=get_parameter(
		'SuperSecret'
	)
	print(f'Found config values: {parameter_value}')

	return {
		'statusCode': 200,
		'message': f'Hello from AWS Lambda using Python {sys.version}!!! {parameter_value}',
	}

def another_lambda_handler(
		event: S3Event, # pylint: disable=unused-argument
		context: Context # pylint: disable=unused-argument
) -> typing.Dict[str, typing.Any]:
	'''\
	Implement another example function lambda handler to test.

	This function exist only for tests presupposes, some code here is
	used only as examples. This is a test for another lambda handler in the
	same image.
	'''
	return {
		'statusCode': 200,
		'message': f'another_lambda_handler using Python {sys.version}!!!',
	}

# vim: nu ts=4 fdm=indent noet ft=python:
