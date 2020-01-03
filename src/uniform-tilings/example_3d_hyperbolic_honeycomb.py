from honeycomb import Honeycomb


if __name__ == "__main__":
    H = Honeycomb((3, 2, 2, 5, 2, 3), (-1, 0, 0, 0))
    # I used maxcount=130000 for the example image
    H.generate_povray_data(maxcount=10000, eye=(0, 0, 0.55))
