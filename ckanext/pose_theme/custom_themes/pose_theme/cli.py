import click
import traceback  
import ckan.model as model
from ckanext.activity.model import Activity 

from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB


@click.group()
def pose_theme():
    """Commands for the Pose Theme extension."""
    pass


@pose_theme.command(name='cleanup-activities')
@click.argument('dataset_type')
def cleanup_activities(dataset_type):
    """
    Permanently delete activity stream records for a given dataset type.

    This is useful for cleaning up orphaned activities after a custom dataset
    type extension has been removed.

    Example:
    ckan -c /etc/ckan/default/ckan.ini pose-theme cleanup-activities application
    """
    click.echo(f'Searching for activity records with dataset_type="{dataset_type}"...')

    try:
        activities_to_delete = model.Session.query(Activity).filter(
            cast(Activity.data, JSONB).op('->')('package').op('->>')('type') == dataset_type
        )

        count = activities_to_delete.count()

        if count == 0:
            click.secho(f'No activity records found for type "{dataset_type}". Nothing to do.', fg='green')
            return

        click.secho(f'Found {count} activity record(s) to delete.', fg='yellow')

        if not click.confirm(f'Are you sure you want to permanently delete these {count} records?'):
            click.echo('Cleanup cancelled.')
            return

        activities_to_delete.delete(synchronize_session=False)
        model.Session.commit()
        click.secho(f'Successfully deleted {count} activity record(s).', fg='green')

    except Exception as e:
        model.Session.rollback()
        click.secho(f'An error occurred: {e}', fg='red')
        traceback.print_exc()
    finally:
        model.Session.remove()