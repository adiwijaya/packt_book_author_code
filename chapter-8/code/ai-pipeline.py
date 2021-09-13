import kfp
from kfp.v2 import compiler
from kfp.v2.google.client import AIPlatformClient
from google.cloud import aiplatform
from google_cloud_pipeline_components import aiplatform as gcc_aip

from typing import NamedTuple

from kfp import dsl
from kfp.v2 import compiler
from kfp.v2.dsl import component
from kfp.v2.google.client import AIPlatformClient

project_id = "aw-general-dev"
region = "us-central1"
pipeline_root_path = "gs://aw-general-dev/aipipeline-root/hello-world"


@component(output_component_file="hw.yaml", base_image="python:3.9")
def hello_world(text: str) -> str:
    print(text)
    return text

@component(packages_to_install=["google-cloud-storage"])
def two_outputs(
    text: str,
) -> NamedTuple(
    "Outputs",
    [
        ("output_one", str),  # Return parameters
        ("output_two", str),
    ],
):
    # the import is not actually used for this simple example, but the import
    # is successful, as it was included in the `packages_to_install` list.
    from google.cloud import storage  # noqa: F401

    o1 = f"output one from text: {text}"
    o2 = f"output two from text: {text}"
    print("output one: {}; output_two: {}".format(o1, o2))
    return (o1, o2)


@component
def consumer(text1: str, text2: str, text3: str):
    print(f"text1: {text1}; text2: {text2}; text3: {text3}")

@kfp.dsl.pipeline(
    name="hello-world-v2",
    description="A simple intro pipeline",
    pipeline_root=pipeline_root_path,
)
def pipeline(text: str = "hi there"):
    hw_task = hello_world(text)
    two_outputs_task = two_outputs(text)
    consumer_task = consumer(  
        hw_task.output,
        two_outputs_task.outputs["output_one"],
        two_outputs_task.outputs["output_two"],
    )

# @kfp.dsl.pipeline(
#     name="automl-image-training-v2",
#     pipeline_root=pipeline_root_path)
# def pipeline(project_id: str):
#     ds_op = gcc_aip.ImageDatasetCreateOp(
#         project=project_id,
#         display_name="flowers",
#         gcs_source="gs://cloud-samples-data/vision/automl_classification/flowers/all_data_v2.csv",
#         import_schema_uri=aiplatform.schema.dataset.ioformat.image.single_label_classification,
#     )

#     training_job_run_op = gcc_aip.AutoMLImageTrainingJobRunOp(
#         project=project_id,
#         display_name="train-iris-automl-mbsdk-1",
#         prediction_type="classification",
#         model_type="CLOUD",
#         base_model=None,
#         dataset=ds_op.outputs["dataset"],
#         model_display_name="iris-classification-model-mbsdk",
#         training_fraction_split=0.6,
#         validation_fraction_split=0.2,
#         test_fraction_split=0.2,
#         budget_milli_node_hours=8000,
#     )

#     endpoint_op = gcc_aip.ModelDeployOp(
#         project=project_id, model=training_job_run_op.outputs["model"]
#     )


# compiler.Compiler().compile(pipeline_func=pipeline,
#         package_path='image_classif_pipeline.json')

compiler.Compiler().compile(
    pipeline_func=pipeline, package_path="intro_pipeline.json".replace(" ", "_")
)

# api_client = AIPlatformClient(project_id=project_id, region=region)

# response = api_client.create_run_from_job_spec(
#     'intro_pipeline.json',
#     pipeline_root=pipeline_root_path,
#     parameter_values={
#         'project_id': project_id
#     })

api_client = AIPlatformClient(project_id=project_id, region=region)

response = api_client.create_run_from_job_spec(
    job_spec_path="intro_pipeline.json".replace(" ", "_"), pipeline_root=pipeline_root_path
)