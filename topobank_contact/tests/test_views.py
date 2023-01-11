import pytest

from django.shortcuts import reverse

from topobank.utils import assert_in_content
from topobank.manager.utils import subjects_to_json
from topobank.analysis.views import switch_card_view
from topobank.analysis.registry import AnalysisRegistry

from ..views import ContactMechanicsCardView


@pytest.mark.urls('topobank_contact.tests.urls')
@pytest.mark.parametrize('template_flavor', ['list', 'detail'])
def test_resolve_card_view(rf, example_contact_analysis, template_flavor):
    subjects_ids_json = subjects_to_json([example_contact_analysis.subject])

    request = rf.post(reverse('analysis:card'),
                   data=dict(
                       function_id=example_contact_analysis.function.id,
                       card_id="card-1",
                       template_flavor=template_flavor,
                       subjects_ids_json=subjects_ids_json
                   ), HTTP_X_REQUESTED_WITH='XMLHttpRequest')  # we need an AJAX request
    request.user = example_contact_analysis.related_surfaces()[0].creator
    request.session = {}

    reg = AnalysisRegistry()
    card_view_class = reg.get_card_view_class(
        reg.get_analysis_result_type_for_function_name(example_contact_analysis.function.name))
    assert card_view_class == ContactMechanicsCardView

    card_view = card_view_class.as_view()
    response = card_view(request)
    assert response.status_code == 200
    assert response.template_name == [f'topobank_contact/contact_mechanics_card_{template_flavor}.html']

    # Render does not work yet here, templates of main topobank package not found
    # response.render()
    # assert_in_content(response, 'Load vs displacement')






