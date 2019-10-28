import argparse, json, secrets, re, webbrowser
import boto3, requests
from  machina import database

SCHEMA_URL = 'http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd'
QUESTION_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
                            <ExternalQuestion xmlns="{schema_url}">
                            <ExternalURL>{external_url}</ExternalURL>
                            <FrameHeight>{frame_height}</FrameHeight>
                        </ExternalQuestion>'''
                    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a HIT on MTurk')
    parser.add_argument('host', type=str, help='Hostname of deployed application for HIT')
    parser.add_argument('-c', '--config', required=True, type=str, help='Path to config file.')
    parser.add_argument('--consent', action="store_true", help='Prepend HIT with consent form')
    parser.add_argument('--preview', action="store_true", help='Open preview of HIT')
    parser.add_argument('--sandbox', action="store_true", help='Create HIT on the sandbox rather than the main MTurk site')
    parser.add_argument('-n', '--n_assignments', type=int, default=100, help='Number of assignments to create the HIT with.')
    parser.add_argument('-l', '--lifetime', type=int, default=172800, help='Lifetime (in seconds) of HIT')
    parser.add_argument('-d', '--duration', type=int, default=3600, help='Duration (in seconds) of a single assignment')
    parser.add_argument('-a', '--approval_delay', type=int, default=86400, help='Approval delay (in seconds) for the  HIT')

    args = parser.parse_args()
    
    with open(args.config, "r") as f:
        config = json.load(f)

    API_ENDPOINT = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com' if args.sandbox else 'https://mturk-requester.us-east-1.amazonaws.com' 
    token = secrets.token_urlsafe()
    hit_url = f"https://{args.host}/instructions?token={token}"
    
    print(f"Submitting {'[consented]' if args.consent else ''} HIT to {API_ENDPOINT} with config ({args.config})\n\n")
    print(f"\tTITLE: {config['title']}")
    print(f"\tDESCRIPTION: {config['description']}\n")
    
    print(f"\tKEYWORDS: {config['keywords']}")
    print(f"\tREWARD: {config['reward']}")
    print(f"\tASSIGNMENTS: {args.n_assignments}")
    print(f"\tLIFETIME: {args.lifetime}")
    print(f"\tDURATION: {args.duration}")
    print(f"\tAPPROVAL DELAY: {args.approval_delay}")
    print(f"\tTOKEN: {token}\n\n")
    
    if args.consent:
        r = requests.post("http://codingthecrowd.com/mturk/setup.php", data={"url": hit_url})
        hit_url = re.search(r"<h1>(.+?)\n</h1>", r.text).group(1).strip()
 
    question = QUESTION_TEMPLATE.format(schema_url=SCHEMA_URL, external_url=hit_url, frame_height=0)
                                        
    mturk = boto3.client('mturk', region_name="us-east-1", endpoint_url=API_ENDPOINT)
    
    hit = mturk.create_hit(
        Title = config['title'],
        Description = config['description'],
        Keywords = config['keywords'],
        Reward = config['reward'],
        MaxAssignments = args.n_assignments,
        LifetimeInSeconds = args.lifetime,
        AssignmentDurationInSeconds = args.duration,
        AutoApprovalDelayInSeconds = args.approval_delay,
        Question = question,
        QualificationRequirements=config['qualifications'] if not args.sandbox else [],
        UniqueRequestToken=secrets.token_urlsafe()
    )
    preview_url = 'https://workersandbox.mturk.com/mturk/preview?groupId=' if args.sandbox else 'https://mturk.com/mturk/preview?groupId=' 
    
    print(f"\tHIT {hit['HIT']['HITId']} created at {hit_url}")
    print(f"\tPreview HIT at: {preview_url}{hit['HIT']['HITGroupId']}") 

    if args.sandbox and args.preview:
        webbrowser.open(f"{preview_url}{hit['HIT']['HITGroupId']}")