from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
import tempfile
import subprocess
import os
import shutil

router = APIRouter(prefix="/export", tags=["export"])

@router.post("/pdf")
async def export_pdf(request: Request):
    data = await request.json()
    latex_code = data.get("latex_code")
    if not latex_code:
        raise HTTPException(status_code=400, detail="Missing LaTeX code.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        pdf_path = os.path.join(tmpdir, "resume.pdf")
        with open(tex_path, "w") as f:
            f.write(latex_code)
        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-jobname=resume", tex_path],
                cwd=tmpdir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=20
            )
            print("Files in tempdir after pdflatex:", os.listdir(tmpdir))
            if not os.path.exists(pdf_path):
                raise Exception("PDF not generated. pdflatex output:\n" + result.stdout.decode() + "\n" + result.stderr.decode())
            # Read PDF into memory
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            return StreamingResponse(
                iter([pdf_bytes]),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=resume.pdf"}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LaTeX compilation failed: {e}")