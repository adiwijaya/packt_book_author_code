resource "google_storage_bucket" "new-gcs-bucket" {
  name          = "packt-data-eng-on-gcp-data-bucket-new"
  location      = "US"
}