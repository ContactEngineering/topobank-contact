import io
import zipfile
from io import BytesIO

import numpy as np
import pytest
from django.shortcuts import reverse
from scipy.io import netcdf_file
from topobank.analysis.models import AnalysisFunction
from topobank.manager.utils import subjects_to_base64

from topobank_contact.downloads import \
    download_contact_mechanics_analyses_as_zip


@pytest.mark.urls("topobank_contact.testing.urls")
@pytest.mark.django_db
def test_download_mock_contact_analysis_to_zip(api_rf, example_contact_analysis):
    request = api_rf.get(
        reverse(
            "analysis:download",
            kwargs=dict(ids=str(example_contact_analysis.id), file_format="zip"),
        )
    )

    response = download_contact_mechanics_analyses_as_zip(
        request, [example_contact_analysis]
    )

    archive = zipfile.ZipFile(BytesIO(response.content))

    expected_filenames = [
        "README.txt",
        f"{example_contact_analysis.subject.name}/plot.csv",
        f"{example_contact_analysis.subject.name}/info.txt",
        f"{example_contact_analysis.subject.name}/result.json",
        f"{example_contact_analysis.subject.name}/result-step-0.nc",
        f"{example_contact_analysis.subject.name}/result-step-1.nc",
        f"{example_contact_analysis.subject.name}/result-step-2.nc",
        f"{example_contact_analysis.subject.name}/result-step-3.nc",
    ]

    assert sorted(expected_filenames) == sorted(archive.namelist())

    exp_plot_content = (
        ",Normalized pressure p/E*,Fractional contact area A/A0,Normalized mean gap u/h_rms,converged,"
        "filename\n0,1,2,4,True,result-step-0.nc\n1,2,4,6,True,result-step-1.nc\n"
        "2,3,6,8,False,result-step-2.nc\n3,4,8,10,True,result-step-3.nc\n"
    )

    plot_content = archive.read(f"{example_contact_analysis.subject.name}/plot.csv")
    assert plot_content.decode("utf-8") == exp_plot_content

    # Howto test info.txt? Content is based on a function in topobank, so it should be tested there

    readme_content = archive.read("README.txt")
    assert b"Accessing the CSV file" in readme_content

    nc_content = archive.read(
        f"{example_contact_analysis.subject.name}/result-step-2.nc"
    )
    assert nc_content == b"test content"


def read_csv(f):
    data = []
    f.readline()  # Skip first line
    L = f.readline()
    while L:
        data += [L.split(",")]
        L = f.readline()
    return np.transpose(data)


@pytest.mark.urls("topobank_contact.testing.urls")
@pytest.mark.django_db
def test_download_actual_contact_analysis_to_zip(
    api_client, two_topos, mocker, django_capture_on_commit_callbacks, settings
):
    settings.CELERY_TASK_ALWAYS_EAGER = True  # perform tasks locally
    topo1, topo2 = two_topos

    m = mocker.patch(
        "topobank.analysis.functions.AnalysisImplementation.has_permission"
    )
    m.return_value = True

    api_client.force_login(topo2.creator)
    contact_mechanics = AnalysisFunction.objects.get(name="Contact mechanics")
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        response = api_client.get(
            f"{reverse('analysis:result-list')}?subjects="
            f"{subjects_to_base64([topo2])}&function_id={contact_mechanics.id}"
        )
        assert response.status_code == 200
    assert len(callbacks) == 1
    assert len(response.data["analyses"]) == 1
    assert response.data["analyses"][0]["task_state"] == "pe"

    # Need to call this again to see the success state
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        response = api_client.get(
            f"{reverse('analysis:result-list')}?subjects="
            f"{subjects_to_base64([topo2])}&function_id={contact_mechanics.id}"
        )
        assert response.status_code == 200
    assert len(callbacks) == 0
    assert len(response.data["analyses"]) == 1
    assert response.data["analyses"][0]["task_state"] == "su"

    # Download
    response = api_client.get(
        reverse(
            "analysis:download",
            kwargs=dict(ids=response.data["analyses"][0]["id"], file_format="zip"),
        )
    )

    # Check the content of the zip file
    archive = zipfile.ZipFile(BytesIO(response.content))

    expected_filenames = [
        "README.txt",
        f"{topo2.name}/plot.csv",
        f"{topo2.name}/info.txt",
        f"{topo2.name}/result.json",
        f"{topo2.name}/result-step-0.nc",
        f"{topo2.name}/result-step-1.nc",
        f"{topo2.name}/result-step-2.nc",
        f"{topo2.name}/result-step-3.nc",
        f"{topo2.name}/result-step-4.nc",
        f"{topo2.name}/result-step-5.nc",
        f"{topo2.name}/result-step-6.nc",
        f"{topo2.name}/result-step-7.nc",
        f"{topo2.name}/result-step-8.nc",
        f"{topo2.name}/result-step-9.nc",
    ]

    assert sorted(expected_filenames) == sorted(archive.namelist())

    exp_plot_content = (
        ",Normalized pressure p/E*,Fractional contact area A/A0,Normalized mean gap u/h_rms,converged,filename\n"
        "0,1.6537790630515102e-07,4.371584699453552e-05,2.1084156348698175,True,result-step-1.nc\n"
        "1,1.4680998872559262e-06,0.00017486338797814208,2.0433658343082093,True,result-step-7.nc\n"
        "2,4.337221850895204e-06,0.0005245901639344263,1.9793492680823797,True,result-step-5.nc\n"
        "3,1.7512125354967977e-05,0.0018797814207650273,1.8561513580356113,True,result-step-4.nc\n"
        "4,4.656089565527127e-05,0.0051147540983606556,1.7427931604060258,True,result-step-8.nc\n"
        "5,9.51276577476628e-05,0.009530054644808742,1.6413243139475338,True,result-step-3.nc\n"
        "6,0.00023888767275195304,0.02041530054644809,1.4664601572611482,True,result-step-9.nc\n"
        "7,0.00044130574852529596,0.035584699453551916,1.3279836214453513,True,result-step-2.nc\n"
        "8,0.001628504212817706,0.10854644808743169,1.0017942681918388,True,result-step-0.nc\n"
        "9,0.0058219472965921944,0.2766775956284153,0.6502025742003311,True,result-step-6.nc\n"
    )

    i1, p1, a1, g1, conv1, fn1 = read_csv(
        io.StringIO(archive.read(f"{topo2.name}/plot.csv").decode("latin-1"))
    )
    i2, p2, a2, g2, conv2, fn2 = read_csv(io.StringIO(exp_plot_content))
    assert np.all(i1 == i2)
    rtol = 1e-3
    np.testing.assert_allclose(p1.astype(float), p2.astype(float), rtol=rtol)
    np.testing.assert_allclose(a1.astype(float), a2.astype(float), rtol=rtol)
    np.testing.assert_allclose(g1.astype(float), g2.astype(float), rtol=rtol)
    assert np.all(conv1 == conv2)
    assert np.all(fn1 == fn2)

    # Howto test info.txt? Content is based on a function in topobank, so it should be
    # tested there

    readme_content = archive.read("README.txt")
    assert b"Accessing the CSV file" in readme_content

    nc_content = archive.read(f"{topo2.name}/result-step-2.nc")
    nc = netcdf_file(io.BytesIO(nc_content))
    assert "contacting_points" in nc.variables
    assert "displacement" in nc.variables
    assert "gap" in nc.variables
    assert "pressure" in nc.variables
