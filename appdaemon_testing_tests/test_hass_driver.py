# pylint: disable=C0115 C0116 W0212 W0621
from unittest import mock

import appdaemon.plugins.hass.hassapi as hass
import pytest

from appdaemon_testing import HassDriver
from appdaemon_testing.pytest import automation_fixture


@pytest.fixture
def hass_driver_with_initialized_states(hass_driver):
    hass_driver._states = {
        "light.1": {"state": "off", "linkquality": 60},
        "light.2": {"state": "on", "linkquality": 10, "brightness": 60},
        "media_player.smart_tv": {"state": "on", "source": None},
    }
    return hass_driver


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_get_state(hass_driver):
    get_state = hass_driver.get_mock("get_state")
    assert get_state("light.1") == "off"


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_get_state_attribute(hass_driver):
    get_state = hass_driver.get_mock("get_state")
    assert get_state("light.1", attribute="linkquality") == 60


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_get_state_attribute_all(hass_driver):
    get_state = hass_driver.get_mock("get_state")
    assert get_state("light.1", attribute="all") == {"state": "off", "linkquality": 60}


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_get_state_attribute_domain(hass_driver):
    get_state = hass_driver.get_mock("get_state")
    assert get_state("light") == {"light.1": "off", "light.2": "on"}


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_get_state_attribute_domain_with_attribute(hass_driver):
    get_state = hass_driver.get_mock("get_state")
    assert get_state("light", attribute="linkquality") == {"light.1": 60, "light.2": 10}


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_get_state_attribute_domain_with_attribute_all(hass_driver):
    get_state = hass_driver.get_mock("get_state")
    assert get_state("light", attribute="all") == {
        "light.1": {"state": "off", "linkquality": 60},
        "light.2": {"state": "on", "linkquality": 10, "brightness": 60},
    }


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_get_state_with_default(hass_driver):
    get_state = hass_driver.get_mock("get_state")
    assert get_state("light.1", attribute="brightness", default=40) == 40
    assert get_state("light.2", attribute="brightness", default=40) == 60


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_get_state_domain_with_default(hass_driver):
    get_state = hass_driver.get_mock("get_state")
    assert get_state("light", attribute="brightness", default=40) == {
        "light.1": 40,
        "light.2": 60,
    }


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_listen_state(hass_driver):
    listen_state = hass_driver.get_mock("listen_state")
    callback1 = mock.Mock()
    callback2 = mock.Mock()
    listen_state(callback1, "light.1")
    listen_state(callback2, "light.1")

    assert callback1.call_count == 0
    assert callback2.call_count == 0

    hass_driver.set_state("light.1", "off")

    assert callback1.call_count == 0
    assert callback2.call_count == 0

    hass_driver.set_state("light.1", "on")

    callback1.assert_called_once_with("light.1", "state", "off", "on", {})
    callback2.assert_called_once_with("light.1", "state", "off", "on", {})


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_listen_state_attribute(hass_driver):
    listen_state = hass_driver.get_mock("listen_state")
    callback = mock.Mock()
    listen_state(callback, "light.1", attribute="linkquality")

    assert callback.call_count == 0
    hass_driver.set_state("light.1", "on")
    assert callback.call_count == 0

    hass_driver.set_state("light.1", 50, attribute_name="linkquality")
    callback.assert_called_once_with("light.1", "linkquality", 60, 50, {})


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_listen_state_attribute_all(hass_driver):
    listen_state = hass_driver.get_mock("listen_state")
    callback = mock.Mock()
    listen_state(callback, "light.1", attribute="all")

    assert callback.call_count == 0
    hass_driver.set_state("light.1", 75, attribute_name="brightness")
    callback.assert_called_once_with(
        "light.1",
        None,
        {"state": "off", "linkquality": 60},
        {"state": "off", "linkquality": 60, "brightness": 75},
        {},
    )


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_listen_state_domain(hass_driver):
    listen_state = hass_driver.get_mock("listen_state")
    callback = mock.Mock()
    listen_state(callback, "light", attribute="brightness")

    assert callback.call_count == 0
    hass_driver.set_state("light.2", 75, attribute_name="brightness")
    callback.assert_called_once_with("light.2", "brightness", 60, 75, {})


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_listen_state_with_new(hass_driver):
    listen_state = hass_driver.get_mock("listen_state")
    callback = mock.Mock()
    listen_state(callback, "media_player.smart_tv", attribute="source", new="Spotify")

    hass_driver.set_state("media_player.smart_tv", "YouTube", attribute_name="source")
    assert callback.call_count == 0

    hass_driver.set_state("media_player.smart_tv", "Spotify", attribute_name="source")
    callback.assert_called_once_with(
        "media_player.smart_tv", "source", "YouTube", "Spotify", {}
    )


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_listen_state_with_old(hass_driver):
    listen_state = hass_driver.get_mock("listen_state")
    callback = mock.Mock()
    listen_state(callback, "media_player.smart_tv", attribute="source", old="Spotify")

    hass_driver.set_state("media_player.smart_tv", "Spotify", attribute_name="source")
    assert callback.call_count == 0

    hass_driver.set_state("media_player.smart_tv", "TV", attribute_name="source")
    callback.assert_called_once_with(
        "media_player.smart_tv", "source", "Spotify", "TV", {}
    )


@pytest.mark.usefixtures("hass_driver_with_initialized_states")
def test_setup_does_not_trigger_spys(hass_driver):
    listen_state = hass_driver.get_mock("listen_state")
    callback = mock.Mock()
    listen_state(callback, "light")
    listen_state(callback, "light.1", attribute="brightness")

    with hass_driver.setup():
        hass_driver.set_state("light.1", "off")
        hass_driver.set_state("light.1", "on")
        hass_driver.set_state("light.1", 50, attribute_name="linkquality")

    assert callback.call_count == 0
    hass_driver.set_state("light.1", "off")
    assert callback.call_count == 1


class MyApp(hass.Hass):
    def initialize(self):
        self.log("This is a log")
        self.error("This is an error")


@automation_fixture(MyApp, args={}, initialize=False)
def my_app() -> MyApp:
    pass


def test_log(hass_driver, my_app: MyApp):
    hass_driver.inject_mocks()

    my_app.initialize()

    log = hass_driver.get_mock("log")
    error = hass_driver.get_mock("error")
    log.assert_called_once_with("This is a log")
    error.assert_called_once_with("This is an error")


def test_set_state(hass_driver, my_app: MyApp):
    hass_driver.inject_mocks()

    with hass_driver.setup():
        hass_driver.set_state("domain.sensor", state="my_state")

    my_app.initialize()

    assert hass_driver._states == {"domain.sensor": {"state": "my_state"}}

    my_app.set_state("domain.sensor", state="my_new_state")

    assert hass_driver._states == {"domain.sensor": {"state": "my_new_state"}}


@pytest.fixture
def hass_driver() -> HassDriver:
    hass_driver = HassDriver()
    return hass_driver
