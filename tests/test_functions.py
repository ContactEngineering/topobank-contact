import numpy as np
import pytest
from SurfaceTopography import NonuniformLineScan as STNonuniformLineScan
from SurfaceTopography import Topography as STTopography
from topobank.testing.factories import ManifestSetFactory
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
            AnalysisResultMock(topography, folder=ManifestSetFactory())
        )


def test_contact_mechanics_whether_given_pressures_in_result(
    simple_linear_2d_topography,
):
    given_pressures = [2e-3, 1e-2]
    topography = FakeTopographyModel(simple_linear_2d_topography)
    result = BoundaryElementMethod(
        nsteps=None, pressures=given_pressures
    ).topography_implementation(
        AnalysisResultMock(topography, folder=ManifestSetFactory()),
        progress_recorder=DummyProgressRecorder(),
    )

    np.testing.assert_almost_equal(result["mean_pressures"], given_pressures)


def test_contact_mechanics_flat_topography_raises():
    t = STTopography(np.zeros((16, 16)), physical_sizes=(1.0, 1.0), unit="nm")
    topography = FakeTopographyModel(t)

    with pytest.raises(IncompatibleTopographyException):
        BoundaryElementMethod().topography_implementation(
            AnalysisResultMock(topography, folder=ManifestSetFactory()),
            progress_recorder=DummyProgressRecorder(),
        )


def test_contact_mechanics_step_file_annotations(simple_linear_2d_topography):
    topography = FakeTopographyModel(simple_linear_2d_topography)
    folder = ManifestSetFactory()
    result = BoundaryElementMethod(
        nsteps=None, pressures=[1e-2]
    ).topography_implementation(
        AnalysisResultMock(topography, folder=folder),
        progress_recorder=DummyProgressRecorder(),
    )

    dataset = folder.read_xarray("step-0/nc/results.nc")

    # Units are annotated on all variables and on the dataset (issue #24)
    unit = simple_linear_2d_topography.unit
    assert dataset.pressure.attrs["units"] == "E*"
    assert dataset.gap.attrs["units"] == unit
    assert dataset.displacement.attrs["units"] == unit
    assert dataset.contacting_points.attrs["units"] == "1"
    assert dataset.attrs["length_unit"] == unit

    # The rigid body displacement (offset) and the convergence status are
    # reported for each step (issues #28, #29). The result dict stores
    # displacements normalized by the rms height.
    assert dataset.attrs["mean_displacement"] == pytest.approx(
        result["mean_displacements"][0] * result["rms_height"]
    )
    assert dataset.attrs["converged"] in (0, 1)
    assert dataset.attrs["mean_pressure"] == pytest.approx(
        result["mean_pressures"][0]
    )

    # The reported contact area is consistent with the contacting points map
    # from the optimizer's active set (issue #16)
    nb_pts = np.prod(dataset.contacting_points.shape)
    assert dataset.attrs["total_contact_area"] == pytest.approx(
        dataset.contacting_points.data.sum() / nb_pts
    )


def test_contact_mechanics_reports_forces_and_scan_area(
    simple_linear_2d_topography,
):
    topography = FakeTopographyModel(simple_linear_2d_topography)
    given_pressures = [2e-3, 1e-2]
    result = BoundaryElementMethod(
        nsteps=None, pressures=given_pressures
    ).topography_implementation(
        AnalysisResultMock(topography, folder=ManifestSetFactory()),
        progress_recorder=DummyProgressRecorder(),
    )

    scan_area = np.prod(simple_linear_2d_topography.physical_sizes)
    assert result["scan_area"] == pytest.approx(scan_area)
    assert result["unit"] == simple_linear_2d_topography.unit
    assert result["rms_height"] == pytest.approx(
        simple_linear_2d_topography.rms_height_from_area()
    )
    # Total force is nominal pressure times scan area (issues #15, #25)
    np.testing.assert_allclose(
        result["mean_forces"], np.array(given_pressures) * scan_area
    )


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
            AnalysisResultMock(topo, folder=ManifestSetFactory())
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
        AnalysisResultMock(topo, folder=ManifestSetFactory()),
        progress_recorder=DummyProgressRecorder(),
    )

    assert len(result["alerts"]) == exp_num_alerts
