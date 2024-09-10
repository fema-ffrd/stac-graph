# stac-graph
Experimental repo for using stac items in graphs for linked compute. Create stac catalogs probabilistic realizations, collect data from the stac catalog, and review results.

---
To load secrets as environment variables, please make a copy of the example.toml file, rename it secrets.toml, and place it within the .streamlit folder, located within the client_sandbox. Secrets within the .toml file need to be wrapped within double quotes (e.g., STREAMLIT_SERVER_RUN_ON_SAVE="true"). This method of loading secrets is preferred for streamlit apps since it is compatible for both local development and cloud deployment. The only difference for cloud deployment is needing to sign into the Streamlit webpage, navigate to your app, and then add the same secrets from there.

---
STAC Items
![](docs/item.png)

---

Review SST Data 
![](docs/gages.png)


---

Review Gage Results
![](docs/storms.png)
