import pytest
from io import StringIO

from topobank.analysis.models import AnalysisFunction
from topobank.analysis.tests.utils import TopographyAnalysisFactory
from topobank.manager.tests.utils import SurfaceFactory, Topography2DFactory


@pytest.mark.django_db
@pytest.fixture
def example_contact_analysis(test_analysis_function, user_with_plugin):
    func = AnalysisFunction.objects.get(name="Contact mechanics")

    storage_prefix = "test_contact_mechanics/"

    result = dict(
        name='Contact mechanics',
        area_per_pt=0.1,
        maxiter=100,
        min_pentol=0.01,
        mean_pressures=[1, 2, 3, 4],
        total_contact_areas=[2, 4, 6, 8],
        mean_displacements=[3, 5, 7, 9],
        mean_gaps=[4, 6, 8, 10],
        converged=[True, True, False, True],
        data_paths=[storage_prefix + "step-0", storage_prefix + "step-1",
                    storage_prefix + "step-2", storage_prefix + "step-3", ],
        effective_kwargs=dict(
            substrate_str="periodic",
            hardness=1,
            nsteps=11,
            pressures=[1, 2, 3, 4],
            maxiter=100,
        )
    )

    surface = SurfaceFactory(creator=user_with_plugin)
    topo = Topography2DFactory(surface=surface)

    # now the following analysis should be linked to a user who is allowed to use this plugin
    analysis = TopographyAnalysisFactory(function=func, result=result, subject=topo)

    # create files in storage for zipping
    from django.core.files.storage import default_storage

    files_to_delete = []

    for k in range(4):
        fn = f"{analysis.storage_prefix}/step-{k}/nc/results.nc"
        default_storage.save(fn, StringIO(f"test content for step {k}"))

    yield analysis

    for fn in files_to_delete:
        default_storage.delete(fn)





