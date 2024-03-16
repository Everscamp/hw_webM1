FROM python:3.12.0-alpine

WORKDIR /app

COPY . .

RUN pip install ./src

CMD run-helper

# I could have also just used entrypoint instead of installing a helper
# ENTRYPOINT [ "python", "./src/src/main.py" ]