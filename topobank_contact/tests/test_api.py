from django.urls import reverse


def test_api():
    """Test API routes"""
    assert reverse('topobank_contact:card-contact-mechanics',
                   kwargs=dict(function_id=123)) == '/plugins/contact/card/contact-mechanics/123'
