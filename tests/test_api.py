from django.urls import reverse


def test_api():
    """Test API routes"""
    assert (
        reverse("topobank_contact:card-contact-mechanics", kwargs=dict(workflow="abc"))
        == "/plugins/contact/card/contact-mechanics/abc"
    )
