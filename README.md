<div align="center">

<h1>SSE Demo</h1>
&nbsp;

</div>

## Preface

A simple web application to demonstrate real-time unidirectional communication with
Server-Sent Events (SSEs). The associated blog post can be found [here][sse-blog].

## Installation

* Clone the repo.
* Go to the root directory and create a Python venv.
* Install the dependencies:
    ```sh
    pip install -r requirements.txt -r requirements-dev.txt
    ```

## Exploration

* Activate the virtual environment.
* Head over to the `sse` directory and start the webserver:
    ```sh
    uvicorn views:app --port 5000 --reload
    ```
* On another console, start the celery workers:
    ```sh
    celery -A views.celery_app worker -l info -Q default -c 1
    ```
* On your browser, go to [http://localhost:5000/index][local-server]. This will trigger
a background task that will take 5 seconds to complete. Upon completion, the backend
will communicate with the client in real-time and stream the task status:

    <video
        src="https://user-images.githubusercontent.com/30027932/229604497-0a0b058f-32dd-4219-a68f-9cd35b250334.mov"
        controls="controls"
        style="max-width: 730px;">
    </video>

<div align="center">
<i> ✨ 🍰 ✨ </i>
</div>

[sse-blog]: http://localhost:5000/index
[local-server]: http://localhost:5000/index
