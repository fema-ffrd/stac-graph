import pandas as pd


def combine_datasets(datasets, data_name):
    df_list = [pd.read_parquet(file) for file in datasets]
    df = pd.concat(df_list, ignore_index=True)
    df.to_parquet(f"{data_name}-Kanawha-0505.pq")


def main():
    storm_datasets = [f"storms-Kanawha-0505-R00{r}.parquet" for r in range(1, 6)]
    combine_datasets(storm_datasets, "storms")

    gage_datasets = [f"gages-Kanawha-0505-R00{r}.parquet" for r in range(1, 6)]
    combine_datasets(gage_datasets, "gages")

    computation_datasets = [f"computation-Kanawha-0505-R00{r}.parquet" for r in range(1, 6)]
    combine_datasets(computation_datasets, "computation")


if __name__ == "__main__":
    main()
