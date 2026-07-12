import pytest
from doug_os.discovery.scientific_method.experiment_protocol import (
    ExperimentProtocol, ExperimentDesign
)


def _valid_exp(**kwargs) -> ExperimentProtocol:
    defaults = dict(
        scientific_protocol_id="proto_abc",
        design=ExperimentDesign.A_B_TESTING,
        sample_size=100,
        iterations=50,
        confidence_level=0.95,
        primary_metric="return",
    )
    defaults.update(kwargs)
    return ExperimentProtocol(**defaults)


def test_experiment_protocol_valid():
    ep = _valid_exp()
    assert ep.is_valid()


def test_experiment_protocol_invalid_no_metric():
    ep = _valid_exp(primary_metric="")
    assert not ep.is_valid()


def test_experiment_protocol_invalid_bad_confidence():
    ep = _valid_exp(confidence_level=1.5)
    assert not ep.is_valid()


def test_experiment_protocol_to_dict_and_back():
    ep = _valid_exp()
    d = ep.to_dict()
    ep2 = ExperimentProtocol.from_dict(d)
    assert ep2.id == ep.id
    assert ep2.design == ep.design
    assert ep2.sample_size == ep.sample_size
