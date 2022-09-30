import pytest
import zipfile
from io import BytesIO

from django.shortcuts import reverse

from ..downloads import download_contact_mechanics_analyses_as_zip
from ..functions import ART_CONTACT_MECHANICS


@pytest.mark.urls('topobank_contact.tests.urls')
@pytest.mark.django_db
def test_download_contact_analyses_to_zip(rf, example_contact_analysis):
    request = rf.get(reverse('analysis:download',
                             kwargs=dict(ids=str(example_contact_analysis.id),
                                         art=ART_CONTACT_MECHANICS,
                                         file_format='zip')))

    response = download_contact_mechanics_analyses_as_zip(request, [example_contact_analysis])

    archive = zipfile.ZipFile(BytesIO(response.content))

    expected_filenames = [
        "README.txt",
        f"{example_contact_analysis.subject.name}/plot.csv",
        f"{example_contact_analysis.subject.name}/info.txt",
        f"{example_contact_analysis.subject.name}/result-step-0.nc",
        f"{example_contact_analysis.subject.name}/result-step-1.nc",
        f"{example_contact_analysis.subject.name}/result-step-2.nc",
        f"{example_contact_analysis.subject.name}/result-step-3.nc",
    ]

    assert sorted(expected_filenames) == sorted(archive.namelist())

    exp_plot_content = ",Normalized pressure p/E*,Fractional contact area A/A0,Normalized mean gap u/h_rms,converged,filename\n"\
            "0,1,2,4,True,result-step-0.nc\n"\
            "1,2,4,6,True,result-step-1.nc\n"\
            "2,3,6,8,False,result-step-2.nc\n"\
            "3,4,8,10,True,result-step-3.nc\n"

    plot_content = archive.read(f"{example_contact_analysis.subject.name}/plot.csv")
    assert plot_content.decode('utf-8') == exp_plot_content

    # Howto test info.txt? Content is based on a function in topobank, so it should be tested there

    readme_content = archive.read(f"README.txt")
    assert b"Accessing the CSV file" in readme_content