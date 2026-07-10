# Can run the following commands from root directory of project (Windows)
#   1. create docker image: docker build --tag build_fluidicity_jdglazer:0.0.1 .
#   2. create and run docker container from image docker: docker run -dt --name bfj_container build_fluidicity_jdglazer:0.0.1
#                         or if container exists already: docker start bfj_container
#   3. copy project to container: docker cp . bfj_container:/tmp
#   4. run terminal on container: docker exec -it bfj_container /bin/bash
#   5. run code on container: cd /tmp && \
#                             PYTHONPATH=/tmp/src pytest --cov=build_fluidicity_jdglazer --cov-report=html && \
#                             python -m build --no-isolation
#   6. copy dist folder to local machine: docker cp bfj_container:/tmp/dist .
FROM python:3.10

RUN apt-get update && \
    apt-get install -y  --reinstall --no-install-recommends \
    python3-hatchling

RUN pip install build hatchling pytest pytest-cov

WORKDIR /build-fluidicity

ENTRYPOINT ["/bin/bash"]