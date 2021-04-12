FROM registry.bnac.net/fix

RUN apt update ; apt install -y python3 python3-pip

ADD main.py /opt/fmri_pipeline/main.py
ADD LICENSE /opt/fmri_pipeline/LICENSE
ADD preprocessing /opt/fmri_pipeline/preprocessing
ADD collect_raw_data /opt/fmri_pipeline/collect_raw_data
ADD connectome_analyses /opt/fmri_pipeline/connectome_analyses
ADD README.md /opt/fmri_pipeline/README.md
ADD requirements.txt /opt/fmri_pipeline/requirements.txt

COPY /usr/bin/ANTS /usr/bin/ANTS

ENV PATH="/opt/fmri_pipeline:${PATH}"

RUN pip3 install wheel
RUN pip3 install -r /opt/fmri_pipeline/requirements.txt
