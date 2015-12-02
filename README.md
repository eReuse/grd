# GRD
The Global Record of Devices (GRD) is a log of information and traceability for any electronic device, worldwide.

It collects from each device, at least, the geographical locations where it has been donated/recycled and aggregated metadata. The system provides a REST-API to allow IT Asset Management Systems, as DeviceHub, report device lifecycle, environmental responsabilities for organizations, etc.

![Screenshot GRD device list][image_device_list]

## Requirements
* Python (3.4)
* Django (1.8)
* Postgres
For more details see [requirements] file.

## Installation
- Prepare Python 3 environment
    ```sudo apt-get install python3 python3-pip```

- Install PostgreSQL database
    ```sudo apt-get install postgresql postgresql-client python3-psycopg2```

- Create and configure database
    ```
    sudo su - postgres
    psql -c "CREATE USER ereuse PASSWORD 'ereuse';"
    psql -c "CREATE DATABASE ereuse OWNER ereuse;"
    ```

- Get latest source and install pip requirements.
    ```
    virtualenv -p python3 grdenv
    . grdenv/bin/activate
    pip install -r https://github.com/eReuse/grd/raw/master/grd/requirements.txt
    pip install git+https://github.com/ereuse/grd.git#egg=grd
    ```

- Create a new Django project.
    ```django-admin startproject ereuse_grd```

- Update database configuration.

<!-- TODO complete steps -->

## Upgrading
<!--- TODO: generalize and move fabfile to this repo. -->
If you want to automatize the process get some inspiration of this [fabfile].
    ```fab deploy:host=user@example.org```


[requirements]: grd/requirements.txt
[fabfile]: https://github.com/eReuse/grd-sandbox/blob/master/deploy_tools/fabfile.py
[image_device_list]: docs/screenshot_device_list.png
