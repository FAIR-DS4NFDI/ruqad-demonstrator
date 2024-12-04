# Build the Docker image #

## Build configuration ##

- Make sure that your `qualitycheck_config.toml` is up to date.
- Update `pylinkahead.ini` if necessary.

## Actual building ##

Building the Docker image from within this `docker/` directory:

```sh
docker build -t ruqad:dev -f Dockerfile ..
```

# Runtime configuration #

Open `../secrets.example.sh` and save it as `secrets.sh`, then fill in all the required
configuration.

# Run the image #

You can start Docker with

`docker run --env-file=../secrets.sh ruqad:dev`

## Add data ##

1. Log into the configured Kadi instance.
2. Create new record with the access token's user, then attach a file.
3. When the monitor finds the file, it should [trigger the pipeline](https://gitlab.indiscale.com/caosdb/customers/f-fit/demonstrator4.2-example-data/-/pipelines/) for the quality check.
4. After the quality check has completed, the crawler should create a LinkAhead record and insert it
   into the specified LinkAhead instance.
