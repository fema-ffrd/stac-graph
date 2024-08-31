from rashdf import RasPlanHdf

bucket_name = "kanawha-pilot"
s3_uri = f"s3://{bucket_name}/FFRD_Kanawha_Compute/sims/uncertainty_10_by_500_no_bootstrap_5_10a_2024/1/ras/ElkMiddle/ElkMiddle.p01.hdf"

ds = RasPlanHdf.open_uri(s3_uri)


def sanitize_reference_summary_output(ds):
    data = ds.reference_summary_output()
    results = {}
    for mesh in data["mesh_name"].unique():
        results[mesh] = {}

        for row in data.itertuples():
            results[mesh][row.refln_name] = {
                "max_flow_time": row.max_q_time.strftime("%Y-%m-%d %H:%M:%S"),
                "max_flow_value": round(row.max_q, 2),
                "max_wse_time": row.max_ws_time.strftime("%Y-%m-%d %H:%M:%S"),
                "max_wse_value": round(row.max_ws, 2),
            }
    return results


def sanitize_summary_results_data(ds):
    data = ds.get_results_unsteady_summary_attrs()
    del data["Computation Time DSS"]
    data["Computation Time Total (minutes)"] = round(data["Computation Time Total"].total_seconds() / 60, 2)
    del data["Computation Time Total"]
    data["Run Time Window"] = [
        data["Run Time Window"][0].strftime("%Y-%m-%d %H:%M:%S"),
        data["Run Time Window"][1].strftime("%Y-%m-%d %H:%M:%S"),
    ]
    return data


def get_vol_error(ds):
    for mesh_name in ds.mesh_area_names():
        # TODO: (Fix) this assumes the mesh has a single area and will overwrite results if there are more than 1....
        sum_vol_error = ds.get_attrs(f"/Results/Unsteady/Summary/Volume Accounting/Volume Accounting 2D/{mesh_name}")
        sum_vol_error = {k: round(v, 2) for k, v in sum_vol_error.items()}
    return sum_vol_error


sum_output = sanitize_reference_summary_output(ds)
# sum_results = sanitize_summary_results_data(ds)
# vol_error = get_vol_error(ds)
