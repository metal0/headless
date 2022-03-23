from enum import Enum

class WindowsScanType(Enum):
    read_memory = 0
    find_module_by_name = 1
    find_mem_image_code_by_hash = 2
    find_code_by_hash = 3
    hash_client_file = 4
    get_lua_variable = 5
    api_check = 6
    find_driver_by_name = 7
    check_timing_values = 8
    max_scan_type = 9
