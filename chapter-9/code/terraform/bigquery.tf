# Enable BigQuery service
resource "google_project_service" "bigquery_service" {
  project = var.project_id
  service = "bigquery.googleapis.com"
}

# Create the BigQuery datasets
resource "google_bigquery_dataset" "dataset" {
  depends_on = [
    google_project_service.bigquery_service
  ]

  project    = var.project_id
  dataset_id = "new_dataset"
}
