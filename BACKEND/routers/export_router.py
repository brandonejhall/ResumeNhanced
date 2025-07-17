from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
import tempfile
import subprocess
import os

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
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_path],
                cwd=tmpdir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if not os.path.exists(pdf_path):
                raise Exception("PDF not generated")
            return FileResponse(pdf_path, media_type="application/pdf", filename="resume.pdf")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LaTeX compilation failed: {e}") 