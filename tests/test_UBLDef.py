import pytest
import UWG
import os
import math
import pprint
import decimal

dd = lambda x: decimal.Decimal.from_float(x)

class TestUBLDef(object):

    DIR_UP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    DIR_EPW_PATH = os.path.join(DIR_UP_PATH,"resources/epw")
    DIR_MATLAB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "matlab_ref","matlab_ubl")
    CALCULATE_TOLERANCE = lambda s,x,p: 1*10**-(p - 1 - int(math.log10(x))) if abs(float(x)) > 1e-15 else 1e-15

    def setup_uwg_integration(self):
        """ set up uwg object from initialize.uwg """

        epw_dir = self.DIR_EPW_PATH
        epw_file_name = "SGP_Singapore.486980_IWEC.epw"
        uwg_param_dir = os.path.join(self.DIR_UP_PATH,"resources")
        uwg_param_file_name = "initialize.uwg"

        self.uwg = UWG.UWG(epw_dir, epw_file_name, uwg_param_dir, uwg_param_file_name)

    def setup_open_matlab_ref(self,matlab_ref_file_path):
        """ open the matlab reference file """

        matlab_path = os.path.join(self.DIR_MATLAB_PATH,matlab_ref_file_path)
        if not os.path.exists(matlab_path):
            raise Exception("Failed to open {}!".format(matlab_path))
        matlab_file = open(matlab_path,'r')
        uwg_matlab_val_ = [float(x) for x in matlab_file.readlines()]
        matlab_file.close()
        return uwg_matlab_val_

    def test_ubl_init(self):
        """ test ubl constructor """

        self.setup_uwg_integration()
        self.uwg.read_epw()
        self.uwg.read_input()
        self.uwg.set_input()

        # Get uwg_python values
        uwg_python_val = [
            self.uwg.UBL.charLength,          # characteristic length of the urban area (m)
            self.uwg.UBL.perimeter,
            self.uwg.UBL.urbArea,             # horizontal urban area (m2)
            self.uwg.UBL.orthLength,          # length of the side of the urban area orthogonal to wind dir (m)
            self.uwg.UBL.paralLength,         # length of the side of the urban area parallel to wind dir (m)
            self.uwg.UBL.ublTemp,             # urban boundary layer temperature (K)
            reduce(lambda x,y:x+y, self.uwg.UBL.ublTempdx), # urban boundary layer temperature discretization (K)
            self.uwg.UBL.dayBLHeight,         # daytime mixing height, orig = 700
            self.uwg.UBL.nightBLHeight        # Sing: 80, Bub-Cap: 50, nighttime boundary-layer height (m); orig 80
        ]

        uwg_matlab_val = self.setup_open_matlab_ref("matlab_ref_ubl_init.txt")

        # matlab ref checking
        assert len(uwg_matlab_val) == len(uwg_python_val), "matlab={}, python={}".format(len(uwg_matlab_val), len(uwg_python_val))

        for i in xrange(len(uwg_matlab_val)):
            #print uwg_python_val[i], uwg_matlab_val[i]
            tol = self.CALCULATE_TOLERANCE(uwg_python_val[i],15.0)
            assert uwg_python_val[i] == pytest.approx(uwg_matlab_val[i], tol), "error at index={}".format(i)

    def test_ublmodel(self):
        """ test ubl constructor """

        self.setup_uwg_integration()
        self.uwg.read_epw()
        self.uwg.read_input()

        # Test Jan 1 (winter, no vegetation coverage)
        self.uwg.Month = 1
        self.uwg.Day = 1
        self.uwg.nDay = 1

        # set_input
        self.uwg.set_input()


        # In order to avoid integration effects. Test only first time step
        # Subtract timestep to stop at 300 sec
        self.uwg.simTime.nt -= (23*12 + 11)

        # Run simulation
        self.uwg.hvac_autosize()
        self.uwg.uwg_main()

        # check date
        #print self.uwg.simTime
        assert self.uwg.simTime.month == 1
        assert self.uwg.simTime.day == 1
        assert self.uwg.simTime.secDay == pytest.approx(300.0,abs=1e-15)

        # Get uwg_python values
        uwg_python_val = [
            self.uwg.UBL.ublTemp,               # urban boundary layer temperature (K)
            reduce(lambda x,y:x+y,self.uwg.UBL.ublTempdx), # urban boundary layer temperature discretaization (K)
            self.uwg.UBL.dayBLHeight,         # night boundary layer height (m)
            self.uwg.UBL.nightBLHeight         # night boundary layer height (m)
        ]

        uwg_matlab_val = self.setup_open_matlab_ref("matlab_ref_ublmodel.txt")

        # matlab ref checking
        assert len(uwg_matlab_val) == len(uwg_python_val)

        for i in xrange(len(uwg_matlab_val)):
            #print uwg_python_val[i], uwg_matlab_val[i]
            tol = self.CALCULATE_TOLERANCE(uwg_python_val[i],15.0)
            assert uwg_python_val[i] == pytest.approx(uwg_matlab_val[i], tol), "error at index={}".format(i)


if __name__ == "__main__":
    ubl = TestUBLDef()
    ubl.test_ubl_init()
    ubl.test_ublmodel()
