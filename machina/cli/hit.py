import boto3
from machina.util import colors
import datetime
import ipdb
import xmltodict
import pprint
import json, csv, os


ENDPOINTS = {
    'mturk': 'https://mturk-requester.us-east-1.amazonaws.com',
    'sandbox': 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
}

pp = pprint.PrettyPrinter(indent=4)

def list_hits(target='mturk', max_results=100):
    mturk = boto3.client('mturk', region_name="us-east-1", endpoint_url=ENDPOINTS[target])
    return mturk.list_hits()

def clean_hits(target, auto=False):
    mturk = boto3.client('mturk', region_name="us-east-1", endpoint_url=ENDPOINTS[target])
    
    for item in mturk.list_hits()['HITs']:
        hit_id, hit_status = item['HITId'], item['HITStatus']
 
        if hit_status == 'Assignable':
            if auto:
                print(f"Deleting HIT {hit_id}")
                mturk.update_expiration_for_hit(
                    HITId=hit_id,
                    ExpireAt=datetime.datetime(2018, 1, 1)
                )   
                mturk.delete_hit(HITId=hit_id)
                continue

            res = input(f"Would you like to delete HIT {hit_id}? (Y) for yes, (N) for no.")
            if res == 'Y':
                print(f"Deleting HIT {hit_id}")
                mturk.update_expiration_for_hit(
                    HITId=hit_id,
                    ExpireAt=datetime.datetime(2018, 1, 1)
                )   
                mturk.delete_hit(HITId=hit_id)
        elif hit_status == 'Reviewable':
            print(f"Deleting HIT {hit_id}")   
            mturk.delete_hit(HITId=hit_id) 

def retrieve_assignments(client, hit_id, max_results):
    assignments = []

    response = client.list_assignments_for_hit(HITId=hit_id, MaxResults=max_results)
    assignments += response['Assignments']

    while 'NextToken' in response:
        response = client.list_assignments_for_hit(HITId=hit_id, MaxResults=max_results, NextToken=response['NextToken'])
        assignments += response['Assignments']

    return assignments
    

def review(hit_id, target='mturk', auto_approve=False, max_results=100):
    mturk = boto3.client('mturk', region_name="us-east-1", endpoint_url=ENDPOINTS[target])
    hit_meta = mturk.get_hit(HITId=hit_id)['HIT']

    assignments = retrieve_assignments(mturk, hit_id, max_results)

    submitted = [ a for a in assignments if a['AssignmentStatus'] == 'Submitted' ]
    approved = [ a for a in assignments if a['AssignmentStatus'] == 'Approved' ]
    rejected = [ a for a in assignments if a['AssignmentStatus'] == 'Rejected' ]   

    print(f"{colors.WARNING}{len(submitted)} assignments{colors.END} ready for review. {colors.GREEN}{len(approved)} approved{colors.END} and {colors.RED}{len(rejected)} rejected{colors.END} of {colors.BLUE}{hit_meta['MaxAssignments']} total{colors.END} assignments.")
    
    progress = {
        'approved': 0,
        'rejected': 0
    } 

    for assignment in submitted:
        if auto_approve:
            mturk.approve_assignment(
                AssignmentId=assignment['AssignmentId'],
                RequesterFeedback='Thank you for your participation in the HIT.',
            )
            progress['approved'] += 1
        else:
            res = input("Would you like to approve: (Y) for yes, (N) for no, (<return>) to skip.")
            if res == 'Y':
                msg = input("Feedback message assignment (blank for no message):")
                progress['approved'] += 1
            elif res == 'N':
                msg = input("Feedback message assignment (blank for no message):")
                progress['rejected'] += 1
            elif res == 'enter':
                continue
            else:
                input("Please answer (Y) or (N)")        

    print(f"{colors.GREEN}{progress['approved']} new submissions approved{colors.END}. {colors.RED}{progress['rejected']} new submissions rejected{colors.END}. {colors.BLUE}{len(submitted) - (progress['approved'] + progress['rejected'])} of {hit_meta['MaxAssignments']} total assignments still waiting review.{colors.END}")
    

def fetch(hit_id, dirname='mturk_results', target='mturk', max_results=100):
    mturk = boto3.client('mturk', region_name="us-east-1", endpoint_url=ENDPOINTS[target])

    if os.path.exists(dirname):
        raise FileExistsError(f"{dirname} already exists! Cannot export results...")
    else:
        os.mkdir(dirname)

    print(f"Writing {hit_id} metadata to {dirname}/meta.json.")
    hit_meta = mturk.get_hit(HITId=hit_id)['HIT']
    with open(f"{dirname}/meta.json", 'w') as fh:
        json.dump(hit_meta, fh, default=str)

    print(f"Retrieving Assignments for {hit_id}....")
    assignments = retrieve_assignments(mturk, hit_id, max_results)

    print(f"Writing {len(assignments)} results for {hit_id} to {dirname}/dump.json.")
    with open(f"{dirname}/dump.json", 'w') as fh:
        json.dump(assignments, fh, default=str)

    print(f"Writing {len(assignments)} results for {hit_id} to {dirname}/assignments.csv.")
    with open(f"{dirname}/assignments.csv", 'w', newline='') as f:
        dicts = []
        names = set()

        for assignment in assignments:
            ipdb.set_trace()
            answer = parse_answer(assignment.pop('Answer'))

            names.update(assignment.keys())
            names.update(answer.keys())
            dicts.append({**assignment, **answer})
        
        writer = csv.DictWriter(f, fieldnames=list(names))    
        writer.writeheader()
        writer.writerows(dicts)

def parse_answer(answer):
    xml_doc = xmltodict.parse(answer)

    return { item['QuestionIdentifier']: item['FreeText'] for item in xml_doc['QuestionFormAnswers']['Answer'] }
            


