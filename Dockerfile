FROM continuumio/miniconda3:latest

WORKDIR /code
COPY finbert/ finbert/

RUN wget --quiet https://prosus-public.s3-eu-west-1.amazonaws.com/finbert/finbert-sentiment/pytorch_model.bin -O finbert/models/sentiment/base/pytorch_model.bin

COPY environment.yml environment.yml
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "finbert", "/bin/bash", "-c"]
RUN python -m nltk.downloader punkt

EXPOSE 8050
EXPOSE 8051

COPY . .

ENTRYPOINT ["bash", "run.sh"]
