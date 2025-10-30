#!/usr/bin/env python3
"""
Deploy All Metadata Forms
Deploys all md01-md37 metadata forms (excluding already deployed MD25/MD27 polymorphic forms)
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import utils
from joget_client import JogetClient
from processors.master_data_deployer import MasterDataDeployer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('deploy_all_metadata')

print("=" * 80)
print("DEPLOYING ALL METADATA FORMS")
print("=" * 80)
print()

# Load configs
deploy_config = utils.load_config('config/master_data_deploy.yaml')
joget_config = utils.load_config('config/joget.yaml')

# Merge configs
deploy_config['metadata'] = joget_config.get('metadata', {})
deploy_config['subcategory_mappings'] = joget_config.get('subcategory_mappings', {})

# Initialize client
base_url = deploy_config['deployment']['base_url']
api_key = deploy_config['deployment']['form_creator_api_key']
client = JogetClient(base_url=base_url + '/form', api_key=api_key, debug=False)

# Initialize deployer
deployer = MasterDataDeployer(config=deploy_config, logger=logger)

# Database config
import os
from dotenv import load_dotenv

env_file = Path('config/../.env.3')
if env_file.exists():
    load_dotenv(env_file, override=True)

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3308)),
    'database': os.getenv('DB_NAME', 'jwdb'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Forms to deploy - ALL metadata forms except already deployed polymorphic ones
# Exclude: md25equipCategory, md25equipment, md27inputCategory, md27input (already deployed)
# Exclude: old archived child forms (md25generalTools, md27fertilizer, etc.)
forms_to_deploy = [
    # MD01-MD20: Basic metadata
    'md01maritalStatus',
    'md02language',
    'md03district',
    'md04agroEcologicalZone',
    'md05residencyType',
    'md06farmLabourSource',
    'md07livelihoodSource',
    'md08educationLevel',
    'md09infoSource',
    'md10conservationPractice',
    'md11hazard',
    'md12relationship',
    'md13orphanhoodStatus',
    'md14disabilityStatus',
    'md15areaUnits',
    'md16livestockType',
    'md17incomeSource',
    'md18registrationChannel',
    'md19crops',
    'md20supportProgram',

    # MD21-MD24: Program metadata
    'md21programType',
    'md22applicationStatus',
    'md23documentType',
    'md24paymentMethod',

    # MD26, MD28, MD30-MD37: Additional metadata
    'md26trainingTopic',
    'md28benefitModel',
    'md30targetGroup',
    'md31decisionType',
    'md32rejectionReason',
    'md33requestType',
    'md34notificationType',
    'md35foodSecurityStatus',
    'md36eligibilityOperator',
    'md37collectionPoint',
]

print(f"Forms to deploy: {len(forms_to_deploy)}")
print()

results = []

for form_id in forms_to_deploy:
    csv_file = Path(f'data/metadata/{form_id}.csv')
    json_file = Path(f'data/metadata_forms/{form_id}.json')

    print(f"\n{'=' * 80}")
    print(f"Deploying: {form_id}")
    print('=' * 80)

    # Check files exist
    if not csv_file.exists():
        print(f"  ✗ CSV not found: {csv_file}")
        results.append({'form': form_id, 'success': False, 'error': 'CSV not found'})
        continue

    if not json_file.exists():
        print(f"  ✗ JSON not found: {json_file}")
        results.append({'form': form_id, 'success': False, 'error': 'JSON not found'})
        continue

    try:
        # Extract metadata
        form_metadata = deployer.extract_form_metadata(json_file)

        # Create form
        print("  Creating form...")
        result = deployer.create_form(client, form_metadata)

        if not result['success']:
            print(f"  ✗ Form creation failed: {result.get('error')}")
            results.append({'form': form_id, 'success': False, 'error': result.get('error')})
            continue

        # Get API ID
        print("  Querying API ID...")
        api_name = f"api_{form_metadata['form_id']}"
        api_id = client.get_api_id_for_form(
            app_id=deploy_config['target_application']['app_id'],
            app_version=deploy_config['target_application']['app_version'],
            api_name=api_name,
            db_config=db_config
        )

        if not api_id:
            print(f"  ✗ API ID not found")
            results.append({'form': form_id, 'success': False, 'error': 'API ID not found'})
            continue

        form_metadata['api_id'] = api_id

        # Populate data
        print("  Populating data...")
        result = deployer.populate_form_data(client, form_metadata, csv_file)

        if result['success']:
            print(f"  ✓ Success! {result['records_posted']} records")
            results.append({'form': form_id, 'success': True, 'records': result['records_posted']})
        else:
            print(f"  ✗ Data population failed: {result.get('error')}")
            results.append({'form': form_id, 'success': False, 'error': result.get('error')})

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        results.append({'form': form_id, 'success': False, 'error': str(e)})

# Summary
print(f"\n{'=' * 80}")
print("DEPLOYMENT SUMMARY")
print('=' * 80)
print()

successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"Total forms: {len(results)}")
print(f"Successful:  {len(successful)}")
print(f"Failed:      {len(failed)}")
print()

if successful:
    print("✓ Successful deployments:")
    for r in successful:
        print(f"  - {r['form']} ({r['records']} records)")
    print()

if failed:
    print("✗ Failed deployments:")
    for r in failed:
        print(f"  - {r['form']}: {r['error']}")
    print()

print("=" * 80)
print("COMPLETE METADATA STATUS")
print("=" * 80)
print(f"Total metadata forms deployed: {len(successful) + 4}")  # +4 for MD25/MD27
print(f"  - Basic metadata (md01-md24, md26, md28, md30-md37): {len(successful)}")
print(f"  - Polymorphic forms (md25, md27): 4 (already deployed)")
print("=" * 80)

if failed:
    sys.exit(1)
