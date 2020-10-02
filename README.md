# covid19api

A simple Flask-based API server for COVID-19 data.

## Host Your Own Server

### Firebase and GCP setup

This server is aimed to be hosted on Google Firebase. For this, you'll need to create a [Firebase project](https://firebase.google.com/) and [enable billing](https://cloud.google.com/billing/docs/how-to/manage-billing-account) on the [Google Cloud Platform](https://console.cloud.google.com/).

### Repository setup

Once that is done, clone the repository using (replace `<username>` with the username of the user you're cloning from.):

    git clone https://github.com/<username>/covid19api.git

Once cloned, generate a new private key from the Firebase console and download the file to the repository. This file should be named `key.json`.

Also note the Web API Key of the project in the settings. Store this API key in the root of the repository in a file called `api.key`.

### Deploying to Firebase

Now you can deploy it to your GCP using the [gcloud CLI](https://cloud.google.com/sdk/docs/quickstarts).

To deploy, you can follow the instructions [here](https://cloud.google.com/community/tutorials/building-flask-api-with-cloud-firestore-and-deploying-to-cloud-run).

Alternatively, click on the 'Run on Google Cloud' button below after creating a Firebase project and enabling a billing account for it.

[![Run on Google Cloud](https://storage.googleapis.com/cloudrun/button.svg)](https://console.cloud.google.com/cloudshell/editor?shellonly=true&cloudshell_image=gcr.io/cloudrun/button&cloudshell_git_repo=https://github.com/patraanjan23/covid19api.git)


## How To Use

Once the server is up and running on Firebase, it is ready to be sent requests to. The responses shall be in JSON format.

Note the URL you see for the server on the Firebase console -- this is the URL you will send the requests to. We'll refer to this URL as the `base-url`. Replace `base-url` in the below URLs with the actual URL.

Update the server's data base using:

    <base-url>/update

Query all countries' data using:

    <base-url>/api/v1/current

Query a specific country's data using (replace `<string:country>` with the name of the country, for example: <base-url>/api/v1/current/india):

    <base-url>/api/v1/current/<string:country>

Update the server's time-series data:

    <base-url>/api/v1/timeseries/update

Query time-series data for a country (replace `<string:country>` with the name of the country, for example: <base-url>/api/v1/timeseries/india):

    <base-url>/api/v1/timeseries/<string:country>