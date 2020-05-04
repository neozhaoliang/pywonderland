import subprocess
from honeycomb import Honeycomb


POV_EXE = "povray"
POV_COMMAND = "cd povray && povray {}"


if __name__ == "__main__":
    """
    H = Honeycomb((3, 2, 2, 3, 2, 6), (0, 0, 0, -1))
    # I used maxcount=15000, cell_edges=10000 for the example image
    H.generate_povray_data(maxcount=50, cell_edges=1000,
                           eye=(0, 0, 0), lookat=(0, 0, 1))
    subprocess.check_call(POV_COMMAND.format("honeycomb-4-3-5.pov"), shell=True)
    """
    H = Honeycomb((3, 2, 2, 5, 2, 3), (-1, 0, 0, 0))
    # I used maxcount=130000 for the example image
    H.generate_povray_data(maxcount=13000)
    subprocess.check_call(POV_COMMAND.format("honeycomb-3-5-3.pov"), shell=True)
