# Build the Docker image

(Preliminary note: First, make sure that your `qualitycheck_config.toml` is up to date.)

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
