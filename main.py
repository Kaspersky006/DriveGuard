from src.driveguard.reader import read_telemetry


def main():
    dataframe = read_telemetry("data/raw/sample_telemetry.csv")

    print(dataframe)


if __name__ == "__main__":
    main()
