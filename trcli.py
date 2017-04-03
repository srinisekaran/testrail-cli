import click
import getpass
from testrail import *
import json

### Configuration

with open('config.json') as config:
	user = json.load(config)

if not user['CLIENT_DOMAIN'] or not user['USERNAME']:
	user['CLIENT_DOMAIN'] = raw_input('Domain URL: ')
	user['USERNAME'] = raw_input('Username: ')
	with open('config.json', 'w') as outfile:
		json.dump(user, outfile)


client = APIClient(user['CLIENT_DOMAIN'])
client.user = user['USERNAME']

if not user['PASSWORD']:
	user['PASSWORD'] = getpass.getpass('Password: ')
	with open('config.json', 'w') as outfile:
		json.dump(user, outfile)

client.password = user['PASSWORD']




### CLI Main 

@click.group()
def cli():
	'''
	TestRail CLI\n
	Srinivaas Sekaran | 2017
	'''
	pass


### Usability: Status ID to Significance Mapping

# Status ID for Corresponding Result 
status_dict = {
	1: 	'Passed',
	2:	'Blocked',
	3:	'Untested',
	4:	'Retest',
	5:	'Failed'
}

def status_id_to_text(status_id):
	return status_dict[status_id]

# Inverse Status ID dictionary for reverse functionality
def text_to_status_id(result_text):
	reverse_dict = dict((text, status) for status, text in status_dict.iteritems())
	return reverse_dict[result_text]

def get_user_from_id(user_id):
	user_info = client.send_get('get_user/' + str(user_id))
	return user_info['name']




### GET Commands: Retrive Tests, Runs 

@cli.command()
@click.argument('test_number')
def get_test(test_number):
	'''Retrieve basic details of a unique test'''
	test = client.send_get('get_test/' + test_number)
	click.echo('*** ' + test['title'] + ' ***')
	status = status_id_to_text(test['status_id'])
	click.echo('>> ' + status)
	assigned = get_user_from_id(test['assignedto_id'])
	click.echo('Assignee: ' + assigned)
	click.echo('Case ID: ' + str(test['case_id']))
	click.echo('Run ID: ' + str(test['run_id']))

@cli.command()
@click.argument('test_run_id')
def get_run_status(test_run_id):
	'''Get stats on a test run'''
	run = client.send_get('get_run/' + test_run_id)
	click.echo(run['name'] + '(' + run['url'] + ')')
	click.echo('Passing: ' + str(run['passed_count']))
	click.echo('Failing: ' + str(run['failed_count']))
	click.echo('To Retest: ' + str(run['retest_count']))
	click.echo('Untested: ' + str(run['untested_count']))
	click.echo('Blocked: ' + str(run['blocked_count']))

@cli.command()
@click.argument('test_run_id')
def get_tests(test_run_id):
	'''Retrieve information of all tests for a run'''
	tests_data = client.send_get('get_tests/' + test_run_id)
	titles = []
	status = []
	assigned = []
	for test in tests_data:
		titles.append((test['title']) + ' (' + str(test['id']) + ') ')
		status.append((test['status_id']))
		assigned.append((test['assignedto_id']))
	for i in range(len(titles)):
		click.echo('***' + titles[i] + '***')
		status_result = status_id_to_text(status[i])
		user_result =  get_user_from_id(assigned[i])
		click.echo(status_result + ', ' + user_result)
		
@cli.command()
@click.argument('case_id')
def get_case(case_id):
	'''Retrieve a test case'''
	case_data = client.send_get('get_case/' + case_id)
	click.echo('***' + case_data['title'] + '***')
	click.echo('Created by: ' + get_user_from_id(case_data['created_by']))
	click.echo('Steps: \n')
	click.echo(case_data['custom_steps'])




### POST Commands: Update Tests, Runs
 
@cli.command()
@click.argument('test_number')
@click.argument('test_result')
@click.option('--comment', help='Optional comment.')
@click.option('--version', help='Version number.')
def set_test_result(test_number, test_result, comment, version):
	'''Mark a test with a result --comment --version'''
	status = text_to_status_id(test_result)
	result = client.send_post(
		'add_result/' + test_number,
		{ 'status_id': status, 'comment': comment, 'version': version }
	)
	click.echo(result)





if __name__ == '__main__':
    cli()
