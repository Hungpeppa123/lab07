# Họ và Tên: Nguyễn Đức Hưng
# MSSV: 202418913

from models import *


def section(title: str):
    print(f"\n=== {title} ===")


def main():
    # Test 1: Thêm vào repo
    section("1. Thêm vào repo")
    projector_repo = InMemoryRepository[ProjectorRemote]()
    ac_repo = InMemoryRepository[AirConditionerRemote]()
    mic_repo = InMemoryRepository[WirelessMicrophone]()

    projector_repo.add(ProjectorRemote("PR01", "Điều khiển máy chiếu 1", "Tủ A", 90))
    projector_repo.add(ProjectorRemote("PR02", "Điều khiển máy chiếu 2", "Tủ A", 10))
    projector_repo.add(ProjectorRemote("PR03", "Điều khiển máy chiếu 3", "Tủ B", 60))

    ac_repo.add(AirConditionerRemote("AC01", "Điều khiển điều hòa 1", "Tủ C", {"A101", "A102"}))
    ac_repo.add(AirConditionerRemote("AC02", "Điều khiển điều hòa 2", "Tủ C", {"A203", "A204"}))

    mic_repo.add(WirelessMicrophone("MI01", "Micro 1", "Tủ D", 20, 90))
    mic_repo.add(WirelessMicrophone("MI02", "Micro 2", "Tủ D", 60, 60))
    mic_repo.add(WirelessMicrophone("MI03", "Micro 3", "Tủ D", 90, 80))

    print(f"Máy chiếu: {len(projector_repo.get_all())}")
    print(f"Điều hòa: {len(ac_repo.get_all())}")
    print(f"Micro: {len(mic_repo.get_all())}")

    # Test 2: Trùng mã
    section("2. Trùng mã")
    try:
        projector_repo.add(ProjectorRemote("PR01", "Bản sao", "Tủ A", 50))
    except DuplicateIdException as e:
        print(f"Bắt được lỗi trùng mã: {e.duplicate_id}")
    else:
        print("SAI")
    print(f"Số máy chiếu vẫn là: {len(projector_repo.get_all())}")

    # Test 3: Tìm theo mã
    section("3. Tìm theo mã")
    print(projector_repo.find_by_id("PR03"))
    print(projector_repo.find_by_id("XXX"))

    # Test 4: Lọc sẵn sàng
    section("4. Lọc sẵn sàng")
    print(projector_repo.find_all(lambda d: d.is_ready_for_use()))
    print(mic_repo.find_all(lambda d: d.is_ready_for_use()))

    # Test 5: Máy chiếu điểm cao nhất
    section("5. Máy chiếu điểm cao nhất")
    projector_service = AllocationService(
        projector_repo,
        HighestPriorityStrategy(lambda d: d.get_default_priority_score()),
    )
    selected_projector = projector_service.allocate()
    print(f"Được chọn: {selected_projector}")

    # Test 6: Điều hòa theo phòng
    section("6. Điều hòa theo phòng")
    ac_service = AllocationService(ac_repo, FirstAvailableStrategy())
    selected_ac = ac_service.allocate(lambda d: d.is_compatible_with("A203"))
    print(f"Được chọn: {selected_ac}")

    # Test 7: Micro đầu tiên sẵn sàng
    section("7. Micro đầu tiên sẵn sàng")
    mic_service = AllocationService(mic_repo, FirstAvailableStrategy())
    selected_mic = mic_service.allocate()
    print(f"Được chọn: {selected_mic}")

    # Test 8: Đổi chiến lược
    section("8. Đổi chiến lược")
    print(f"Trả: {mic_service.return_device('MI02')}")
    print(f"Ứng viên: {mic_service.find_candidates()}")
    print(f"Chiến lược trước: {type(mic_service.strategy).__name__}")
    mic_service.change_strategy(HighestPriorityStrategy(lambda d: d.get_default_priority_score()))
    print(f"Chiến lược sau: {type(mic_service.strategy).__name__}")
    print(f"Được chọn: {mic_service.allocate()}")

    # Test 9: Không có ứng viên
    section("9. Không có ứng viên")
    try:
        ac_service.allocate(lambda d: d.is_compatible_with("Z999"))
    except NoSuitableItemException as e:
        print(f"Bắt được lỗi: {e}")
    else:
        print("SAI")

    # Test 10: Chuyển sang Borrowed
    section("10. Chuyển sang Borrowed")
    found = projector_repo.find_by_id("PR01")
    print(f"Trạng thái PR01: {found.status.name}")
    assert found.status == DeviceStatus.BORROWED
    projector_service.return_device("PR01")
    print(f"Sau khi trả: {found.status.name}")

    # Test 11: Repo generic
    section("11. Repo generic")
    for repo in (projector_repo, ac_repo, mic_repo):
        device_types = {type(d).__name__ for d in repo.get_all()}
        print(f"{type(repo).__name__} chứa {device_types}")
    print(f"Cùng một lớp: {type(projector_repo) is type(mic_repo)}")


if __name__ == "__main__":
    main()
