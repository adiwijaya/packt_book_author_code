resource "google_service_account" "bq-service_account" {
  account_id   = "sa-bigquery"
  display_name = "Service Account for accessing BigQuery"
}