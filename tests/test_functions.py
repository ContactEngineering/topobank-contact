import numpy as np
import pytest
from SurfaceTopography import NonuniformLineScan as STNonuniformLineScan
from topobank.testing.factories import FolderFactory
from topobank.testing.utils import (AnalysisResultMock, DummyProgressRecorder,
                                    FakeTopographyModel)

from topobank_contact.workflows import (BoundaryElementMethod,
                                        IncompatibleTopographyException)


def test_contact_mechanics_incompatible_topography():
    x = np.arange(10)
    arr = 2 * x
    t = STNonuniformLineScan(x, arr, unit="nm").detrend("center")
    topography = FakeTopographyModel(t)

    with pytest.raises(IncompatibleTopographyException):
        BoundaryElementMethod().topography_implementation(
            AnalysisResultMock(topography, folder=FolderFactory())
        )


def test_contact_mechanics_whether_given_pressures_in_result(
    simple_linear_2d_topography,
):
    given_pressures = [2e-3, 1e-2]
    topography = FakeTopographyModel(simple_linear_2d_topography)
    result = BoundaryElementMethod(
        nsteps=None, pressures=given_pressures
    ).topography_implementation(
        AnalysisResultMock(topography, folder=FolderFactory()),
        progress_recorder=DummyProgressRecorder(),
    )

    np.testing.assert_almost_equal(result["mean_pressures"], given_pressures)


@pytest.mark.parametrize(["x_dim", "y_dim"], [[20000, 10000], [9999999, 3]])
def test_exception_topography_too_large_for_contact_mechanics(
    x_dim, y_dim, mocker, simple_linear_2d_topography
):
    topo = FakeTopographyModel(simple_linear_2d_topography)

    # patch raw topography in order to return a higher number of grid points
    m = mocker.patch(
        "SurfaceTopography.Topography.nb_grid_pts", new_callable=mocker.PropertyMock
    )
    m.return_value = (
        x_dim,
        y_dim,
    )  # this make the topography returning high numbers of grid points

    with pytest.raises(IncompatibleTopographyException):
        BoundaryElementMethod().topography_implementation(
            AnalysisResultMock(topo, folder=FolderFactory())
        )


@pytest.mark.parametrize(
    ["topo_is_periodic", "substrate", "exp_num_alerts"],
    [
        [False, "nonperiodic", 0],
        [False, "periodic", 1],
        [True, "nonperiodic", 1],
        [True, "periodic", 0],
    ],
)
def test_alert_if_topographys_periodicity_does_not_match(
    simple_linear_2d_topography, topo_is_periodic, substrate, exp_num_alerts
):
    topo = FakeTopographyModel(
        simple_linear_2d_topography, is_periodic=topo_is_periodic
    )
    result = BoundaryElementMethod(
        substrate=substrate,
    ).topography_implementation(
        AnalysisResultMock(topo, folder=FolderFactory()),
        progress_recorder=DummyProgressRecorder(),
    )

    assert len(result["alerts"]) == exp_num_alerts
