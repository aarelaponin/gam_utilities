"""
Main CLI for joget-dx-toolkit.

Provides commands for:
- Parsing input formats to canonical YAML
- Building platform-specific forms from canonical
- Deploying forms to Joget server
- End-to-end workflows
"""

import click
import logging
import sys
from pathlib import Path
from typing import Optional

from joget_toolkit.parsers import MarkdownParser, CSVParser, YAMLParser
from joget_toolkit.builders import JogetBuilder
from joget_toolkit.deployers import JogetDeployer
from joget_toolkit.specs.validator import SpecValidator


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger('joget_toolkit')


@click.group()
@click.version_option(version='0.1.0', prog_name='joget-dx-toolkit')
def cli():
    """
    Joget DX Toolkit - Developer tools for Joget DX platform.

    \b
    Workflow:
    1. Parse specification to canonical YAML: joget-dx parse markdown spec.md
    2. Build Joget forms: joget-dx build joget spec.yaml -o forms/
    3. Deploy to server: joget-dx deploy forms/*.json --app-id myApp

    \b
    Or use all-in-one command:
    joget-dx deploy --from-md spec.md --app-id myApp --server http://localhost:8080
    """
    pass


# ============================================================================
# PARSE Commands
# ============================================================================

@cli.group()
def parse():
    """Parse input formats to canonical YAML."""
    pass


@parse.command('markdown')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_file', type=click.Path(),
              help='Output YAML file (default: <input>.yaml)')
@click.option('--app-id', help='Override application ID from markdown')
@click.option('--app-name', help='Override application name from markdown')
def parse_markdown(input_file, output_file, app_id, app_name):
    """
    Parse markdown specification to canonical YAML.

    \b
    Example:
        joget-dx parse markdown form_specs.md -o specs/myapp.yaml
    """
    try:
        click.echo(f"Parsing markdown: {input_file}")

        # Parse markdown
        parser = MarkdownParser()
        app_spec = parser.parse(input_file, app_id=app_id, app_name=app_name)

        # Determine output file
        if not output_file:
            output_file = Path(input_file).with_suffix('.yaml')

        # Save as YAML
        SpecValidator.save_yaml(app_spec, output_file)

        click.echo(f"✓ Created: {output_file}")
        click.echo(f"  App: {app_spec.metadata.app_name}")
        click.echo(f"  Forms: {len(app_spec.forms)}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@parse.command('csv')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_file', type=click.Path(), required=True,
              help='Output YAML file')
@click.option('--app-id', required=True, help='Application ID')
@click.option('--form-id', help='Form ID (default: filename)')
def parse_csv(input_file, output_file, app_id, form_id):
    """
    Parse CSV to canonical YAML.

    \b
    Example:
        joget-dx parse csv metadata.csv -o specs/metadata.yaml --app-id myApp
    """
    try:
        click.echo(f"Parsing CSV: {input_file}")

        # Parse CSV
        parser = CSVParser()
        app_spec = parser.parse(input_file, app_id=app_id, form_id=form_id)

        # Save as YAML
        SpecValidator.save_yaml(app_spec, output_file)

        click.echo(f"✓ Created: {output_file}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# BUILD Commands
# ============================================================================

@cli.group()
def build():
    """Build platform-specific forms from canonical YAML."""
    pass


@build.command('joget')
@click.argument('spec_file', type=click.Path(exists=True))
@click.option('-o', '--output', 'output_dir', type=click.Path(),
              default='./forms', help='Output directory for JSON files')
@click.option('--overwrite', is_flag=True, help='Overwrite existing files')
def build_joget(spec_file, output_dir, overwrite):
    """
    Build Joget form JSONs from canonical specification.

    \b
    Example:
        joget-dx build joget specs/myapp.yaml -o forms/
    """
    try:
        click.echo(f"Building Joget forms from: {spec_file}")

        # Load and validate spec
        app_spec = SpecValidator.validate_yaml(spec_file)

        # Build forms
        builder = JogetBuilder(logger=logger)
        results = builder.build(app_spec, output_dir, overwrite=overwrite)

        # Show results
        if results['forms_created']:
            click.echo(f"\n✓ Created {len(results['forms_created'])} forms:")
            for form_file in results['forms_created']:
                click.echo(f"  - {form_file}")

        if results['forms_skipped']:
            click.echo(f"\n⊘ Skipped {len(results['forms_skipped'])} existing forms (use --overwrite)")

        if results['errors']:
            click.echo(f"\n✗ Errors:")
            for error in results['errors']:
                click.echo(f"  - {error}", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# DEPLOY Commands
# ============================================================================

@cli.command()
@click.option('--from-md', 'markdown_file', type=click.Path(exists=True),
              help='Deploy directly from markdown specification')
@click.option('--from-yaml', 'yaml_file', type=click.Path(exists=True),
              help='Deploy from canonical YAML specification')
@click.argument('form_files', nargs=-1, type=click.Path(exists=True))
@click.option('--app-id', required=True, help='Target application ID')
@click.option('--server', default='http://localhost:8080',
              help='Joget server URL')
@click.option('--api-key', help='API key for authentication')
@click.option('--api-id', help='FormCreator API ID')
@click.option('--no-api', is_flag=True, help='Do not create API endpoint')
@click.option('--no-crud', is_flag=True, help='Do not create CRUD interface')
@click.option('--dry-run', is_flag=True, help='Show what would be deployed without deploying')
def deploy(markdown_file, yaml_file, form_files, app_id, server, api_key, api_id,
          no_api, no_crud, dry_run):
    """
    Deploy forms to Joget server.

    \b
    Examples:
        # Deploy from form JSONs
        joget-dx deploy forms/*.json --app-id myApp --server http://localhost:8080

        # Deploy directly from markdown
        joget-dx deploy --from-md spec.md --app-id myApp --api-key KEY --api-id FORMCREATOR_API

        # Dry run
        joget-dx deploy forms/*.json --app-id myApp --dry-run
    """
    try:
        # Determine source
        if markdown_file:
            click.echo(f"Deploying from markdown: {markdown_file}")
            # Parse markdown → build → deploy
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                # Parse
                parser = MarkdownParser()
                app_spec = parser.parse(markdown_file)

                # Build
                builder = JogetBuilder(logger=logger)
                results = builder.build(app_spec, tmpdir, overwrite=True)

                # Deploy
                form_files = results['forms_created']

        elif yaml_file:
            click.echo(f"Deploying from YAML: {yaml_file}")
            # Build → deploy
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                # Load spec
                app_spec = SpecValidator.validate_yaml(yaml_file)

                # Build
                builder = JogetBuilder(logger=logger)
                results = builder.build(app_spec, tmpdir, overwrite=True)

                # Deploy
                form_files = results['forms_created']

        if not form_files:
            click.echo("✗ No forms to deploy", err=True)
            sys.exit(1)

        click.echo(f"\nDeploying {len(form_files)} forms to: {server}")
        click.echo(f"Target app: {app_id}\n")

        if dry_run:
            click.echo("[DRY RUN] Would deploy:")
            for form_file in form_files:
                click.echo(f"  - {Path(form_file).name}")
            return

        # Check credentials
        if not api_key:
            click.echo("✗ --api-key is required for deployment", err=True)
            sys.exit(1)

        if not api_id:
            click.echo("✗ --api-id is required (FormCreator API ID)", err=True)
            sys.exit(1)

        # Deploy
        deployer = JogetDeployer(server, api_key, api_id, logger=logger)
        results = deployer.deploy_forms(
            form_files,
            app_id=app_id,
            create_api=not no_api,
            create_crud=not no_crud
        )

        # Show results
        if results['successful']:
            click.echo(f"\n✓ Successfully deployed {len(results['successful'])} forms")

        if results['failed']:
            click.echo(f"\n✗ Failed to deploy {len(results['failed'])} forms:")
            for error in results['errors']:
                click.echo(f"  - {error['file']}: {error['error']}", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ============================================================================
# VALIDATE Command
# ============================================================================

@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
def validate(spec_file):
    """
    Validate canonical YAML specification.

    \b
    Example:
        joget-dx validate specs/myapp.yaml
    """
    try:
        click.echo(f"Validating: {spec_file}")

        # Validate
        app_spec = SpecValidator.validate_yaml(spec_file)

        click.echo(f"✓ Valid canonical format")
        click.echo(f"  Version: {app_spec.version}")
        click.echo(f"  App: {app_spec.metadata.app_name} ({app_spec.metadata.app_id})")
        click.echo(f"  Forms: {len(app_spec.forms)}")

        # Show forms
        for form in app_spec.forms:
            click.echo(f"\n  - {form.name} ({form.id})")
            click.echo(f"    Fields: {len(form.fields)}")
            if form.indexes:
                click.echo(f"    Indexes: {len(form.indexes)}")

    except Exception as e:
        click.echo(f"✗ Validation failed: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
