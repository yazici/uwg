import pytest
from UWG import UWG

DIR_EPW_NAME = "data\\epw\\"


def test_UWG():
    """Test for UWG.py"""

    epw_dir = None
    epw_file_name = None
    uwg_param_dir = None
    uwg_param_file_name = None

    UWG(epw_dir, epw_file_name, uwg_param_dir, uwg_param_file_name)

if __name__ == '__main__':
    test_UWG()
