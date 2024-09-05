import pytest
from django.core.files.base import ContentFile
from topobank.analysis.models import AnalysisFunction
from topobank.testing.factories import (OrganizationFactory, SurfaceFactory,
                                        Topography2DFactory,
                                        TopographyAnalysisFactory, UserFactory)
from topobank.testing.fixtures import api_rf  # noqa: F401
from topobank.testing.fixtures import handle_usage_statistics  # noqa: F401
from topobank.testing.fixtures import simple_linear_2d_topography  # noqa: F401
from topobank.testing.fixtures import sync_analysis_functions  # noqa: F401
from topobank.testing.fixtures import test_analysis_function  # noqa: F401


@pytest.mark.django_db
@pytest.fixture
def example_contact_analysis(test_analysis_function, user_with_plugin, settings):  # noqa: F811
    settings.DELETE_EXISTING_FILES = True

    func = AnalysisFunction.objects.get(name="Contact mechanics")

    storage_prefix = "test_contact_mechanics/"

    result = dict(
        name="Contact mechanics",
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
            substrate_str="periodic",
            hardness=1,
            nsteps=11,
            pressures=[1, 2, 3, 4],
            maxiter=100,
        ),
    )

    surface = SurfaceFactory(creator=user_with_plugin)
    topo = Topography2DFactory(surface=surface)

    # now the following analysis should be linked to a user who is allowed to use this plugin
    analysis = TopographyAnalysisFactory(
        function=func, result=result, subject_topography=topo
    )

    for k in range(4):
        fn = f"step-{k}/nc/results.nc"
        analysis.folder.save_file(fn, "der", ContentFile(f"test content for step {k}"))

    return analysis


@pytest.mark.django_db
@pytest.fixture
def user_with_plugin(sync_analysis_functions):  # noqa: F811
    org_name = "Test Organization"
    org = OrganizationFactory(name=org_name, plugins_available="topobank_contact")
    user = UserFactory()
    user.groups.add(org.group)
    return user
