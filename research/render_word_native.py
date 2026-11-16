"""Use installed Microsoft Word to export PDF, then the packaged DOCX renderer for PNG QA.

The bundled renderer has no LibreOffice backend on this Windows runtime.
Only its conversion hook is replaced; its page/DPI/raster pipeline is retained.
"""
from pathlib import Path
import importlib.util,sys,os
import win32com.client

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=Path('C:/Users/pc/.codex/plugins/cache/openai-primary-runtime/documents/26.1026.10807/skills/documents/render_docx.py')
os.environ['PATH']='C:/Users/pc/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin'+os.pathsep+os.environ['PATH']
spec=importlib.util.spec_from_file_location('packaged_docx_renderer',SCRIPT);renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)

def convert_with_word(doc_path,user_profile,convert_tmp_dir,stem,verbose=False):
    pdf=Path(convert_tmp_dir)/(stem+'.pdf')
    app=win32com.client.DispatchEx('Word.Application');app.Visible=False;app.DisplayAlerts=0
    document=None
    try:
        document=app.Documents.Open(str(Path(doc_path).resolve()),ConfirmConversions=False,ReadOnly=True,AddToRecentFiles=False,Visible=False)
        document.Repaginate();document.Fields.Update()
        document.ExportAsFixedFormat(str(pdf),17,OpenAfterExport=False)
    finally:
        if document is not None:document.Close(SaveChanges=0)
        app.Quit(SaveChanges=0)
    return str(pdf),'Native Microsoft Word PDF export used because bundled Windows runtime has no LibreOffice.'

renderer.convert_to_pdf=convert_with_word
if __name__=='__main__':renderer.main()
