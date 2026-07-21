from topobank.test_settings import *  # noqa: F401, F403

ROOT_URLCONF = "test_urls"

CONTACT_MECHANICS_KWARGS_LIMITS = {
    "nsteps": dict(min=1, max=50),
    "maxiter": dict(min=100, max=1000),
    "pressures": dict(maxlen=50),
}
