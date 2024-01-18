import pytest

from topobank.manager.utils import subjects_to_base64

from ..views import contact_mechanics_card_view


@pytest.mark.django_db
@pytest.mark.urls('topobank_contact.tests.urls')
@pytest.mark.parametrize('template_flavor', ['list', 'detail'])
def test_resolve_card_view(api_rf, example_contact_analysis, template_flavor, handle_usage_statistics):
    subjects = subjects_to_base64([example_contact_analysis.subject])

    request = api_rf.get(f'/plugins/contact/card/contact-mechanics/{example_contact_analysis.function.id}',
                         {'function_id': example_contact_analysis.function.id, 'subjects': subjects})
    request.user = example_contact_analysis.related_surfaces()[0].creator
    request.session = {}

    response = contact_mechanics_card_view(request)
    assert response.status_code == 200
