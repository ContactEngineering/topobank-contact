import pytest
from topobank.manager.utils import subjects_to_base64

from topobank_contact.views import contact_mechanics_card_view


@pytest.mark.django_db
@pytest.mark.urls("topobank_contact.testing.urls")
@pytest.mark.parametrize("template_flavor", ["list", "detail"])
def test_resolve_card_view(
    api_rf, example_contact_analysis, template_flavor, handle_usage_statistics
):
    subjects = subjects_to_base64([example_contact_analysis.subject])

    request = api_rf.get(
        f"/plugins/contact/card/contact-mechanics/{example_contact_analysis.function.name}",
        {"workflow": example_contact_analysis.function.name, "subjects": subjects},
    )
    request.user = example_contact_analysis.get_related_surfaces()[0].creator
    request.session = {}

    response = contact_mechanics_card_view(request)
    assert response.status_code == 200
