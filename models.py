# Họ và Tên: Nguyễn Đức Hưng
# MSSV: 202418913

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import (
    Generic,
    TypeVar,
    Callable,
    Optional,
    Sequence,
    Iterable,
    AbstractSet,
)


class DeviceManagementError(Exception):
    pass


class DuplicateIdException(DeviceManagementError):
    def __init__(self, duplicate_id: str) -> None:
        self._duplicate_id = duplicate_id
        super().__init__(f"ID bị trùng: '{duplicate_id}'")

    @property
    def duplicate_id(self) -> str:
        return self._duplicate_id


class NoSuitableItemException(DeviceManagementError):
    def __init__(self, message: str = "Không tìm thấy thiết bị phù hợp") -> None:
        super().__init__(message)


class DeviceNotReadyException(DeviceManagementError):
    def __init__(self, device_id: str, current_status: DeviceStatus, reason: str) -> None:
        self._device_id = device_id
        self._current_status = current_status
        super().__init__(f"Thiết bị '{device_id}' chưa sẵn sàng ({reason})")

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def current_status(self) -> DeviceStatus:
        return self._current_status


class DeviceStatus(Enum):
    AVAILABLE = auto()
    BORROWED = auto()
    UNDER_MAINTENANCE = auto()


class IIdentifiable(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        pass


class TeachingDevice(IIdentifiable):
    def __init__(self, device_id: str, name: str, storage_location: str) -> None:
        for field, value in (("Mã thiết bị", device_id), ("Tên thiết bị", name), ("Vị trí cất giữ", storage_location)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} không được rỗng")

        self._id = device_id
        self._name = name
        self._storage_location = storage_location
        self._status = DeviceStatus.AVAILABLE

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def storage_location(self) -> str:
        return self._storage_location

    @property
    def status(self) -> DeviceStatus:
        return self._status

    def _set_status(self, s: DeviceStatus) -> None:
        self._status = s

    @abstractmethod
    def is_ready_for_use(self) -> bool:
        pass

    @abstractmethod
    def get_default_priority_score(self) -> float:
        pass

    def get_not_ready_reason(self) -> str:
        if self._status != DeviceStatus.AVAILABLE:
            return f"trạng thái hiện tại: {self._status.name}"
        return "không đạt điều kiện sẵn sàng"

    def borrow(self) -> None:
        if not self.is_ready_for_use():
            raise DeviceNotReadyException(self._id, self._status, self.get_not_ready_reason())
        self._set_status(DeviceStatus.BORROWED)

    def return_device(self) -> None:
        if self._status != DeviceStatus.BORROWED:
            raise DeviceManagementError(f"Thiết bị '{self._id}' chưa được mượn, không thể trả")
        self._set_status(DeviceStatus.AVAILABLE)

    def __repr__(self) -> str:
        return (f"{type(self).__name__}({self._id}, {self._name}, "
                f"{self._storage_location}, {self._status.name})")


def _validate_percent(value: int, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field} phải là số nguyên")
    if not 0 <= value <= 100:
        raise ValueError(f"{field} ({value}) phải nằm trong khoảng 0 đến 100")
    return value


class ProjectorRemote(TeachingDevice):
    def __init__(self, device_id: str, name: str, storage_location: str, battery_level: int) -> None:
        super().__init__(device_id, name, storage_location)
        self._battery_level = _validate_percent(battery_level, "Mức pin")

    @property
    def battery_level(self) -> int:
        return self._battery_level

    def is_ready_for_use(self) -> bool:
        return self.status == DeviceStatus.AVAILABLE and self._battery_level >= 20

    def get_default_priority_score(self) -> float:
        return float(self._battery_level)

    def get_not_ready_reason(self) -> str:
        if self.status == DeviceStatus.AVAILABLE and self._battery_level < 20:
            return f"pin {self._battery_level}% < 20%"
        return super().get_not_ready_reason()


class AirConditionerRemote(TeachingDevice):
    def __init__(self, device_id: str, name: str, storage_location: str,
                 compatible_rooms: Iterable[str]) -> None:
        super().__init__(device_id, name, storage_location)
        if isinstance(compatible_rooms, str) or compatible_rooms is None:
            raise TypeError("Danh sách phòng tương thích phải là tập/danh sách mã phòng, ví dụ {'A203'}")
        try:
            rooms = frozenset(compatible_rooms)
        except TypeError:
            raise TypeError("Danh sách phòng tương thích phải là tập/danh sách mã phòng, ví dụ {'A203'}")
        for room in rooms:
            if not isinstance(room, str):
                raise TypeError(f"Mã phòng {room!r} phải là chuỗi")
            if not room.strip():
                raise ValueError("Mã phòng không được rỗng")
        self._compatible_rooms = rooms

    @property
    def compatible_rooms(self) -> AbstractSet[str]:
        return self._compatible_rooms

    def is_ready_for_use(self) -> bool:
        return self.status == DeviceStatus.AVAILABLE

    def get_default_priority_score(self) -> float:
        return 100.0 if self._compatible_rooms else 0.0

    def is_compatible_with(self, room_id: str) -> bool:
        return room_id in self._compatible_rooms

    def get_priority_score_for_room(self, room_id: str) -> float:
        return 100.0 if self.is_compatible_with(room_id) else 0.0


class WirelessMicrophone(TeachingDevice):
    def __init__(self, device_id: str, name: str, storage_location: str,
                 battery_level: int, signal_quality: int) -> None:
        super().__init__(device_id, name, storage_location)
        self._battery_level = _validate_percent(battery_level, "Mức pin")
        self._signal_quality = _validate_percent(signal_quality, "Chất lượng tín hiệu")

    @property
    def battery_level(self) -> int:
        return self._battery_level

    @property
    def signal_quality(self) -> int:
        return self._signal_quality

    def is_ready_for_use(self) -> bool:
        return (self.status == DeviceStatus.AVAILABLE
                and self._battery_level >= 30
                and self._signal_quality >= 40)

    def get_default_priority_score(self) -> float:
        return (self._battery_level + self._signal_quality) / 2

    def get_not_ready_reason(self) -> str:
        if self.status == DeviceStatus.AVAILABLE:
            if self._battery_level < 30:
                return f"pin {self._battery_level}% < 30%"
            if self._signal_quality < 40:
                return f"tín hiệu {self._signal_quality}% < 40%"
        return super().get_not_ready_reason()


T = TypeVar("T", bound=IIdentifiable)


class IRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, item: T) -> None:
        pass

    @abstractmethod
    def remove(self, item_id: str) -> bool:
        pass

    @abstractmethod
    def find_by_id(self, item_id: str) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self) -> tuple[T, ...]:
        pass

    @abstractmethod
    def find_all(self, condition: Callable[[T], bool]) -> tuple[T, ...]:
        pass


class InMemoryRepository(IRepository[T]):
    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def add(self, item: T) -> None:
        if item is None:
            raise ValueError("Thiết bị không được rỗng")
        if item.id in self._items:
            raise DuplicateIdException(item.id)
        self._items[item.id] = item

    def remove(self, item_id: str) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    def find_by_id(self, item_id: str) -> Optional[T]:
        return self._items.get(item_id)

    def get_all(self) -> tuple[T, ...]:
        return tuple(self._items.values())

    def find_all(self, condition: Callable[[T], bool]) -> tuple[T, ...]:
        if condition is None:
            raise ValueError("Điều kiện lọc không được rỗng")
        return tuple(x for x in self._items.values() if condition(x))


S = TypeVar("S")


class ISelectionStrategy(ABC, Generic[S]):
    @abstractmethod
    def select(self, candidates: Sequence[S]) -> S:
        pass


class FirstAvailableStrategy(ISelectionStrategy[S]):
    def select(self, candidates: Sequence[S]) -> S:
        if not candidates:
            raise NoSuitableItemException()
        return candidates[0]


class HighestPriorityStrategy(ISelectionStrategy[S]):
    def __init__(self, score_selector: Callable[[S], float]) -> None:
        if score_selector is None:
            raise ValueError("Hàm tính điểm không được rỗng")
        self._score_selector = score_selector

    def select(self, candidates: Sequence[S]) -> S:
        if not candidates:
            raise NoSuitableItemException()
        return max(candidates, key=self._score_selector)


D = TypeVar("D", bound=TeachingDevice)


class AllocationService(Generic[D]):
    def __init__(self, repository: IRepository[D], strategy: ISelectionStrategy[D]) -> None:
        if repository is None:
            raise ValueError("Kho thiết bị không được rỗng")
        if strategy is None:
            raise ValueError("Chiến lược chọn không được rỗng")
        self._repository = repository
        self._strategy = strategy

    @property
    def strategy(self) -> ISelectionStrategy[D]:
        return self._strategy

    def change_strategy(self, new_strategy: ISelectionStrategy[D]) -> None:
        if new_strategy is None:
            raise ValueError("Chiến lược chọn không được rỗng")
        self._strategy = new_strategy

    def find_candidates(self, condition: Optional[Callable[[D], bool]] = None) -> tuple[D, ...]:
        return self._repository.find_all(
            lambda d: d.is_ready_for_use() and (condition is None or condition(d))
        )

    def allocate(self, condition: Optional[Callable[[D], bool]] = None) -> D:
        candidates = self.find_candidates(condition)
        device = self._strategy.select(candidates)
        device.borrow()
        return device

    def return_device(self, device_id: str) -> D:
        device = self._repository.find_by_id(device_id)
        if device is None:
            raise DeviceManagementError(f"Không tìm thấy thiết bị có mã '{device_id}'")
        device.return_device()
        return device
