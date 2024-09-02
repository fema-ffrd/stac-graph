# import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from components.layout import configure_page_settings
from components.tables import stylized_table


def app():
    configure_page_settings("Gage Viewer")

    st.markdown("## Weibull Plotter for Gage Results")

    df = st.gages

    col1, col2 = st.columns(2)

    with col1:
        gage_id = st.selectbox("Search for results by Gage", ["None", *df["gage"].unique()])

        variable = st.selectbox("Select Water Surface Elevation or Flow", ["Flow", "WSE"])

        if variable == "Flow":
            value, time, plot_label = "max_flow_value", "max_flow_time", "Flow (cfs)"
        else:
            value, time, plot_label = "max_wse_value", "max_wse_time", "Water Surface Elevation(ft)"

        if gage_id != "None":
            df = df[df["gage"].str.contains(gage_id, case=False, na=False)]
            df["rank"] = df[value].rank(ascending=False)
            # stylized_table(df[["ID", value, "rank", time, "Link"]].sort_values(by="rank", ascending=True))
            stylized_table(df[["ID", value, "rank", "Link"]].sort_values(by="rank", ascending=True))

    with col2:
        realization_colors = {1: "red", 2: "blue", 3: "green", 4: "orange", 5: "purple"}
        fig = go.Figure()

        if gage_id != "None":
            for realization in df["realization"].unique():
                realization_df = df[df["realization"] == realization]
                realization_df = realization_df.sort_values(by=value, ascending=False)
                realization_df["weibull_position"] = realization_df["rank"] / (len(realization_df) + 1)

                fig.add_trace(
                    go.Scatter(
                        x=realization_df["weibull_position"],
                        y=realization_df[value],
                        mode="markers",
                        name=f"Realization {realization}",
                        marker=dict(color=realization_colors.get(realization, "black")),
                        hovertext=realization_df["ID"],
                    )
                )

            fig.update_layout(
                title="Weibull Plot", xaxis_title=f"{gage_id}", yaxis_title=plot_label, xaxis=dict(autorange="reversed")
            )

            # 1% chance event
            fig.add_shape(
                type="line",
                x0=0.01,
                y0=df[value].min(),
                x1=0.01,
                y1=df[value].max(),
                line=dict(color="Red", width=2, dash="dashdot"),
            )
            fig.add_annotation(x=0.01, y=df[value].max(), text="1% Chance Event", showarrow=True, arrowhead=1)

            # # 50% chance event
            # fig.add_shape(
            #     type="line",
            #     x0=0.5,
            #     y0=df[value].min(),
            #     x1=0.5,
            #     y1=df[value].max(),
            #     line=dict(color="Red", width=2, dash="dashdot"),
            # )
            # fig.add_annotation(x=0.5, y=df[value].max(), text="50% Chance Event", showarrow=True, arrowhead=1)

            st.plotly_chart(fig)


if __name__ == "__main__":
    app()
