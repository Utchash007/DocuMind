from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

import uvicorn
from fastapi import UploadFile

from app import main
from tests.fixtures import isolated_backend, make_pdf


def run():
    with TemporaryDirectory(prefix="notemind-e2e-") as directory:
        with isolated_backend(Path(directory)):
            for filename, pages in {
                "Reference research.pdf": [
                    "Qubits use superposition to represent quantum states.",
                    "Error correction protects quantum information.",
                ],
                "Lab notes.pdf": ["Quantum experiments require careful calibration."],
            }.items():
                with BytesIO(make_pdf(pages)) as pdf:
                    main.upload_file(UploadFile(filename=filename, file=pdf))
            uvicorn.run(main.app, host="127.0.0.1", port=8011, log_level="warning")


if __name__ == "__main__":
    run()
