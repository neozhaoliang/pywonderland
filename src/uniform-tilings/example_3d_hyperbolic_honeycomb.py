from honeycomb import Honeycomb


if __name__ == "__main__":
    H = Honeycomb((4, 2, 2, 3, 2, 5), (-1, -1, 0, 0))
    H.generate_povray_data(maxcount=80000)
