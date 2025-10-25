#!/usr/bin/env python3
"""
Deploy Polymorphic Forms: md25equipment, md27input
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
logger = logging.getLogger('deploy_polymorphic')

print("=" * 80)
print("DEPLOYING POLYMORPHIC FORMS: md25equipment, md27input")
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

# Forms to deploy
forms = [
    {
        'form_id': 'md25equipment',
        'csv_file': 'data/metadata/md25equipment.csv',
        'json_file': 'data/metadata_forms/md25equipment.json'
    },
    {
        'form_id': 'md27input',
        'csv_file': 'data/metadata/md27input.csv',
        'json_file': 'data/metadata_forms/md27input.json'
    }
]

results = []

for form_spec in forms:
    form_id = form_spec['form_id']
    csv_file = Path(form_spec['csv_file'])
    json_output = Path(form_spec['json_file'])

    print(f"\n{'=' * 80}")
    print(f"Deploying: {form_id}")
    print('=' * 80)

    if not csv_file.exists():
        print(f"✗ CSV not found: {csv_file}")
        results.append({'form': form_id, 'success': False, 'error': 'CSV not found'})
        continue

    if not json_output.exists():
        print(f"✗ JSON not found: {json_output}")
        results.append({'form': form_id, 'success': False, 'error': 'JSON not found'})
        continue

    try:
        # Extract metadata
        form_metadata = deployer.extract_form_metadata(json_output)

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

if failed:
    sys.exit(1)
