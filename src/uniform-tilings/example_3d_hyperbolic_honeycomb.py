from honeycomb import Honeycomb


if __name__ == "__main__":
    H = Honeycomb((3, 2, 2, 5, 2, 3), (-1, 0, 0, 0))
    H.generate_povray_data(maxcount=10000)
