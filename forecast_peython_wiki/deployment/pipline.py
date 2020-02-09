import kfp
import datetime
import os
import click
import logging


def pipeline(github_sha :str):
    """Returns the pipeline function with the github_sha used for the versioning of the containers and enviroment of the containers as well. 

    
    Keyword Arguments:
        env {str} -- The enviroment for which the pipeline is made for (default: {"develop"})
        github_sha {str} --The github sha used for the versioning
    """
    @kfp.dsl.pipeline(
        name="Example pipeline github action",
        description="This pipeline show how you can version the pipeline components using the githash"
    )
    def timeseries_pipeline(gcp_bucket: str, gcp_project: str, train_data :str="train.csv", forecast_date: str="forecast.csv"):
        """The kfp pipeline function. 
        
        Arguments:
            gcp_bucket {str} -- The google bucket
            project {str} -- The gcp project where the data should be stored
        
        Keyword Arguments:
            train_data {str} -- The name of the train file that is uploaded to the bucket (default: {"train.csv"})
            forecast_date {str} -- The name of the forecast file uploaded to the bucket (default: {"forecast.csv"})
        """
        pre_image = f"gcr.io/{project}/pre_image:{github_sha}"
        train_forecast_image = f"gcr.io/{project}/train_forecast_image:{github_sha}"

        operations['preprocess'] = dsl.ContainerOp(
            name='Preprocess',
            image=pre_image,
            command=['python3'],
            arguments=["main.py",
                    "--url", "https://raw.githubusercontent.com/facebook/prophet/master/examples/example_wp_log_peyton_manning.csv",
                    "--bucket", gcp_bucket,
                    "--destination_blob_name", train_data
            ]
        ).apply(use_secret(secret_name=secret_database_name, volume_name="mysecretvolume-one", secret_volume_mount_path=secret_volume_mount_path_sandtrade_database)) \
            .set_image_pull_policy('Always')

        operations['train_forecast'] = dsl.ContainerOp(
            name='Forecast',
            image=pre_image,
            command=['python3'],
            arguments=["main.py",
                    "--bucket", gcp_bucket,
                    "--source_blob_name", train_data,
                    "--forecast_blob_name", forecast_date
            ]
        ).apply(use_secret(secret_name=secret_database_name, volume_name="mysecretvolume-one", secret_volume_mount_path=secret_volume_mount_path_sandtrade_database)) \
            .set_image_pull_policy('Always')