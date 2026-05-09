import pytest
from django.core.files.base import ContentFile
from topobank.analysis.models import Workflow
from topobank.testing.factories import (OrganizationFactory, SurfaceFactory,
                                        Topography2DFactory,
                                        TopographyAnalysisFactory, UserFactory)
from topobank.testing.fixtures import handle_usage_statistics  # noqa: F401
from topobank.testing.fixtures import simple_linear_2d_topography  # noqa: F401
from topobank.testing.fixtures import sync_workflows  # noqa: F401
from topobank.testing.fixtures import test_workflow  # noqa: F401
from topobank.testing.fixtures import api_rf, two_topos  # noqa: F401


@pytest.fixture
def example_contact_analysis(test_workflow, user_with_plugin, settings):  # noqa: F811
    settings.DELETE_EXISTING_FILES = True

    func = Workflow(name="topobank_contact.boundary_element_method")

    storage_prefix = "test_contact_mechanics/"

    result = dict(
        name="topobank_contact.boundary_element_method",
        display_name="Contact mechanics",
        area_per_pt=0.1,
        maxiter=100,
        min_pentol=0.01,
        mean_pressures=[1, 2, 3, 4],
        total_contact_areas=[2, 4, 6, 8],
        mean_displacements=[3, 5, 7, 9],
        mean_gaps=[4, 6, 8, 10],
        converged=[True, True, False, True],
        data_paths=[
            storage_prefix + "step-0",
            storage_prefix + "step-1",
            storage_prefix + "step-2",
            storage_prefix + "step-3",
        ],
        effective_kwargs=dict(
            substrate="periodic",
            hardness=1,
            nsteps=11,
            pressures=[1, 2, 3, 4],
            maxiter=100,
        ),
    )

    surface = SurfaceFactory(created_by=user_with_plugin)
    topo = Topography2DFactory(surface=surface)

    # now the following analysis should be linked to a user who is allowed to use this plugin
    analysis = TopographyAnalysisFactory(
        workflow_name=func.name, result=result, subject_topography=topo
    )

    for k in range(4):
        fn = f"step-{k}/nc/results.nc"
        analysis.folder.save_file(fn, "der", ContentFile(b"test content"))

    return analysis


@pytest.fixture
def user_with_plugin(sync_workflows):  # noqa: F811
    org_name = "Test Organization"
    org = OrganizationFactory(name=org_name)
    user = UserFactory()
    user.groups.add(org.group)
    return user
