#!/usr/bin/env python3
"""
Retry the 3 failed forms: md19crops, md27inputCategory, md30targetGroup
"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import utils
from joget_client import JogetClient
from processors.master_data_deployer import MasterDataDeployer
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('retry')

print("=" * 80)
print("RETRYING 3 FAILED FORMS")
print("=" * 80)
print()

# Load configs
deploy_config = utils.load_config('config/master_data_deploy.yaml')
joget_config = utils.load_config('config/joget.yaml')
deploy_config['metadata'] = joget_config.get('metadata', {})

# Initialize client
base_url = deploy_config['deployment']['base_url']
api_key = deploy_config['deployment']['form_creator_api_key']
client = JogetClient(base_url=base_url + '/form', api_key=api_key, debug=True)

# Load .env
env_file = Path('.env.3')
load_dotenv(env_file, override=True)

db_config = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3308)),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Initialize deployer
deployer = MasterDataDeployer(config=deploy_config, logger=logger)

# Forms to retry
failed_forms = [
    'md19crops',
    'md27inputCategory',
    'md30targetGroup',
]

for form_id in failed_forms:
    print(f"\n{'=' * 80}")
    print(f"Retrying: {form_id}")
    print('=' * 80)

    json_file = Path(f'data/metadata_forms/{form_id}.json')
    csv_file = Path(f'data/metadata/{form_id}.csv')

    # Extract metadata
    form_metadata = deployer.extract_form_metadata(json_file)

    # Get API ID from database
    api_name = f"api_{form_metadata['form_id']}"
    api_id = client.get_api_id_for_form(
        app_id=deploy_config['target_application']['app_id'],
        app_version=deploy_config['target_application']['app_version'],
        api_name=api_name,
        db_config=db_config
    )

    if not api_id:
        print(f"✗ API ID not found for {form_id}")
        continue

    print(f"✓ Found API ID: {api_id}")
    form_metadata['api_id'] = api_id

    # Populate data with full debug logging
    print(f"Populating data from: {csv_file}")
    result = deployer.populate_form_data(client, form_metadata, csv_file)

    print(f"\nResult: {result}")
    print()
