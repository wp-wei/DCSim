# Reproducible headless environment for OpenModelica + OMPython + Buildings.
FROM openmodelica/openmodelica:v1.26.3-ompython

# Install Buildings in a deterministic path used by run.py defaults.
ADD https://github.com/lbl-srg/modelica-buildings/archive/refs/tags/v11.1.0.tar.gz /tmp/buildings.tar.gz
RUN set -eux; \
    tar -xzf /tmp/buildings.tar.gz -C /opt; \
    mv /opt/modelica-buildings-11.1.0 /opt/Buildings; \
    rm -f /tmp/buildings.tar.gz

ENV BUILDINGS_PATH=/opt/Buildings
WORKDIR /workspace

CMD ["bash"]
