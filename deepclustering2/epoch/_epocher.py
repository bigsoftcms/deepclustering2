from abc import abstractmethod, ABCMeta
from contextlib import contextmanager

import torch

from deepclustering2.meters2 import MeterInterface, EpochResultDict
from deepclustering2.models.models import Model


class _Epocher(metaclass=ABCMeta):
    def __init__(self, model: Model, cur_epoch=0, device="cpu") -> None:
        super().__init__()
        self._model = model
        self._device = device
        self._cur_epoch = cur_epoch
        self.to(self._device)

    @classmethod
    @abstractmethod
    def create_from_trainer(cls, trainer):
        pass

    @contextmanager
    def _register_meters(self):
        meters: MeterInterface = MeterInterface()
        meters = self._configure_meters(meters)
        yield meters

    @abstractmethod
    def _configure_meters(self, meters: MeterInterface) -> MeterInterface:
        # todo: to be overrided to add or delete individual meters
        return meters

    @abstractmethod
    def _run(self, *args, **kwargs) -> EpochResultDict:
        pass

    def run(self, *args, **kwargs) -> EpochResultDict:
        with self._register_meters() as self.meters:
            return self._run(*args, **kwargs)

    def to(self, device="cpu"):
        if isinstance(device, str):
            device = torch.device(device)
        assert isinstance(device, torch.device)
        self._model.to(device)
        self._device = device
