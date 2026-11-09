from pi_controller.devices.base import Device


class DeviceAlreadyRegistered(Exception):
    pass


class DeviceNotFound(Exception):
    pass


class DeviceRegistry:

    def __init__(self):
        self._devices: dict[str, Device] = {}

    def register(self, device: Device) -> None:
        if device.id in self._devices:
            raise DeviceAlreadyRegistered(device.id)

        self._devices[device.id] = device

    def get(self, device_id: str) -> Device:
        device = self._devices.get(device_id)

        if device is None:
            raise DeviceNotFound(device_id)

        return device

    def list_devices(self) -> list[Device]:
        return list(self._devices.values())