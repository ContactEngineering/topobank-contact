import pytest

from topobank.manager.utils import subjects_to_dict

from ..views import contact_mechanics_card_view


@pytest.mark.urls('topobank_contact.tests.urls')
@pytest.mark.parametrize('template_flavor', ['list', 'detail'])
def test_resolve_card_view(api_rf, example_contact_analysis, template_flavor):
    subjects = subjects_to_dict([example_contact_analysis.subject])

    request = api_rf.post('/plugins/topobank_contact/card/contact-mechanics',
                   data=dict(
                       function_id=example_contact_analysis.function.id,
                       subjects=subjects
                   ), format='json')  # we need an AJAX request
    request.user = example_contact_analysis.related_surfaces()[0].creator
    request.session = {}

    response = contact_mechanics_card_view(request)
    assert response.status_code == 200
